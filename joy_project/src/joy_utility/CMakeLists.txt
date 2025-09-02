set(joy_utility_DLL joy_utility)

file(GLOB_RECURSE joy_utility_hdrs *.h *.hxx *.inc)
file(GLOB_RECURSE joy_utility_srcs *.cpp *.cc)

set(joy_utility_all_files ${joy_utility_hdrs} ${joy_utility_srcs})

add_library(${joy_utility_DLL} SHARED ${joy_utility_all_files})

target_compile_definitions(${joy_utility_DLL} PRIVATE JOY_UTILITY_DLL)

ds_source_group_by_dir(joy_utility_all_files)
find_path(CPP_BASE64_INCLUDE_DIRS "cpp-base64/base64.cpp")

target_include_directories(${joy_utility_DLL} PUBLIC include PRIVATE ${CPP_BASE64_INCLUDE_DIRS})
find_package(tinyxml2 CONFIG REQUIRED)
find_package(jsoncpp CONFIG REQUIRED)
find_package(Boost REQUIRED COMPONENTS locale)
find_package(boost_uuid REQUIRED CONFIG)
find_package(Iconv)




target_link_libraries(${joy_utility_DLL}
  PUBLIC   tinyxml2::tinyxml2 JsonCpp::JsonCpp
  PRIVATE  Iconv::Iconv Boost::locale  Boost::uuid
)
if (WIN32)
target_link_libraries(${joy_utility_DLL}
  PUBLIC   tinyxml2::tinyxml2 JsonCpp::JsonCpp
  PRIVATE  Iconv::Iconv Boost::locale  Boost::uuid bcrypt.lib
)
elseif(UNIX AND NOT APPLE)
target_link_libraries(${joy_utility_DLL}
  PUBLIC   tinyxml2::tinyxml2 JsonCpp::JsonCpp
  PRIVATE  Iconv::Iconv Boost::locale  Boost::uuid
)
endif()

install(
  TARGETS ${joy_utility_DLL}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install_local_dependencies(TARGETS ${joy_utility_DLL} DIRECTORIES
  ${my_dependency_paths})
