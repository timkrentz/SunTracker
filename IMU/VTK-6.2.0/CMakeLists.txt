cmake_minimum_required(VERSION 2.8.8 FATAL_ERROR)

option(VTK_ENABLE_KITS "Build VTK using kits instead of modules." OFF)
mark_as_advanced(VTK_ENABLE_KITS)
if(VTK_ENABLE_KITS)
  # Kits use INTERFACE libraries which were introduced in 3.0.
  cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
endif()

foreach(p
    CMP0020 # CMake 2.8.11
    CMP0022 # CMake 2.8.12
    CMP0025 # CMake 3.0
    CMP0053 # CMake 3.1
    )
  if(POLICY ${p})
    cmake_policy(SET ${p} NEW)
  endif()
endforeach()

# Set a consistent MACOSX_RPATH default across all CMake versions.
# When CMake 2.8.12 is required, change this default to 1.
# When CMake 3.0.0 is required, remove this block (see CMP0042).
if(NOT DEFINED CMAKE_MACOSX_RPATH)
  set(CMAKE_MACOSX_RPATH 0)
endif()

project(VTK)

# Objective-C++ compile flags.
# CMake has no equivalent of CMAKE_CXX_FLAGS for Objective-C++ (bug #4756)
# so we provide this in case the user needs to specify flags specifically
# for Objective-C++ source files.  For example, to build with garbage
# collection support, the -fobjc-gc flag would be used.
IF(APPLE)
  SET(VTK_OBJCXX_FLAGS_DEFAULT "")
  SET(VTK_REQUIRED_OBJCXX_FLAGS ${VTK_OBJCXX_FLAGS_DEFAULT} CACHE STRING "Extra flags for Objective-C++ compilation")
  MARK_AS_ADVANCED(VTK_REQUIRED_OBJCXX_FLAGS)
ENDIF()

set(VTK_CMAKE_DIR "${VTK_SOURCE_DIR}/CMake")
set(CMAKE_MODULE_PATH ${VTK_CMAKE_DIR} ${CMAKE_MODULE_PATH})

include(vtkModuleMacros)
include(vtkExternalData)

# Set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Debug' as none was specified.")
  set(CMAKE_BUILD_TYPE Debug CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
    "MinSizeRel" "RelWithDebInfo")
endif()

# Test input data staging directory.
file(RELATIVE_PATH vtk_reldir "${CMAKE_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}")
set(VTK_TEST_DATA_DIR "${ExternalData_BINARY_ROOT}/${vtk_reldir}/Testing")

# Test input data directory.
set(VTK_TEST_INPUT_DIR "${VTK_SOURCE_DIR}/Testing/Data")

# Test output directory.
set(VTK_TEST_OUTPUT_DIR "${VTK_BINARY_DIR}/Testing/Temporary")

# Set up our directory structure for output libraries and binaries
if(NOT CMAKE_RUNTIME_OUTPUT_DIRECTORY)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${VTK_BINARY_DIR}/bin")
endif()
if(NOT CMAKE_LIBRARY_OUTPUT_DIRECTORY)
  if(UNIX)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${VTK_BINARY_DIR}/lib")
  else()
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${VTK_BINARY_DIR}/bin")
  endif()
endif()
if(NOT CMAKE_ARCHIVE_OUTPUT_DIRECTORY)
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${VTK_BINARY_DIR}/lib")
endif()
mark_as_advanced(CMAKE_RUNTIME_OUTPUT_DIRECTORY
  CMAKE_LIBRARY_OUTPUT_DIRECTORY
  CMAKE_ARCHIVE_OUTPUT_DIRECTORY
  )

include(vtkVersion)
set(VTK_VERSION
    "${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION}.${VTK_BUILD_VERSION}")

option(VTK_IOS_BUILD "Build vtk.framework for iOS" OFF)
if (VTK_IOS_BUILD)
  include(vtkiOS)
  return()
endif()

