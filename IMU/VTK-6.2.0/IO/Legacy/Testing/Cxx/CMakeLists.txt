vtk_add_test_cxx(${vtk-module}CxxTests tests
  NO_VALID
  TestLegacyCompositeDataReaderWriter.cxx)
vtk_test_cxx_executable(${vtk-module}CxxTests tests
    RENDERING_FACTORY
    )
