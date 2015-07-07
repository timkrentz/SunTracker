set(vtkInteractionStyle_HEADERS_LOADED 1)
set(vtkInteractionStyle_HEADERS "vtkInteractorStyleDrawPolygon;vtkInteractorStyleFlight;vtkInteractorStyleImage;vtkInteractorStyleJoystickActor;vtkInteractorStyleJoystickCamera;vtkInteractorStyleMultiTouchCamera;vtkInteractorStyleRubberBand2D;vtkInteractorStyleRubberBand3D;vtkInteractorStyleRubberBandPick;vtkInteractorStyleRubberBandZoom;vtkInteractorStyleTerrain;vtkInteractorStyleTrackballActor;vtkInteractorStyleTrackballCamera;vtkInteractorStyleTrackball;vtkInteractorStyleUnicam;vtkInteractorStyleUser;vtkInteractorStyleSwitch;vtkParallelCoordinatesInteractorStyle")

foreach(header ${vtkInteractionStyle_HEADERS})
  set(vtkInteractionStyle_HEADER_${header}_EXISTS 1)
endforeach()