option(VTK_ANDROID_BUILD "Build VTK for Android" OFF)
if (VTK_ANDROID_BUILD)
  include(vtkAndroid)
  return()
endif()

# some specific defaults for Andriod to give folks
# a reasonable starting point
if (ANDROID OR APPLE_IOS)
  SET( CMAKE_REQUIRE_LARGE_FILE_SUPPORT 2
       CACHE STRING "Result from TRY_RUN" FORCE)
  SET( CMAKE_REQUIRE_LARGE_FILE_SUPPORT__TRYRUN_OUTPUT ""
       CACHE STRING "Output from TRY_RUN" FORCE)
  SET( VTK_TYPE_CHAR_IS_SIGNED 1
     CACHE STRING "Result from TRY_RUN" FORCE)
  SET( VTK_ANSI_STREAM_EOF_RESULT 0
     CACHE STRING "Result from TRY_RUN" FORCE)
  SET( KWSYS_CHAR_IS_SIGNED 1
     CACHE STRING "Result from TRY_RUN" FORCE)
  SET( KWSYS_LFS_WORKS 2
     CACHE STRING "Result from TRY_RUN" FORCE)
  SET( KWSYS_LFS_WORKS__TRYRUN_OUTPUT ""
     CACHE STRING "Output from TRY_RUN" FORCE)

  option(BUILD_SHARED_LIBS "should be off for embedded" OFF)
  set(VTK_RENDERING_BACKEND OpenGL2)
  set(Module_vtkRenderingCore ON)
  option(VTK_Group_Rendering "off for embedded" OFF)
  option(VTK_Group_StandAlone "off for embedded" OFF)
  option(VTK_Group_Imaging "off for embedded" OFF)
  option(VTK_Group_MPI "off for embedded" OFF)
  option(VTK_Group_Views "off for embedded" OFF)
  option(VTK_Group_Qt "off for embedded" OFF)
  option(VTK_Group_Tk "off for embedded" OFF)
  option(VTK_Group_Web "off for embedded" OFF)

  # need int version for CPP
  if (${OPENGL_ES_VERSION} MATCHES 2.0)
    set(OPENGL_ES_VERSION_INT 20)
  endif()
  if (${OPENGL_ES_VERSION} MATCHES 3.0)
    set(OPENGL_ES_VERSION_INT 30)
  endif()

  if (APPLE_IOS)
    unset(OPENGL_INCLUDE_DIR CACHE)
    if (${OPENGL_ES_VERSION} MATCHES 2.0)
      find_path(OPENGL_INCLUDE_DIR ES2/gl.h
                ${CMAKE_OSX_SYSROOT}/System/Library/Frameworks/OpenGLES.framework/Headers
                ${_OPENGL_INCLUDE_DIR})
    elseif (${OPENGL_ES_VERSION} MATCHES 3.0)
      find_path(OPENGL_INCLUDE_DIR ES3/gl.h
                ${CMAKE_OSX_SYSROOT}/System/Library/Frameworks/OpenGLES.framework/Headers
                ${_OPENGL_INCLUDE_DIR})
    endif()
    find_library(OPENGL_gl_LIBRARY
       NAMES OpenGLES
       PATHS
         ${CMAKE_OSX_SYSROOT}/System/Library/Frameworks
         ${_OPENGL_LIB_PATH}
       )
  elseif (ANDROID)
    unset(OPENGL_INCLUDE_DIR CACHE)
    unset(OPENGL_gl_LIBRARY CACHE)
    unset(OPENGL_egl_LIBRARY CACHE)

    if (${OPENGL_ES_VERSION} MATCHES 2.0)
      find_path(OPENGL_INCLUDE_DIR GLES2/gl2.h
         ${ANDROID_NDK}/platforms/android-${ANDROID_NATIVE_API_LEVEL}/arch-${ANDROID_ARCH_NAME}/usr/include
         ${_OPENGL_INCLUDE_PATH}
         NO_DEFAULT_PATH
         )
      find_library(OPENGL_gl_LIBRARY
         NAMES GLESv2
         PATHS
           ${ANDROID_NDK}/platforms/android-${ANDROID_NATIVE_API_LEVEL}/arch-${ANDROID_ARCH_NAME}/usr/lib
           ${_OPENGL_LIB_PATH}
         )
    elseif (${OPENGL_ES_VERSION} MATCHES 3.0)
      find_path(OPENGL_INCLUDE_DIR GLES3/gl3.h
         ${ANDROID_NDK}/platforms/android-${ANDROID_NATIVE_API_LEVEL}/arch-${ANDROID_ARCH_NAME}/usr/include
         ${_OPENGL_INCLUDE_PATH}
         )
      find_library(OPENGL_gl_LIBRARY
         NAMES GLESv3
         PATHS
           ${ANDROID_NDK}/platforms/android-${ANDROID_NATIVE_API_LEVEL}/arch-${ANDROID_ARCH_NAME}/usr/lib
           ${_OPENGL_LIB_PATH}
         )
    endif()
    find_library(OPENGL_egl_LIBRARY
       NAMES EGL
       PATHS
         ${ANDROID_NDK}/platforms/android-${ANDROID_NATIVE_API_LEVEL}/arch-${ANDROID_ARCH_NAME}/usr/lib
         ${_OPENGL_LIB_PATH}
       )
  endif()
