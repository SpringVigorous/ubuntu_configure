set(handle_data_DLL handle_data)

file(GLOB_RECURSE handle_data_hdrs *.h *.hxx *.inc)
file(GLOB_RECURSE handle_data_srcs *.cpp *.cc)

set(handle_data_all_files ${handle_data_hdrs} ${handle_data_srcs})

add_library(${handle_data_DLL} SHARED ${handle_data_all_files})

target_compile_definitions(${handle_data_DLL} PRIVATE HANDLE_DATA_DLL)

ds_source_group_by_dir(handle_data_all_files)

target_include_directories(${handle_data_DLL} PUBLIC include)


target_link_libraries(${handle_data_DLL}
  PUBLIC data
)



install(
  TARGETS ${handle_data_DLL}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install_local_dependencies(TARGETS ${handle_data_DLL} DIRECTORIES
  ${my_dependency_paths})
