cmake_minimum_required(VERSION 3.20)





# import custom cmake modules
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
# import 3rd party deps configured by vcpkg
include(vcpkg-config)


set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project("joy_project" CXX)

if(CMAKE_BUILD_TYPE STREQUAL Debug)
  add_definitions(-D_DEBUG)
  if(MSVC
     AND WIN32
     AND NOT MSVC_VERSION VERSION_LESS 142)
    set(CMAKE_CXX_FLAGS_DEBUG "/ZI")
  endif()
endif()
set(CMAKE_DEBUG_POSTFIX "_d")
# GNU install standard
include(GNUInstallDirs)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})

# Include this module to search for compiler-provided system runtime libraries
# and add install rules for them.
include(InstallRequiredSystemLibraries)
# if(UNIX)
# find_package(Boost REQUIRED)
# elseif(WIN32)
# find_package(Boost COMPONENTS serialization REQUIRED)
# endif()
# find_package(rttr CONFIG REQUIRED)


#if(MSVC)
#    add_compile_options(/nologo)    # 关闭版权信息
#    add_compile_options(/W0)        # 关闭所有警告
#endif()

#if(MSVC)
#    add_compile_options(/utf-8)  # 告知编译器以UTF-8处理源文件和字符串
#endif()

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
    ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}$<IF:$<CONFIG:Debug>,/deubg/${dynamic_path},/${dynamic_path}>
)

set(VCPKG_INCLUDE ${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/include)
include_directories(${VCPKG_INCLUDE})
include_directories(${CMAKE_SOURCE_DIR}/src)

# show installation directories
foreach(_p LIB BIN INCLUDE CMAKE)
  file(TO_NATIVE_PATH ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_${_p}DIR} _path)
  message(STATUS "Show installing ${_p} components to ${_path}")
  unset(_path)
endforeach()

include(coverage)
add_code_coverage_all_targets(EXCLUDE ${CMAKE_BINARY_DIR}/* /usr/include/*)

# add_test support
include(CTest)
# include(Dart)
enable_testing()

include(sanitizer)
include(ds-copy-file)
include(ds-source-group)
# include(monitor)
include(OSInstall)

# include_directories(${CMAKE_SOURCE_DIR}/src/logger/include)

add_subdirectory(${CMAKE_SOURCE_DIR}/src/joy_utility)
set(BUILD_TESTING TRUE)

message(STATUS "BUILD_TESTING:${BUILD_TESTING}")
if(BUILD_TESTING)
  add_subdirectory(${CMAKE_SOURCE_DIR}/test)
endif()
