INCLUDE_DIRECTORIES(
  ${CMAKE_CURRENT_BINARY_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}
)
FIND_PACKAGE(GLUT REQUIRED)

VTK_ADD_TEST_CXX(${vtk-module}CxxTests tests
  TestGLUTRenderWindow.cxx
  )

VTK_TEST_CXX_EXECUTABLE(${vtk-module}CxxTests tests)
TARGET_LINK_LIBRARIES(${vtk-module}CxxTests LINK_PRIVATE
  vtkRenderingExternal ${OPENGL_gl_LIBRARY} ${GLUT_LIBRARY})
