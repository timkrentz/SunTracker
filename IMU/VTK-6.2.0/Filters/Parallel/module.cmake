vtk_module(vtkFiltersParallel
  GROUPS
    StandAlone
  DEPENDS
    vtkParallelCore
    vtkFiltersExtraction
    vtkRenderingCore
    vtkFiltersModeling
    vtkFiltersGeometry
  TEST_DEPENDS
    vtkParallelMPI
    vtkTestingCore
    vtkTestingRendering
    vtkInteractionStyle
    vtkRendering${VTK_RENDERING_BACKEND}
    vtkRenderingParallel
    vtkFiltersParallelMPI
    vtkFiltersParallelImaging
    vtkIOLegacy
  KIT
    vtkParallel
  )
