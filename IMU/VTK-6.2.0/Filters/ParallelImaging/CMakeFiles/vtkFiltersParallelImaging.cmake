set(vtkFiltersParallelImaging_LOADED 1)
set(vtkFiltersParallelImaging_DEPENDS "vtkFiltersImaging;vtkFiltersParallel;vtkIOLegacy;vtkImagingCore;vtkParallelCore")
set(vtkFiltersParallelImaging_LIBRARIES "vtkFiltersParallelImaging")
set(vtkFiltersParallelImaging_INCLUDE_DIRS "${VTK_INSTALL_PREFIX}/include/vtk-6.2")
set(vtkFiltersParallelImaging_LIBRARY_DIRS "")
set(vtkFiltersParallelImaging_RUNTIME_LIBRARY_DIRS "${VTK_INSTALL_PREFIX}/lib")
set(vtkFiltersParallelImaging_WRAP_HIERARCHY_FILE "${CMAKE_CURRENT_LIST_DIR}/vtkFiltersParallelImagingHierarchy.txt")

