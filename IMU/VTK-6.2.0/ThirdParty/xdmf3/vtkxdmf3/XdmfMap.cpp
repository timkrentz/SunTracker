/*****************************************************************************/
/*                                    XDMF                                   */
/*                       eXtensible Data Model and Format                    */
/*                                                                           */
/*  Id : XdmfMap.cpp                                                         */
/*                                                                           */
/*  Author:                                                                  */
/*     Kenneth Leiter                                                        */
/*     kenneth.leiter@arl.army.mil                                           */
/*     US Army Research Laboratory                                           */
/*     Aberdeen Proving Ground, MD                                           */
/*                                                                           */
/*     Copyright @ 2011 US Army Research Laboratory                          */
/*     All Rights Reserved                                                   */
/*     See Copyright.txt for details                                         */
/*                                                                           */
/*     This software is distributed WITHOUT ANY WARRANTY; without            */
/*     even the implied warranty of MERCHANTABILITY or FITNESS               */
/*     FOR A PARTICULAR PURPOSE.  See the above copyright notice             */
/*     for more information.                                                 */
/*                                                                           */
/*****************************************************************************/

#include <utility>
#include "XdmfAttribute.hpp"
#include "XdmfError.hpp"
#include "XdmfGridCollection.hpp"
#include "XdmfGridCollectionType.hpp"
#include "XdmfHeavyDataController.hpp"
#include "XdmfMap.hpp"

shared_ptr<XdmfMap>
XdmfMap::New()
{
  shared_ptr<XdmfMap> p(new XdmfMap());
  return p;
}

std::vector<shared_ptr<XdmfMap> >
XdmfMap::New(const std::vector<shared_ptr<XdmfAttribute> > & globalNodeIds)
{
  // globalNodeId | taskId | localNodeId at taskId
  std::map<node_id, std::map<task_id, node_id> > globalNodeIdMap;

  // fill globalNodeIdMap using globalNodeIds
  std::vector<bool> releaseGlobalNodeIds(globalNodeIds.size(), false);
  for(unsigned int i=0; i<globalNodeIds.size(); ++i) {
    const shared_ptr<XdmfAttribute> currGlobalNodeIds = globalNodeIds[i];
    if(!currGlobalNodeIds->isInitialized()) {
      currGlobalNodeIds->read();
      releaseGlobalNodeIds[i] = true;
    }
    for(unsigned int j=0; j<currGlobalNodeIds->getSize(); ++j) {
      const node_id currGlobalNodeId = currGlobalNodeIds->getValue<node_id>(j);
      globalNodeIdMap[currGlobalNodeId][i] = j;
    }
  }

  std::vector<shared_ptr<XdmfMap> > returnValue;
  returnValue.resize(globalNodeIds.size());

  // fill maps for each partition
  for(unsigned int i=0; i<globalNodeIds.size(); ++i)  {
    shared_ptr<XdmfMap> map = XdmfMap::New();
    returnValue[i] = map;
    const shared_ptr<XdmfAttribute> currGlobalNodeIds = globalNodeIds[i];

    for(unsigned int j=0; j<currGlobalNodeIds->getSize(); ++j) {
      const node_id currGlobalNodeId = currGlobalNodeIds->getValue<node_id>(j);
      const std::map<task_id, node_id> & currMap = 
        globalNodeIdMap[currGlobalNodeId];
      if(currMap.size() > 1) {
        for(std::map<task_id, node_id>::const_iterator iter = currMap.begin();
            iter != currMap.end();
            ++iter) {
          if(iter->first != (int)i) {
            map->insert(iter->first, j, iter->second);
          }
        }
      }
    }
    if(releaseGlobalNodeIds[i]) {
      currGlobalNodeIds->release();
    }
  }

  return returnValue;
}

XdmfMap::XdmfMap() :
  mName("")
{
}

XdmfMap::~XdmfMap()
{
}

const std::string XdmfMap::ItemTag = "Map";

