set(utilities_DLL utilities)

file(GLOB_RECURSE utilities_hdrs *.h *.hxx *.inc)
file(GLOB_RECURSE utilities_srcs *.cpp *.cc)

set(utilities_all_files ${utilities_hdrs} ${utilities_srcs})
# set(utilities_all_files ${utilities_hdrs} ${utilities_srcs})


add_library(${utilities_DLL} SHARED ${utilities_all_files})

target_compile_definitions(${utilities_DLL} PRIVATE UTILITIES_DLL)

ds_source_group_by_dir(utilities_all_files)

target_include_directories(${utilities_DLL} PUBLIC include
    # 使用相对于当前CMakeLists.txt的路径
    #$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    # 如果安装，则使用安装后的路径（可选，用于安装分发）
    # $<INSTALL_INTERFACE:include>
)
find_package(cereal CONFIG REQUIRED)
target_link_libraries(${utilities_DLL}
  PUBLIC cereal::cereal

  
)

install(
  TARGETS ${utilities_DLL}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}

)

install_local_dependencies(TARGETS ${utilities_DLL} DIRECTORIES
  ${my_dependency_paths})
