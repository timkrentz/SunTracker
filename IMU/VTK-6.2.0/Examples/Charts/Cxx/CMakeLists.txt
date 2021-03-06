PROJECT (Charts)

IF(NOT VTK_BINARY_DIR)
FIND_PACKAGE(VTK REQUIRED)
IF(NOT VTK_USE_CHARTS)
  MESSAGE(FATAL_ERROR "Example ${PROJECT_NAME} requires VTK_USE_CHARTS.")
ENDIF()
INCLUDE(${VTK_USE_FILE})
ENDIF()

IF(VTK_USE_VIEWS)
  ADD_EXECUTABLE(GraphItem GraphItem.cxx vtkGraphItem.cxx)
  TARGET_LINK_LIBRARIES(GraphItem vtkCharts)
ENDIF()

ADD_EXECUTABLE(PiecewiseItem PiecewiseItem.cxx)
TARGET_LINK_LIBRARIES(PiecewiseItem vtkCharts)

IF(VTK_USE_QVTK)
  FIND_PACKAGE(Qt4 REQUIRED)
  INCLUDE(${QT_USE_FILE})
  INCLUDE_DIRECTORIES(${QT_INCLUDE_DIR})
  ADD_EXECUTABLE(QChartTable QChartTable.cxx)
  TARGET_LINK_LIBRARIES(QChartTable
    QVTK
    ${QT_LIBRARIES}
    vtkRendering
    vtkCharts
  )
  ADD_EXECUTABLE(QScalarsToColors QScalarsToColors.cxx)
  TARGET_LINK_LIBRARIES(QScalarsToColors
    QVTK
    ${QT_LIBRARIES}
    vtkRendering
    vtkCharts
  )
ENDIF()