else()
  # Choose static or shared libraries.
  option(BUILD_SHARED_LIBS "Build VTK with shared libraries." ON)
endif()

set(VTK_BUILD_SHARED_LIBS ${BUILD_SHARED_LIBS})

#-----------------------------------------------------------------------------
# VTK installation structure
if(NOT VTK_INSTALL_RUNTIME_DIR)
  set(VTK_INSTALL_RUNTIME_DIR bin)
endif()
if(NOT VTK_INSTALL_LIBRARY_DIR)
  set(VTK_INSTALL_LIBRARY_DIR lib)
endif()
if(NOT VTK_INSTALL_ARCHIVE_DIR)
  set(VTK_INSTALL_ARCHIVE_DIR lib)
endif()
if(NOT VTK_INSTALL_INCLUDE_DIR)
  set(VTK_INSTALL_INCLUDE_DIR include/vtk-${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION})
endif()
if(NOT VTK_INSTALL_DATA_DIR)
  set(VTK_INSTALL_DATA_DIR share/vtk-${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION})
endif()
if(NOT VTK_INSTALL_DOC_DIR)
  set(VTK_INSTALL_DOC_DIR share/doc/vtk-${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION})
endif()
if(NOT VTK_INSTALL_PACKAGE_DIR)
  set(VTK_INSTALL_PACKAGE_DIR "lib/cmake/vtk-${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION}")
endif()
if(NOT VTK_INSTALL_DOXYGEN_DIR)
  set(VTK_INSTALL_DOXYGEN_DIR ${VTK_INSTALL_DOC_DIR}/doxygen)
endif()
if(NOT VTK_INSTALL_TCL_DIR)
  # tclsh searches <prefix>/lib/tcltk and its subdirectories for pkgIndex.tcl files
  set(VTK_INSTALL_TCL_DIR lib/tcltk/vtk-${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION})
endif()
if(NOT VTK_INSTALL_EXPORT_NAME)
  set(VTK_INSTALL_EXPORT_NAME VTKTargets)
endif()
if(NOT VTK_MODULES_DIR)
  set(VTK_MODULES_DIR "${VTK_BINARY_DIR}/${VTK_INSTALL_PACKAGE_DIR}/Modules")
endif()
if(NOT VTK_WWW_DIR)
  set(VTK_WWW_DIR "${VTK_BINARY_DIR}/www")
endif()
if(NOT VTK_INSTALL_PYTHON_MODULE_DIR)
  set (VTK_INSTALL_PYTHON_MODULE_DIR "-NOTFOUND" CACHE
       PATH "Directory where python modules will be installed")
  mark_as_advanced(VTK_INSTALL_PYTHON_MODULE_DIR)
