# -*- test-case-name: twisted.web.test.test_flatten -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Context-free flattener/serializer for rendering Python objects, possibly
complex or arbitrarily nested, as strings.
"""

from cStringIO import StringIO
from sys import exc_info
from types import GeneratorType
from traceback import extract_tb
from twisted.internet.defer import Deferred
from twisted.web.error import UnfilledSlot, UnsupportedType, FlattenerError

from twisted.web.iweb import IRenderable
from twisted.web._stan import (
    Tag, slot, voidElements, Comment, CDATA, CharRef)



def escapeForContent(data):
    """
    Escape some character or UTF-8 byte data for inclusion in an HTML or XML
    document, by replacing metacharacters (C{&<>}) with their entity
    equivalents (C{&amp;&lt;&gt;}).

    This is used as an input to L{_flattenElement}'s C{dataEscaper} parameter.

    @type data: C{bytes} or C{unicode}
    @param data: The string to escape.

    @rtype: C{bytes}
    @return: The quoted form of C{data}.  If C{data} is unicode, return a utf-8
        encoded string.
    """
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    data = data.replace('&', '&amp;'
        ).replace('<', '&lt;'
        ).replace('>', '&gt;')
    return data



def attributeEscapingDoneOutside(data):
    """
    Escape some character or UTF-8 byte data for inclusion in the top level of
    an attribute.  L{attributeEscapingDoneOutside} actually passes the data
    through unchanged, because L{flattenWithAttributeEscaping} handles the
    quoting of the text within attributes outside the generator returned by
    L{_flattenElement}; this is used as the C{dataEscaper} argument to that
    L{_flattenElement} call so that that generator does not redundantly escape
    its text output.

    @type data: C{bytes} or C{unicode}
    @param data: The string to escape.

    @return: The string, unchanged, except for encoding.
    @rtype: C{bytes}
    """
    if isinstance(data, unicode):
        return data.encode("utf-8")
    return data



def flattenWithAttributeEscaping(root):
    """
    Decorate the generator returned by L{_flattenElement} so that its output is
    properly quoted for inclusion within an XML attribute value.

    If a L{Tag <twisted.web.template.Tag>} C{x} is flattened within the context
    of the contents of another L{Tag <twisted.web.template.Tag>} C{y}, the
    metacharacters (C{<>&"}) delimiting C{x} should be passed through
    unchanged, but the textual content of C{x} should still be quoted, as
    usual.  For example: C{<y><x>&amp;</x></y>}.  That is the default behavior
    of L{_flattenElement} when L{escapeForContent} is passed as the
    C{dataEscaper}.

    However, when a L{Tag <twisted.web.template.Tag>} C{x} is flattened within
    the context of an I{attribute} of another L{Tag <twisted.web.template.Tag>}
    C{y}, then the metacharacters delimiting C{x} should be quoted so that it
    can be parsed from the attribute's value.  In the DOM itself, this is not a
    valid thing to do, but given that renderers and slots may be freely moved
    around in a L{twisted.web.template} template, it is a condition which may
    arise in a document and must be handled in a way which produces valid
    output.  So, for example, you should be able to get C{<y attr="&lt;x /&gt;"
    />}.  This should also be true for other XML/HTML meta-constructs such as
    comments and CDATA, so if you were to serialize a L{comment
    <twisted.web.template.Comment>} in an attribute you should get C{<y
    attr="&lt;-- comment --&gt;" />}.  Therefore in order to capture these
    meta-characters, the attribute generator from L{_flattenElement} context is
    wrapped with an L{flattenWithAttributeEscaping}.

    Because I{all} characters serialized in the context of an attribute are
    quoted before they are yielded by the generator returned by
    L{flattenWithAttributeEscaping}, on the "outside" of the L{_flattenElement}
    call, the L{_flattenElement} generator therefore no longer needs to quote
    text that appears directly within the attribute itself.

    The final case, and hopefully the much more common one as compared to
    serializing L{Tag <twisted.web.template.Tag>} and arbitrary L{IRenderable}
    objects within an attribute, is to serialize a simple string, and those
    should be passed through for L{flattenWithAttributeEscaping} to quote
    without applying a second, redundant level of quoting.

    @param root: A value that may be yielded by L{_flattenElement}; either an
        iterable yielding L{bytes} (or more iterables), or bytes itself.
    @type root: L{bytes} or C{iterable}

    @return: The same type as L{_flattenElement} returns, with all the bytes
        encoded for representation within an attribute.
    @rtype: the same type as the C{subFlatten} argument
    """
    if isinstance(root, bytes):
        root = escapeForContent(root)
        root = root.replace('"', '&quot;')
        yield root
    elif isinstance(root, Deferred):
        yield root.addCallback(flattenWithAttributeEscaping)
    else:
        for subroot in root:
            yield flattenWithAttributeEscaping(subroot)



def escapedCDATA(data):
    """
    Escape CDATA for inclusion in a document.

    @type data: C{str} or C{unicode}
    @param data: The string to escape.

    @rtype: C{str}
    @return: The quoted form of C{data}. If C{data} is unicode, return a utf-8
        encoded string.
    """
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    return data.replace(']]>', ']]]]><![CDATA[>')



def escapedComment(data):
    """
    Escape a comment for inclusion in a document.

    @type data: C{str} or C{unicode}
    @param data: The string to escape.

    @rtype: C{str}
    @return: The quoted form of C{data}. If C{data} is unicode, return a utf-8
        encoded string.
    """
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    data = data.replace('--', '- - ').replace('>', '&gt;')
    if data and data[-1] == '-':
        data += ' '
    return data



def _getSlotValue(name, slotData, default=None):
    """
    Find the value of the named slot in the given stack of slot data.
    """
    for slotFrame in slotData[::-1]:
        if slotFrame is not None and name in slotFrame:
            return slotFrame[name]
    else:
        if default is not None:
            return default
        raise UnfilledSlot(name)



def _flattenElement(request, root, slotData, renderFactory, dataEscaper):
    """
    Make C{root} slightly more flat by yielding all its immediate contents as
    strings, deferreds or generators that are recursive calls to itself.

    @param request: A request object which will be passed to
        L{IRenderable.render}.

    @param root: An object to be made flatter.  This may be of type C{unicode},
        C{str}, L{slot}, L{Tag <twisted.web.template.Tag>}, L{URL}, L{tuple},
        L{list}, L{GeneratorType}, L{Deferred}, or an object that implements
        L{IRenderable}.

    @param slotData: A C{list} of C{dict} mapping C{str} slot names to data
        with which those slots will be replaced.

    @param renderFactory: If not C{None}, an object that provides
        L{IRenderable}.

    @param dataEscaper: A 1-argument callable which takes L{bytes} or
        L{unicode} and returns L{bytes}, quoted as appropriate for the
        rendering context.  This is really only one of two values:
        L{attributeEscapingDoneOutside} or L{escapeForContent}, depending on
        whether the rendering context is within an attribute or not.  See the
        explanation in L{flattenWithAttributeEscaping}.

    @return: An iterator that eventually yields L{bytes} that should be written
        to the output.  However it may also yield other iterators or
        L{Deferred}s; if it yields another iterator, the caller will iterate
        it; if it yields a L{Deferred}, the result of that L{Deferred} will
        either be L{bytes}, in which case it's written, or another generator,
        in which case it is iterated.  See L{_flattenTree} for the trampoline
        that consumes said values.
    @rtype: An iterator which yields L{bytes}, L{Deferred}, and more iterators
        of the same type.
    """
    def keepGoing(newRoot, dataEscaper=dataEscaper,
                  renderFactory=renderFactory):
        return _flattenElement(request, newRoot, slotData, renderFactory,
                               dataEscaper)
    if isinstance(root, (bytes, unicode)):
        yield dataEscaper(root)
    elif isinstance(root, slot):
        slotValue = _getSlotValue(root.name, slotData, root.default)
        yield keepGoing(slotValue)
    elif isinstance(root, CDATA):
        yield '<![CDATA['
        yield escapedCDATA(root.data)
        yield ']]>'
    elif isinstance(root, Comment):
        yield '<!--'
        yield escapedComment(root.data)
        yield '-->'
    elif isinstance(root, Tag):
        slotData.append(root.slotData)
        if root.render is not None:
            rendererName = root.render
            rootClone = root.clone(False)
            rootClone.render = None
            renderMethod = renderFactory.lookupRenderMethod(rendererName)
            result = renderMethod(request, rootClone)
            yield keepGoing(result)
            slotData.pop()
            return

        if not root.tagName:
            yield keepGoing(root.children)
            return

        yield '<'
        if isinstance(root.tagName, unicode):
            tagName = root.tagName.encode('ascii')
        else:
            tagName = str(root.tagName)
        yield tagName
        for k, v in root.attributes.iteritems():
            if isinstance(k, unicode):
                k = k.encode('ascii')
            yield ' ' + k + '="'
            # Serialize the contents of the attribute, wrapping the results of
            # that serialization so that _everything_ is quoted.
            attribute = keepGoing(v, attributeEscapingDoneOutside)
            yield flattenWithAttributeEscaping(attribute)
            yield '"'
        if root.children or tagName not in voidElements:
            yield '>'
            # Regardless of whether we're in an attribute or not, switch back
            # to the escapeForContent dataEscaper.  The contents of a tag must
            # be quoted no matter what; in the top-level document, just so
            # they're valid, and if they're within an attribute, they have to
            # be quoted so that after applying the *un*-quoting required to re-
            # parse the tag within the attribute, all the quoting is still
            # correct.
            yield keepGoing(root.children, escapeForContent)
            yield '</' + tagName + '>'
        else:
            yield ' />'

    elif isinstance(root, (tuple, list, GeneratorType)):
        for element in root:
            yield keepGoing(element)
    elif isinstance(root, CharRef):
        yield '&#%d;' % (root.ordinal,)
    elif isinstance(root, Deferred):
        yield root.addCallback(lambda result: (result, keepGoing(result)))
    elif IRenderable.providedBy(root):
        result = root.render(request)
        yield keepGoing(result, renderFactory=root)
    else:
        raise UnsupportedType(root)



def _flattenTree(request, root):
    """
    Make C{root} into an iterable of L{bytes} and L{Deferred} by doing a depth
    first traversal of the tree.

    @param request: A request object which will be passed to
        L{IRenderable.render}.

    @param root: An object to be made flatter.  This may be of type C{unicode},
        L{bytes}, L{slot}, L{Tag <twisted.web.template.Tag>}, L{tuple},
        L{list}, L{GeneratorType}, L{Deferred}, or something providing
        L{IRenderable}.

    @return: An iterator which yields objects of type L{bytes} and L{Deferred}.
        A L{Deferred} is only yielded when one is encountered in the process of
        flattening C{root}.  The returned iterator must not be iterated again
        until the L{Deferred} is called back.
    """
    stack = [_flattenElement(request, root, [], None, escapeForContent)]
    while stack:
        try:
            # In Python 2.5, after an exception, a generator's gi_frame is
            # None.
            frame = stack[-1].gi_frame
            element = stack[-1].next()
        except StopIteration:
            stack.pop()
        except Exception, e:
            stack.pop()
            roots = []
            for generator in stack:
                roots.append(generator.gi_frame.f_locals['root'])
            roots.append(frame.f_locals['root'])
            raise FlattenerError(e, roots, extract_tb(exc_info()[2]))
        else:
            if type(element) is str:
                yield element
            elif isinstance(element, Deferred):
                def cbx((original, toFlatten)):
                    stack.append(toFlatten)
                    return original
                yield element.addCallback(cbx)
            else:
                stack.append(element)


def _writeFlattenedData(state, write, result):
    """
    Take strings from an iterator and pass them to a writer function.

    @param state: An iterator of C{str} and L{Deferred}.  C{str} instances will
        be passed to C{write}.  L{Deferred} instances will be waited on before
        resuming iteration of C{state}.

    @param write: A callable which will be invoked with each C{str}
        produced by iterating C{state}.

    @param result: A L{Deferred} which will be called back when C{state} has
        been completely flattened into C{write} or which will be errbacked if
        an exception in a generator passed to C{state} or an errback from a
        L{Deferred} from state occurs.

    @return: C{None}
    """
    while True:
        try:
            element = state.next()
        except StopIteration:
            result.callback(None)
        except:
            result.errback()
        else:
            if type(element) is str:
                write(element)
                continue
            else:
                def cby(original):
                    _writeFlattenedData(state, write, result)
                    return original
                element.addCallbacks(cby, result.errback)
        break



def flatten(request, root, write):
    """
    Incrementally write out a string representation of C{root} using C{write}.

    In order to create a string representation, C{root} will be decomposed into
    simpler objects which will themselves be decomposed and so on until strings
    or objects which can easily be converted to strings are encountered.

    @param request: A request object which will be passed to the C{render}
        method of any L{IRenderable} provider which is encountered.

    @param root: An object to be made flatter.  This may be of type L{unicode},
        L{bytes}, L{slot}, L{Tag <twisted.web.template.Tag>}, L{tuple},
        L{list}, L{GeneratorType}, L{Deferred}, or something that provides
        L{IRenderable}.

    @param write: A callable which will be invoked with each L{bytes} produced
        by flattening C{root}.

    @return: A L{Deferred} which will be called back when C{root} has been
        completely flattened into C{write} or which will be errbacked if an
        unexpected exception occurs.
    """
    result = Deferred()
    state = _flattenTree(request, root)
    _writeFlattenedData(state, write, result)
    return result



def flattenString(request, root):
    """
    Collate a string representation of C{root} into a single string.

    This is basically gluing L{flatten} to a C{StringIO} and returning the
    results. See L{flatten} for the exact meanings of C{request} and
    C{root}.

    @return: A L{Deferred} which will be called back with a single string as
        its result when C{root} has been completely flattened into C{write} or
        which will be errbacked if an unexpected exception occurs.
    """
    io = StringIO()
    d = flatten(request, root, io.write)
    d.addCallback(lambda _: io.getvalue())
    return d
