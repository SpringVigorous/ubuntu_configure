cmake_minimum_required(VERSION 3.16 FATAL_ERROR)

if(SKBUILD)
  message(STATUS "The project is built using scikit-build")
endif()


# import 3rd party deps configured by vcpkg
if(CMAKE_HOST_WIN32)
  set(VCPKG_ROOT "${CMAKE_SOURCE_DIR}/3rdParty/vcpkg/win")
else()
  set(VCPKG_ROOT "${CMAKE_SOURCE_DIR}/3rdParty/vcpkg/linux")
endif()

# set cmake tool chain
set(CMAKE_TOOLCHAIN_FILE
    ${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake
    CACHE STRING "Vcpkg toolchain file")
message(STATUS "Vcpkg toolchain directory:${CMAKE_TOOLCHAIN_FILE}")

# import custom cmake modules
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")


# Version must be at end of project params
project(
  ProjectExample
  LANGUAGES CXX C)

add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/bigobj>")

# cmake install with deps automatically
set(X_VCPKG_APPLOCAL_DEPS_INSTALL
    OFF
    CACHE BOOL "deps install automatically" FORCE)
message(
  STATUS
    "Open deps install option automatically ${X_VCPKG_APPLOCAL_DEPS_INSTALL}")

# c++17 required
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_BUILD_TYPE)
  message(STATUS "Set default build type as Debug")
  set(CMAKE_BUILD_TYPE
      Debug
      CACHE STRING "Build Type" FORCE)
endif()

# multi config setting
get_property(GENERATOR_IS_MULTI_CONFIG GLOBAL
             PROPERTY GENERATOR_IS_MULTI_CONFIG)
message(STATUS "GENERATOR_IS_MULTI_CONFIG ${GENERATOR_IS_MULTI_CONFIG}")
message(STATUS "CMAKE_CONFIGURATION_TYPES ${CMAKE_CONFIGURATION_TYPES}")
message(STATUS "CMAKE_BUILD_TYPE ${CMAKE_BUILD_TYPE}")

if(${GENERATOR_IS_MULTI_CONFIG})
  set(multi_config_path
      "${CMAKE_BUILD_TYPE}"
      CACHE STRING "Multi Config Path" FORCE)
endif()