endif()
if(NOT VTK_BUILD_PYTHON_MODULE_DIR)
  set (VTK_BUILD_PYTHON_MODULE_DIR "-NOTFOUND" CACHE
       PATH "Directory where python modules will be put inside the build tree")
  mark_as_advanced(VTK_BUILD_PYTHON_MODULE_DIR)
endif()
if (CMAKE_CROSSCOMPILING AND NOT COMPILE_TOOLS_IMPORTED)
  # if CMAKE_CROSSCOMPILING is true, we need to import build-tools targets.
  find_package(VTKCompileTools REQUIRED)
  set (COMPILE_TOOLS_IMPORTED TRUE)
endif()

#-----------------------------------------------------------------------------
# Do we try to use system libraries by default?
option(VTK_USE_SYSTEM_LIBRARIES "Use the system's libraries by default." OFF)
mark_as_advanced(VTK_USE_SYSTEM_LIBRARIES)

#-----------------------------------------------------------------------------
# The third party macros are still used in one or two third party builds.
include(vtkThirdParty)

#-----------------------------------------------------------------------------
include(vtkCompilerExtras)
include(vtkBuildPath)

#-----------------------------------------------------------------------------
if(NOT EXISTS "${VTK_SOURCE_DIR}/.ExternalData/README.rst")
  # This file is always present in version-controlled source trees
  # so we must have been extracted from a source tarball with no
  # data objects needed for testing.  Turn off tests by default
  # since enabling them requires network access or manual data
  # store configuration.
  option(BUILD_TESTING "Build the testing tree." OFF)
endif()
include(CTest)

#-----------------------------------------------------------------------------
if(APPLE)
  mark_as_advanced(
    CMAKE_OSX_ARCHITECTURES
    CMAKE_OSX_DEPLOYMENT_TARGET
    CMAKE_OSX_SYSROOT
    )
endif()

#-----------------------------------------------------------------------------
# Does VTK require support for 64 bit file systems
INCLUDE(CheckCXXSourceRuns)
FILE(READ "${VTK_CMAKE_DIR}/vtkRequireLargeFilesSupport.cxx"
  VTK_REQUIRE_LARGE_FILE_SUPPORT_FILE)
CHECK_CXX_SOURCE_RUNS("${VTK_REQUIRE_LARGE_FILE_SUPPORT_FILE}"
  CMAKE_REQUIRE_LARGE_FILE_SUPPORT "Support for 64 bit file systems")
SET(VTK_REQUIRE_LARGE_FILE_SUPPORT ${CMAKE_REQUIRE_LARGE_FILE_SUPPORT})