std::map<std::string, std::string>
XdmfMap::getItemProperties() const
{
  std::map<std::string, std::string> mapProperties;
  mapProperties.insert(std::make_pair("Name", mName));
  return mapProperties;
}

std::string
XdmfMap::getItemTag() const
{
  return ItemTag;
}

std::map<XdmfMap::task_id, XdmfMap::node_id_map>
XdmfMap::getMap() const
{
  return mMap;
}

std::string
XdmfMap::getName() const
{
  return mName;
}

XdmfMap::node_id_map
XdmfMap::getRemoteNodeIds(const task_id remoteTaskId)
{
  std::map<task_id, node_id_map>::const_iterator iter =
    mMap.find(remoteTaskId);
  if(iter != mMap.end()) {
    return iter->second;
  }
  // No entry, return empty map.
  return node_id_map();
}

void
XdmfMap::insert(const task_id remoteTaskId,
                const node_id localNodeId,
                const node_id remoteLocalNodeId)
{
  mMap[remoteTaskId][localNodeId].insert(remoteLocalNodeId);
}

bool XdmfMap::isInitialized() const
{
  return mMap.size() > 0;
}

void
XdmfMap::populateItem(const std::map<std::string, std::string> & itemProperties,
                      const std::vector<shared_ptr<XdmfItem> > & childItems,
                      const XdmfCoreReader * const reader)
{
  XdmfItem::populateItem(itemProperties, childItems, reader);
  std::map<std::string, std::string>::const_iterator name =
    itemProperties.find("Name");
  if(name != itemProperties.end()) {
    mName = name->second;
  }
  else {
    mName = "";
  }
  std::vector<shared_ptr<XdmfArray> > arrayVector;
  arrayVector.reserve(3);
  for(std::vector<shared_ptr<XdmfItem> >::const_iterator iter =
        childItems.begin();
      iter != childItems.end();
      ++iter) {
    if(shared_ptr<XdmfArray> array = shared_dynamic_cast<XdmfArray>(*iter)) {
      arrayVector.push_back(array);
    }
  }

  if(arrayVector.size() != 0) {
    if(arrayVector.size() != 3) {
      XdmfError::message(XdmfError::FATAL,
                         "Expected 3 arrays attached to "
                         "XdmfMap::populateItem");
    }
    if(!(arrayVector[0]->getSize() == arrayVector[1]->getSize() &&
         arrayVector[0]->getSize() == arrayVector[2]->getSize())) {
      XdmfError::message(XdmfError::FATAL,
                         "Arrays must be of equal size in "
                         "XdmfMap:: populateItem");
    }

    // check if any arrays have values in memory - if so, they need to be
    // read into map
    bool needToRead = false;
    for(std::vector<shared_ptr<XdmfArray> >::const_iterator iter =
          arrayVector.begin();
        iter != arrayVector.end();
        ++iter) {
      if((*iter)->isInitialized()) {
        needToRead = true;
        break;
      }
    }

    if(needToRead) {
      for(std::vector<shared_ptr<XdmfArray> >::const_iterator iter =
            arrayVector.begin();
          iter != arrayVector.end();
          ++iter) {
        if(!(*iter)->isInitialized()) {
          (*iter)->read();
        }
      }
      for(unsigned int i=0; i<arrayVector[0]->getSize(); ++i) {
        this->insert(arrayVector[0]->getValue<task_id>(i),
                     arrayVector[1]->getValue<node_id>(i),
                     arrayVector[2]->getValue<node_id>(i));
      }
    }
    else {

      mRemoteTaskIdsControllers.clear();
      for (unsigned int i = 0; i <  arrayVector[0]->getNumberHeavyDataControllers(); ++i)
      {
        mRemoteTaskIdsControllers.push_back(arrayVector[0]->getHeavyDataController(i));
      }
      mLocalNodeIdsControllers.clear();
      for (unsigned int i = 0; i <  arrayVector[1]->getNumberHeavyDataControllers(); ++i)
      {
        mLocalNodeIdsControllers.push_back(arrayVector[1]->getHeavyDataController(i));
      }
      mRemoteLocalNodeIdsControllers.clear();
      for (unsigned int i = 0; i <  arrayVector[2]->getNumberHeavyDataControllers(); ++i)
      {
        mRemoteLocalNodeIdsControllers.push_back(arrayVector[2]->getHeavyDataController(i));
      }
    }
  }
}

