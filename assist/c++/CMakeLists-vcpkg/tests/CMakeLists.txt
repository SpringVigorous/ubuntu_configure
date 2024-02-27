cmake_minimum_required(VERSION 3.14 FATAL_ERROR)

if(ENABLE_UNIT_TESTS)
  # fatch googletest since 3.11
  include(FetchContent)

  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://gitee.com/mirrors/googletest.git
    GIT_TAG release-1.12.1)

  # For Windows: Prevent overriding the parent project's compiler/linker
  # settings

  set(gtest_force_shared_crt
      ON
      CACHE BOOL "" FORCE)

  FetchContent_MakeAvailable(googletest)

  include(GoogleTest)

  # logger test module
  # add_subdirectory(logger)

endif()
