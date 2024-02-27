set(tools_dll tools)
file(GLOB_RECURSE tools_src src/*.*)
file(GLOB_RECURSE tools_hdr include/*.*)
set(tools_all ${tools_src} ${tools_hdr})


message(STATUS "${tools_src}")
message(STATUS "${tools_hdr}")

add_library(${tools_dll} SHARED ${tools_all})
#若是exe则
# copy_sanitizer_runtime(${tools_dll})

target_compile_definitions(${tools_dll} PRIVATE __TOOLS__)
target_include_directories(${tools_dll} PUBLIC include)
# target_link_libraries(${tools_dll} PRIVATE Iconv::Iconv Boost::locale)
set_target_properties(${tools_dll} PROPERTIES DEBUG_POSTFIX "_d")
ds_source_group_by_dir(tools_all)

include_globally( ${tools_all} logger global_path ${CMAKE_CURRENT_LIST_DIR}/include)

# #以下不建议这么做
# #全局
# set(WINDOWS_EXPORT_ALL_SYMBOLS ON)
# #单项目
# set_target_properties(MyLibrary PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)


install(
  TARGETS ${tools_dll}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})


#install_local_dependencies(TARGETS ${tools_src} DIRECTORIES ${my_dependency_paths})