file(
  WRITE ${CMAKE_BINARY_DIR}/multi_config.json
  "
{
    \"multi_config\": ${GENERATOR_IS_MULTI_CONFIG}
}")

set(VCPKG_LIBRARY_LINKAGE "dynamic")
message(STATUS "CMAKE_HOST_SYSTEM_NAME  ${CMAKE_HOST_SYSTEM_NAME}")
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
  set(VCPKG_TARGET_IS_WINDOWS TRUE)
  set(VCPKG_TARGET_IS_MINGW FALSE)
endif()

message(STATUS "VCPKG_HOST_TRIPLET ${VCPKG_HOST_TRIPLET}")
message(STATUS "VCPKG_INSTALLED_DIR ${VCPKG_INSTALLED_DIR}")
message(STATUS "VCPKG_TARGET_TRIPLET ${VCPKG_TARGET_TRIPLET}")
message(STATUS "VCPKG_LIBRARY_LINKAGE ${VCPKG_LIBRARY_LINKAGE}")
message(STATUS "VCPKG_TARGET_IS_WINDOWS ${VCPKG_TARGET_IS_WINDOWS}")
message(STATUS "VCPKG_TARGET_IS_MINGW ${VCPKG_TARGET_IS_MINGW}")

# config global include module
include(ConfigIncludeGlobally)

option(INCLUDE_GLOBALLY "Include project directories globally" ON)
message(STATUS "Include project directories globally: ${INCLUDE_GLOBALLY}")

function(load_backtrace_header)
  # load gcc distribution backtrace header
  if(CMAKE_HOST_UNIX)
    message(
      STATUS
        "search backtrace link include ${CMAKE_C_IMPLICIT_LINK_DIRECTORIES}")
    find_path(
      Backtrace_INCLUDE_PATH
      NAMES include/backtrace.h
      PATHS ${CMAKE_C_IMPLICIT_LINK_DIRECTORIES}
      DOC "find backtrace.h" REQUIRED)
    message(
      STATUS
        "backtrace.h found path ${Backtrace_INCLUDE_PATH}/include/backtrace.h")
    add_definitions(
      -DBOOST_STACKTRACE_BACKTRACE_INCLUDE_FILE=<${Backtrace_INCLUDE_PATH}/include/backtrace.h>
    )
  endif(CMAKE_HOST_UNIX)
endfunction()

message(STATUS "Using compiler is ${CMAKE_CXX_COMPILER_ID}")
# compiler setup
if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  # using Clang
  if(CMAKE_HOST_WIN32)
    message(STATUS "Config clang config on win")
  else()
    message(STATUS "Config clang on unix")
    load_backtrace_header()
  endif()

  include_globally(target 3rdParty global_path
                   ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/include)

  message(STATUS "Open exception on Clang")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fexceptions")
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  # using GCC
  load_backtrace_header()
  message(STATUS "Open exception on GNU")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fexceptions")
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
  # using Intel C++
  message(STATUS "Open exception on Intel")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fexceptions")
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
  # using Visual Studio C++
  message(STATUS "Open SEH exception on MSVC")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHa")
endif()

# set unity build
if(CMAKE_HOST_WIN32)
  set(CMAKE_UNITY_BUILD OFF)
  set(CMAKE_UNITY_BUILD_BATCH_SIZE 36)
endif(CMAKE_HOST_WIN32)

# add common macro definition
if(CMAKE_HOST_WIN32)
  # disable unsafe notification
  add_definitions(-D_CRT_SECURE_NO_WARNINGS -DPC_WIN
                  -D_CRT_NONSTDC_NO_DEPRECATE -DNOMINMAX)
elseif(CMAKE_HOST_UNIX)
  add_definitions(-DPC_LINUX -DBOOST_STACKTRACE_USE_BACKTRACE)
endif()

# GNU install standard
include(GNUInstallDirs)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})

set(CMAKE_INSTALL_LIBDIR
    ${CMAKE_INSTALL_LIBDIR}
    CACHE PATH "Installation directory for libraries")
set(CMAKE_INSTALL_BINDIR
    ${CMAKE_INSTALL_BINDIR}
    CACHE PATH "Installation directory for executables")
set(CMAKE_INSTALL_INCLUDEDIR
    ${CMAKE_INSTALL_INCLUDEDIR}
    CACHE PATH "Installation directory for header files")
set(CMAKE_INSTALL_CMAKEDIR
    share/${PROJECT_NAME}
    CACHE PATH "Installation directory for CMake files")

####################################################################
# use, i.e. don't skip the full RPATH for the build tree
set(CMAKE_SKIP_BUILD_RPATH FALSE)

# when building, don't use the install RPATH already (but later on when
# installing)
set(CMAKE_BUILD_WITH_INSTALL_RPATH OFF)

if(NOT APPLE)
  # add system bin auto dly-load such as
  list(APPEND CMAKE_INSTALL_RPATH $ORIGIN/../${CMAKE_INSTALL_LIBDIR};$ORIGIN/${CMAKE_INSTALL_LIBDIR};$ORIGIN)
endif()

# add the automatically determined parts of the RPATH which point to directories
# outside the build tree to the install RPATH
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# dynamic_path specify the 3rd party short deps path depends on os-platform
set(dynamic_path $<IF:$<PLATFORM_ID:Windows>,bin,lib>)
message(STATUS "dynamic libraries path search: ${dynamic_path}")
set(my_dependency_paths
    ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}$<IF:$<CONFIG:Debug>,/debug/${dynamic_path},/${dynamic_path}>
)

set(VCPKG_INCLUDE ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/include)
include_directories(${VCPKG_INCLUDE})
include_directories(${CMAKE_SOURCE_DIR}/src)
####################################################################

