vtk_module(vtkRenderingMatplotlib
  IMPLEMENTS
    vtkRenderingFreeType
  DEPENDS
    vtkImagingCore
    vtkRenderingCore
    vtkPythonInterpreter
  PRIVATE_DEPENDS
    vtkWrappingPythonCore
  TEST_DEPENDS
    vtkCommonColor
    vtkInteractionImage
    vtkInteractionWidgets
    vtkIOGeometry
    vtkTestingRendering
    vtkInteractionStyle
    vtkRendering${VTK_RENDERING_BACKEND}
    vtkRenderingFreeType${VTK_RENDERING_BACKEND}
    vtkViewsContext2D
    vtkIOExport
    vtkRenderingGL2PS
  )
