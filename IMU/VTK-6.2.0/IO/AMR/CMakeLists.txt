set(Module_SRCS
  vtkAMRDataSetCache.cxx
  vtkAMRBaseParticlesReader.cxx
  vtkAMRBaseReader.cxx
  vtkAMREnzoParticlesReader.cxx
  vtkAMREnzoReader.cxx
  vtkAMREnzoReaderInternal.cxx
  vtkAMRFlashParticlesReader.cxx
  vtkAMRFlashReader.cxx
  vtkAMRFlashReaderInternal.cxx
  )

set_source_files_properties(
  vtkAMRBaseReader
  vtkAMRBaseParticlesReader
  ABSTRACT
  )

set_source_files_properties(
  vtkAMREnzoReaderInternal
  vtkAMRFlashReaderInternal
  WRAP_EXCLUDE
  )

vtk_module_library(vtkIOAMR ${Module_SRCS})
