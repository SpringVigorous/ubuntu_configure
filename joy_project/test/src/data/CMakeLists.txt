set(data_DLL data)

file(GLOB_RECURSE data_hdrs *.h *.hxx *.inc)
file(GLOB_RECURSE data_srcs *.cpp *.cc)

set(data_all_files ${data_hdrs} ${data_srcs})

add_library(${data_DLL} SHARED ${data_all_files})

target_compile_definitions(${data_DLL} PRIVATE DATA_DLL)

ds_source_group_by_dir(data_all_files)

target_include_directories(${data_DLL} PUBLIC include)


target_link_libraries(${data_DLL}
  PUBLIC common_header
)


install(
  TARGETS ${data_DLL}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install_local_dependencies(TARGETS ${data_DLL} DIRECTORIES
  ${my_dependency_paths})