#-----------------------------------------------------------------------------
# Does the const_reverse_iterator have the comparison operators? Before GCC
# 4.1 they were not present.
include(CheckCXXSourceCompiles)
set(VTK_CONST_REVERSE_ITERATOR_COMPARISON_FILE
"#include <vector>
int main()
{
  std::vector<int> test;
  std::vector<int>::const_reverse_iterator it = test.rbegin();
  it != test.rend();
  return 0;
}")
check_cxx_source_compiles("${VTK_CONST_REVERSE_ITERATOR_COMPARISON_FILE}"
  VTK_CONST_REVERSE_ITERATOR_COMPARISON)

#-----------------------------------------------------------------------------
# Provide compatibility options.
option(VTK_LEGACY_REMOVE "Remove all legacy code completely." OFF)
option(VTK_LEGACY_SILENT "Silence all legacy code messages." OFF)
mark_as_advanced(VTK_LEGACY_REMOVE VTK_LEGACY_SILENT)

#-----------------------------------------------------------------------------
# VTK requires special compiler flags on some platforms.
include(vtkDetermineCompilerFlags)

# Tell VTK source files they are being built inside VTK.
add_definitions(-DVTK_IN_VTK)

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  include(vtkLegacyData)
endif()

# Provide an option for tests requiring "large" input data
option(VTK_USE_LARGE_DATA "Enable tests requiring \"large\" data" OFF)

#-----------------------------------------------------------------------------
# Platform configuration tests.
include(TestBigEndian)
TEST_BIG_ENDIAN(CMAKE_WORDS_BIGENDIAN)

include(FindThreads)
set(VTK_USE_WIN32_THREADS 0)
set(VTK_USE_PTHREADS 0)
set(VTK_HP_PTHREADS 0)
set(VTK_USE_SPROC 0)
# if win32 threads and pthreads are available figure out which
# one the compiler is setup to use.  If you can not figure it
# out default to pthreads.
if(CMAKE_USE_PTHREADS_INIT AND CMAKE_USE_WIN32_THREADS_INIT)
  if(DEFINED VTK_THREAD_MODEL)
    set(output "${VTK_THREAD_MODEL}")
  else()
    execute_process(COMMAND "${CMAKE_C_COMPILER}" -v OUTPUT_VARIABLE output
      ERROR_VARIABLE output RESULT_VARIABLE result TIMEOUT 10)
  endif()
  if(output MATCHES "Thread model: posix")
    set(VTK_THREAD_MODEL "Thread model: posix" CACHE STRING
      "Thread model used by gcc.")
    set(CMAKE_USE_WIN32_THREADS_INIT 0)
  elseif(output MATCHES "Thread model: win32")
    set(VTK_THREAD_MODEL "Thread model: win32" CACHE STRING
      "Thread model used by gcc.")
    set(CMAKE_USE_PTHREADS_INIT 0)
  else()
    set(VTK_THREAD_MODEL "Thread model: posix" CACHE STRING
      "Thread model used by gcc.")
    set(CMAKE_USE_WIN32_THREADS_INIT 0)
  endif()
endif()
mark_as_advanced(VTK_THREAD_MODEL)
if(CMAKE_USE_WIN32_THREADS_INIT)
  set(VTK_USE_WIN32_THREADS 1)
  set(CMAKE_THREAD_LIBS_INIT "")
elseif(CMAKE_USE_PTHREADS_INIT)
  set(VTK_USE_PTHREADS 1)
  if(CMAKE_HP_PTHREADS_INIT)
    set(VTK_HP_PTHREADS 1)
  endif()
elseif(CMAKE_USE_SPROC_INIT)
  set(VTK_USE_SPROC 1)
endif()
set(CMAKE_THREAD_LIBS "${CMAKE_THREAD_LIBS_INIT}" CACHE STRING "Thread library used.")
mark_as_advanced(CMAKE_THREAD_LIBS)
set(VTK_MAX_THREADS "64" CACHE STRING
  "Max number of threads vktMultiThreader will allocate.")
mark_as_advanced(VTK_MAX_THREADS)

include(TestForANSIStreamHeaders)
include(TestForSTDNamespace)
include(TestForANSIForScope)
include(CheckTypeSize)

# Simulate old CMakeBackwardCompatibilityCXX test.
include(TestForSSTREAM)

# Tests for various integer, bool and float types
include(vtkTestTypes)

# Socket tests etc.
#INCLUDE(Parallel/VTKParallelCMakeTests.cmake)

# Check for full template specialization support by compiler.
include(vtkTestFullSpecialization)

# Check for explicit template instantiation support by compiler.
include(vtkTestExplicitInstantiation)

# Test for atomics and other compiler intrinsics
include(vtkTestBuiltins)

#-----------------------------------------------------------------------------

# Check the severity of EOF bugs in the streams library.
# this must be after the test for the long types
INCLUDE(vtkTestStreamsLibrary)

#-----------------------------------------------------------------------------
# Dispatch the build into the proper subdirectories.
SET(VTK_HAS_EXODUS 1)

#-----------------------------------------------------------------------------
# Provide a few configuration options.
OPTION(BUILD_EXAMPLES "Build VTK examples." OFF)

#-----------------------------------------------------------------------------
# Configure files with settings for use by the build.

# Include the sockets test.
# FIXME: The test should be moved and rewritten.
include(VTKParallelCMakeTests)

# Add the option for build the Python wrapping to VTK.
option(VTK_WRAP_PYTHON "Should VTK Python wrapping be built?" OFF)
set(VTK_PYTHON_VERSION 2 CACHE STRING
    "Python version to use: 2, 2.x, or empty")

# Add the option for build the Python wrapping to VTK.
option(VTK_WRAP_JAVA "Should VTK Java wrapping be built?" OFF)

# FIXME: This variable should not be necessary once we are done
set(VTK_IGNORE_BTX ON CACHE INTERNAL "VTK modular always ignores BTX")

# Force reset of hints file location in cache if it was moved
if(VTK_WRAP_HINTS)
  if(NOT EXISTS ${VTK_WRAP_HINTS})
    set(VTK_WRAP_HINTS "VTK_WRAP_HINTS-NOTFOUND")
  endif()
endif()

find_file(VTK_WRAP_HINTS hints ${VTK_SOURCE_DIR}/Wrapping/Tools
  NO_CMAKE_FIND_ROOT_PATH)
mark_as_advanced(VTK_WRAP_HINTS)

if(BUILD_TESTING OR VTK_WRAP_PYTHON)
  # Need PYTHON_EXECUTABLE for HeaderTesting or python wrapping
  find_package(PythonInterp ${VTK_PYTHON_VERSION} QUIET)
  mark_as_advanced(PYTHON_EXECUTABLE)
endif()

if(VTK_WRAP_PYTHON)
  set(VTK_WRAP_PYTHON_EXE vtkWrapPython)
  set(VTK_WRAP_PYTHON_INIT_EXE vtkWrapPythonInit)
  set(VTK_PYTHON_EXE vtkpython)
  # Force the WrappingPythonCore module to on if wrapping is on
  set(Module_vtkWrappingPythonCore ON CACHE BOOL "Core Python wrapping library"
    FORCE)
else()
  # if wrapping is not on then force WrappingPythonCore module to be off
  set(Module_vtkWrappingPythonCore OFF CACHE BOOL "Core Python wrapping library"
    FORCE)
endif()

if(VTK_WRAP_JAVA)
  set(VTK_WRAP_JAVA3_INIT_DIR "${VTK_SOURCE_DIR}/Wrapping/Java")
  # Wrapping executables.
  set(VTK_WRAP_JAVA_EXE  vtkWrapJava)
  set(VTK_PARSE_JAVA_EXE vtkParseJava)
  set(Module_vtkWrappingJava ON CACHE BOOL "Core Java wrapping library"
    FORCE)

  # Java package location.
  set(VTK_JAVA_JAR ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/vtk.jar)
  set(VTK_JAVA_HOME ${VTK_BINARY_DIR}/java/vtk)
  file(MAKE_DIRECTORY ${VTK_JAVA_HOME})
else()
  set(Module_vtkWrappingJava OFF CACHE BOOL "Core Java wrapping library"
    FORCE)
endif()

# Now for Tcl wrapping.
option(VTK_WRAP_TCL "Should VTK Tcl wrapping be built?" OFF)
if(VTK_WRAP_TCL)
  set(VTK_WRAP_TCL_EXE vtkWrapTcl)
  set(VTK_WRAP_TCL_INIT_EXE vtkWrapTclInit)
  set(VTK_TCL_EXE vtk)
  # Tcl package location.
  set(VTK_TCL_HOME ${VTK_BINARY_DIR}/Wrapping/Tcl)
  # Force the WrappingTcl module to on if wrapping is on
  set(Module_vtkWrappingTcl ON CACHE BOOL "Core Tcl wrapping library"
    FORCE)
else()
  # if wrapping is not on then force WrappingTcl module to be off
  set(Module_vtkWrappingTcl OFF CACHE BOOL "Core Tcl wrapping library"
    FORCE)
endif()

if(VTK_WRAP_PYTHON OR VTK_WRAP_TCL OR VTK_WRAP_JAVA)
  set(VTK_WRAP_HIERARCHY_EXE vtkWrapHierarchy)
endif()

# This is not normally necessary, but could be desirable in some circumstances.
option(VTK_MAKE_INSTANTIATORS "Should all modules build instantiators" OFF)
mark_as_advanced(VTK_MAKE_INSTANTIATORS)

#----------------------------------------------------------------------
# Load the module DAG, assess all modules etc.
include(vtkModuleTop)

# Now build the Python wrapping if necessary.
if(VTK_WRAP_PYTHON)
  add_subdirectory(Wrapping/Python)
endif()

if(BUILD_TESTING)
  add_subdirectory(Testing/Install)
endif()

if(BUILD_EXAMPLES)
  add_subdirectory(Examples)
endif()

# The doxygen documentation needs to be aware of all modules.
option(BUILD_DOCUMENTATION "Build the VTK documentation" OFF)
if(BUILD_DOCUMENTATION)
  add_subdirectory(Utilities/Doxygen)
endif()

# If python wrapping and testing is enabled then add driver scripts to run
# tests.  Note: Many pythong tests used to be automatically converted from TCL
# scripts. Hence the name vtkTclTest2Py
if(BUILD_TESTING AND VTK_WRAP_PYTHON)
  add_subdirectory(Utilities/vtkTclTest2Py)
endif()

# Configure the CTestCustom.cmake file now that everything is done.
set(memcheck_excluded_tests "  # These tests do not run any VTK code\n")
foreach(vtk-module ${VTK_MODULES_ALL})
  set(memcheck_excluded_tests
    "${memcheck_excluded_tests}  ${vtk-module}-HeaderTest\n")
endforeach()
configure_file("${VTK_CMAKE_DIR}/CTestCustom.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/CTestCustom.cmake" @ONLY)

#-----------------------------------------------------------------------------
# Export all targets at once from the build tree in their final configuration.
get_property(_vtk_targets GLOBAL PROPERTY VTK_TARGETS)
get_property(_vtk_compiletools_targets GLOBAL PROPERTY VTK_COMPILETOOLS_TARGETS)
set (_vtk_all_targets ${_vtk_targets} ${_vtk_compiletools_targets})
if (_vtk_all_targets)
  list(REMOVE_DUPLICATES _vtk_all_targets)
  export(TARGETS ${_vtk_all_targets} FILE ${VTK_BINARY_DIR}/VTKTargets.cmake)
endif()
# Add a virtual target that can be used to build all compile tools.
add_custom_target(vtkCompileTools)
if (_vtk_compiletools_targets)
  list(REMOVE_DUPLICATES _vtk_compiletools_targets)
  export(TARGETS ${_vtk_compiletools_targets}
         FILE ${VTK_BINARY_DIR}/VTKCompileToolsConfig.cmake)
  add_dependencies(vtkCompileTools ${_vtk_compiletools_targets})
endif()

unset(_vtk_targets)
unset(_vtk_compiletools_targets)
unset(_vtk_all_targets)

# Create target to download data from the VTKData group.  This must come after
# all tests have been added that reference the group, so we put it last.
ExternalData_Add_Target(VTKData)
if(VTK_DATA_EXCLUDE_FROM_ALL)
  set_property(TARGET VTKData PROPERTY EXCLUDE_FROM_ALL 1)
  if(BUILD_TESTING AND NOT VTK_DATA_EXCLUDE_FROM_ALL_NO_WARNING)
    message(WARNING "VTK_DATA_EXCLUDE_FROM_ALL is ON so test data "
      "(needed because BUILD_TESTING is ON) may not be available "
      "without manually building the 'VTKData' target.")
  endif()
endif()
