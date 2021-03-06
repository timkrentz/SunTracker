package require vtk
package require vtkinteraction

# Demonstrate how to use the vtkAffineWidget to apply affine transforms
# ( translate, scale, rotate, shear ) to an actor.

# Start by reading in data
#
vtkVolume16Reader v16
  v16 SetDataDimensions 64 64
  v16 SetDataByteOrderToLittleEndian
  v16 SetImageRange 1 93
  v16 SetDataSpacing 3.2 3.2 1.5
  v16 SetFilePrefix "$VTK_DATA_ROOT/Data/headsq/quarter"
  v16 ReleaseDataFlagOn
  v16 SetDataMask 0x7fff
  v16 Update

  set range [[v16 GetOutput] GetScalarRange]

# vtkImageActor requires unsigned char or unsigned short data, so
# we will transform the data with a linear shift/scale filter.
#
vtkImageShiftScale shifter
  shifter SetShift [ expr -1.0*[lindex $range 0] ]
  shifter SetScale [ expr 255.0 /( [lindex $range 1] - [lindex $range 0] ) ]
  shifter SetOutputScalarTypeToUnsignedChar
  shifter SetInputConnection [ v16 GetOutputPort ]
  shifter ReleaseDataFlagOff
  shifter Update

# An actor to display one slice of 3D image data.
#
vtkImageActor imageActor
  [imageActor GetMapper] SetInputConnection [shifter GetOutputPort]
  imageActor VisibilityOn
  imageActor SetDisplayExtent 0 63 0 63 46 46
  imageActor InterpolateOn

scan [ imageActor GetBounds ] "%f %f %f %f %f %f" \
        xMin xMax yMin yMax zMin zMax

#  Create a renderer and a render window,
#
vtkRenderer ren1
vtkRenderWindow renWin
  renWin AddRenderer ren1

# Create an interactor to respond to mouse events.
#
vtkRenderWindowInteractor iren
  iren SetRenderWindow renWin

# Create an interactor style that works specifically with images:
# middle button: pan image
# right button: zoom image
# left button + ctrl key: rotate image
#
vtkInteractorStyleImage style
  iren SetInteractorStyle style

# VTK widgets consist of two parts: the widget part that handles event processing;
# and the widget representation that defines how the widget appears in the scene
# (i.e., matters pertaining to geometry).  The affine 2D representation consists
# of a set of axes inside a circle set inside a box.  Clicking on an edge or
# a corner of the box will set the scaling.  Clicking the the axes will set
# the translation.  Clicking on the circle and dragging along its circumference
# sets the rotation.  Clicking on an edge while depressing the ctrl key will
# set the shear (currently not fully implemented).
#
vtkAffineRepresentation2D rep
  rep SetBoxWidth 100
  rep SetCircleWidth 75
  rep SetAxesWidth 60
  rep DisplayTextOn
  rep PlaceWidget $xMin $xMax $yMin $yMax $zMin $zMax

vtkAffineWidget widget
  widget SetInteractor iren
  widget SetRepresentation rep

# Add an observer to apply the affine transform to the image actor at
# the end of interaction with the widget.
#
  widget AddObserver EndInteractionEvent WidgetCallback

# Transorm generated by the affine widget's representation that
# will transform the image actor.
#
  vtkTransform transform

#  Add the actor to the renderer, set the background and size.
#
  ren1 AddActor imageActor
  ren1 SetBackground 0.1 0.2 0.4
  renWin SetSize 600 600

# Render the image.
#
iren AddObserver UserEvent {wm deiconify .vtkInteract}
iren Initialize

# Prevent the tk window from showing up then start the event loop
wm withdraw .

proc WidgetCallback  { } {
  rep GetTransform transform
  imageActor SetUserTransform transform
}

iren Start