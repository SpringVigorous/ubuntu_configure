set(common_header_DLL common_header)

file(GLOB_RECURSE common_header_hdrs *.h *.hxx *.inc)
# file(GLOB_RECURSE common_header_srcs *.cpp *.cc)

set(common_header_all_files ${common_header_hdrs} ${common_header_srcs})
# set(common_header_all_files ${common_header_hdrs} ${common_header_srcs})


add_library(${common_header_DLL} INTERFACE ${common_header_all_files})

target_compile_definitions(${common_header_DLL} INTERFACE COMMON_HEADER_DLL)

ds_source_group_by_dir(common_header_all_files)

target_include_directories(${common_header_DLL} INTERFACE
    # 使用相对于当前CMakeLists.txt的路径
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    # 如果安装，则使用安装后的路径（可选，用于安装分发）
    # $<INSTALL_INTERFACE:include>
)
find_package(cereal CONFIG REQUIRED)
target_link_libraries(${common_header_DLL}
  INTERFACE cereal::cereal

  
)

install(
  TARGETS ${common_header_DLL}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}

)

install_local_dependencies(TARGETS ${common_header_DLL} DIRECTORIES
  ${my_dependency_paths})
