if (VTK_WRAP_PYTHON)
  vtk_module(vtkFiltersPython
    GROUPS
      StandAlone
    DEPENDS
      vtkCommonExecutionModel
      vtkPython
    PRIVATE_DEPENDS
      vtkWrappingPythonCore
    EXCLUDE_FROM_TCL_WRAPPING
    EXCLUDE_FROM_JAVA_WRAPPING
    TEST_DEPENDS
      vtkTestingCore
    KIT
      vtkWrapping
    )
endif ()