void
XdmfMap::read()
{
  if(mLocalNodeIdsControllers.size() > 0 &&
     mRemoteTaskIdsControllers.size() > 0 &&
     mRemoteLocalNodeIdsControllers.size() > 0) {

    unsigned int localNodeCount = 0;
    for (unsigned int i = 0; i< mLocalNodeIdsControllers.size(); ++i)
    {
      localNodeCount += mLocalNodeIdsControllers[i]->getSize();
    }
    unsigned int remoteTaskCount = 0;
    for (unsigned int i = 0; i< mRemoteTaskIdsControllers.size(); ++i)
    {
      remoteTaskCount += mRemoteTaskIdsControllers[i]->getSize();
    }
    unsigned int remoteNodeCount = 0;
    for (unsigned int i = 0; i< mRemoteLocalNodeIdsControllers.size(); ++i)
    {
      remoteNodeCount += mRemoteLocalNodeIdsControllers[i]->getSize();
    }

    if(!(localNodeCount ==
         remoteTaskCount &&
         localNodeCount ==
         remoteNodeCount)){
      XdmfError::message(XdmfError::FATAL,
                         "Arrays must be of equal size in XdmfMap::read");
    }

    shared_ptr<XdmfArray> remoteTaskIds = XdmfArray::New();
    shared_ptr<XdmfArray> localNodeIds = XdmfArray::New();
    shared_ptr<XdmfArray> remoteLocalNodeIds = XdmfArray::New();

    mRemoteTaskIdsControllers[0]->read(remoteTaskIds.get());
    for (unsigned int i = 1; i < mRemoteTaskIdsControllers.size(); ++i)
    {
      shared_ptr<XdmfArray> tempArray = XdmfArray::New();
      mRemoteTaskIdsControllers[i]->read(tempArray.get());
      remoteTaskIds->insert(remoteTaskIds->getSize(), tempArray, 0, tempArray->getSize());
    }
    mLocalNodeIdsControllers[0]->read(localNodeIds.get());
    for (unsigned int i = 1; i < mLocalNodeIdsControllers.size(); ++i)
    {
      shared_ptr<XdmfArray> tempArray = XdmfArray::New();
      mLocalNodeIdsControllers[i]->read(tempArray.get());
      localNodeIds->insert(localNodeIds->getSize(), tempArray, 0, tempArray->getSize());
    }
    mRemoteLocalNodeIdsControllers[0]->read(remoteLocalNodeIds.get());
    for (unsigned int i = 1; i < mRemoteLocalNodeIdsControllers.size(); ++i)
    {
      shared_ptr<XdmfArray> tempArray = XdmfArray::New();
      mRemoteLocalNodeIdsControllers[i]->read(tempArray.get());
      remoteLocalNodeIds->insert(remoteLocalNodeIds->getSize(), tempArray, 0, tempArray->getSize());
    }

    for(unsigned int i=0; i<remoteTaskIds->getSize(); ++i) {
      const unsigned int remoteTaskId = remoteTaskIds->getValue<task_id>(i);
      const unsigned int localNodeId = localNodeIds->getValue<node_id>(i);
      const unsigned int remoteLocalNodeId =
        remoteLocalNodeIds->getValue<node_id>(i);
      mMap[remoteTaskId][localNodeId].insert(remoteLocalNodeId);
    }
  }
}


void
XdmfMap::release()
{
  mMap.clear();
}