# show installation directories
foreach(_p LIB BIN INCLUDE CMAKE)
  file(TO_NATIVE_PATH ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_${_p}DIR} _path)
  message(STATUS "Show installing ${_p} components to ${_path}")
  unset(_path)
endforeach()

# Prepare run path
set(DSO_RUN_PATH)
file(RELATIVE_PATH _rel ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}
     ${CMAKE_INSTALL_PREFIX})
if(APPLE)
  set(_run_path "@loader_path/${_rel}")
else()
  set(_run_path "\$ORIGIN/${_rel}")
endif()
file(TO_NATIVE_PATH "${_run_path}/${CMAKE_INSTALL_LIBDIR}" DSO_RUN_PATH)

# strip all lib unused symobols
if(CMAKE_HOST_UNIX)
  set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -s")
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -s")
endif()

# copy pdb file for debug in win
if(CMAKE_HOST_WIN32 AND "${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
  set(PATH_TO_PDB_FILES
      "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/debug/bin")
  file(GLOB filelist ${PATH_TO_PDB_FILES}/*.pdb)
  file(COPY ${filelist}
       DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${multi_config_path})
endif()

include(ConfigPdbTools)
# copy_pdbs(BUILD_PATHS "${CMAKE_BINARY_DIR}/bin/*.dll"
# "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/debug/bin/*.dll")

# config ccache optimization
include(ConfigCcache)
ccache_enable()

# option(ENABLE_PRE_COMMIT "Enable pre-commit" ON)
# if(ENABLE_PRE_COMMIT)
#   message(STATUS "Enable pre-commit: ${ENABLE_PRE_COMMIT}")
#   include(PreCommit)
#   config_pre_commit()
# endif()

if(CMAKE_HOST_UNIX)
  # ipo optimization
  include(ConfigIPO)
  config_ipo()
endif()

# include(ConfigDoxyGen)
# gen_doxygen_docs()

# configure valgrind
if(CMAKE_HOST_UNIX)
  include(ConfigValgrind)
  config_valgrind()
endif()

# configure pybind11
# include(ConfigPybind11)
# config_pybind11()

# disable cgal performance of build type warning
set(CGAL_DO_NOT_WARN_ABOUT_CMAKE_BUILD_TYPE TRUE)

# find packages to be used from tool chain env
# find_package(Threads)

# find_package(rttr CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)

# find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
# find_package(OpenMP REQUIRED)


# if(OpenMP_FOUND AND "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
#   message(STATUS "Found openmp and set openmp cxx flags for clang lld")
#   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
# endif()

# if(NOT TARGET OpenMP::OpenMP_CXX)
#   message(STATUS "Export OpenMP manually")
#   add_library(OpenMP::OpenMP_CXX IMPORTED INTERFACE)
#   set_property(TARGET OpenMP::OpenMP_CXX PROPERTY INTERFACE_COMPILE_OPTIONS
#                                                   ${OpenMP_CXX_FLAGS})
#   # Only works if the same flag is passed to the linker; use CMake 3.9+
#   # otherwise (Intel, AppleClang)
#   set_property(
#     TARGET OpenMP::OpenMP_CXX PROPERTY INTERFACE_LINK_LIBRARIES
#                                        ${OpenMP_CXX_FLAGS} Threads::Threads)

# endif()

get_directory_property(MyDef DIRECTORY ${CMAKE_SOURCE_DIR} COMPILE_DEFINITIONS)
foreach(d ${MyDef})
  message(STATUS "Found Define: " ${d})
endforeach()

# add srcs
add_subdirectory(src)



# add mfc display
# include(ConfigMFCDisplay)
# add_mfc_display()

# we will use the network to fetch Google Test sources make it possible to
# disable unit tests when not on network
option(ENABLE_UNIT_TESTS "Enable unit tests" ON)
message(STATUS "Enable testing: ${ENABLE_UNIT_TESTS}")

# enable testing and define tests
# enable_testing()

# add memcheck test action
include(CTest)

# when using skbuild don't import test set
if(NOT DEFINED SKBUILD)
  # tests
  add_subdirectory(tests)
endif()