void
XdmfMap::setHeavyDataControllers(std::vector<shared_ptr<XdmfHeavyDataController> > remoteTaskIdsControllers,
                                 std::vector<shared_ptr<XdmfHeavyDataController> > localNodeIdsControllers,
                                 std::vector<shared_ptr<XdmfHeavyDataController> > remoteLocalNodeIdsControllers)
{
  unsigned int localNodeCount = 0;
  for (unsigned int i = 0; i< localNodeIdsControllers.size(); ++i)
  {
    localNodeCount += localNodeIdsControllers[i]->getSize();
  }
  unsigned int remoteTaskCount = 0;
  for (unsigned int i = 0; i< remoteTaskIdsControllers.size(); ++i)
  {
    remoteTaskCount += remoteTaskIdsControllers[i]->getSize();
  }
  unsigned int remoteNodeCount = 0;
  for (unsigned int i = 0; i< remoteLocalNodeIdsControllers.size(); ++i)
  {
    remoteNodeCount += remoteLocalNodeIdsControllers[i]->getSize();
  }
  if(!(localNodeCount ==
       remoteTaskCount &&
       localNodeCount ==
       remoteNodeCount)) {
    XdmfError::message(XdmfError::FATAL,
                       "Arrays must be of equal size in "
                       "XdmfMap::setHeavyDataControllers");
  }
  mRemoteTaskIdsControllers = remoteTaskIdsControllers;
  mLocalNodeIdsControllers = localNodeIdsControllers;
  mRemoteLocalNodeIdsControllers = remoteLocalNodeIdsControllers;
}

void 
XdmfMap::setMap(std::map<task_id, node_id_map> map)
{
  mMap = map;
}

void
XdmfMap::setName(const std::string & name)
{
  mName = name;
}

void
XdmfMap::traverse(const shared_ptr<XdmfBaseVisitor> visitor)
{
  XdmfItem::traverse(visitor);

  shared_ptr<XdmfArray> remoteTaskIds = XdmfArray::New();
  shared_ptr<XdmfArray> localNodeIds = XdmfArray::New();
  shared_ptr<XdmfArray> remoteLocalNodeIds = XdmfArray::New();

  for(std::map<task_id, node_id_map>::const_iterator
        iter = mMap.begin();
      iter != mMap.end();
      ++iter) {
    for(node_id_map::const_iterator
          iter2 = iter->second.begin();
        iter2 != iter->second.end();
        ++iter2) {
      for(node_id_map::mapped_type::const_iterator iter3 =
            iter2->second.begin();
          iter3 != iter2->second.end();
          ++iter3) {
        remoteTaskIds->pushBack(iter->first);
        localNodeIds->pushBack(iter2->first);
        remoteLocalNodeIds->pushBack(*iter3);
      }
    }
  }

  for (unsigned int i = 0; i < mRemoteTaskIdsControllers.size(); ++i)
  {
    remoteTaskIds->insert(mRemoteTaskIdsControllers[i]);
  }
  for (unsigned int i = 0; i < mLocalNodeIdsControllers.size(); ++i)
  {
    localNodeIds->insert(mLocalNodeIdsControllers[i]);
  }
  for (unsigned int i = 0; i < mRemoteLocalNodeIdsControllers.size(); ++i)
  {
    remoteLocalNodeIds->insert(mRemoteLocalNodeIdsControllers[i]);
  }

  remoteTaskIds->accept(visitor);
  localNodeIds->accept(visitor);
  remoteLocalNodeIds->accept(visitor);

  mLocalNodeIdsControllers.clear();
  mRemoteTaskIdsControllers.clear();
  mRemoteLocalNodeIdsControllers.clear();

  for (unsigned int i = 0; i < remoteTaskIds->getNumberHeavyDataControllers(); ++i)
  {
    mRemoteTaskIdsControllers.push_back(remoteTaskIds->getHeavyDataController(i));
  }
  for (unsigned int i = 0; i < localNodeIds->getNumberHeavyDataControllers(); ++i)
  {
    mLocalNodeIdsControllers.push_back(localNodeIds->getHeavyDataController(i));
  }
  for (unsigned int i = 0; i < remoteLocalNodeIds->getNumberHeavyDataControllers(); ++i)
  {
    mRemoteLocalNodeIdsControllers.push_back(remoteLocalNodeIds->getHeavyDataController(i));
  }
}
