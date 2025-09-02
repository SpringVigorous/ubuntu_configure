# 获取当前构建的git相关信息
macro(ds_get_git_info _git_hash _git_branch _git_commit_date)
    find_package(Git QUIET)

    if(GIT_FOUND)
      execute_process(
        COMMAND ${GIT_EXECUTABLE} log -1 --pretty=format:%h
        OUTPUT_VARIABLE ${_git_hash}
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        WORKING_DIRECTORY
          ${CMAKE_CURRENT_SOURCE_DIR})

      execute_process(
        COMMAND ${GIT_EXECUTABLE} rev-parse --abbrev-ref HEAD
        OUTPUT_VARIABLE ${_git_branch}
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        WORKING_DIRECTORY
          ${CMAKE_CURRENT_SOURCE_DIR})

      execute_process(
        COMMAND ${GIT_EXECUTABLE} log -1 --pretty=format:%ci
        OUTPUT_VARIABLE ${_git_commit_date}
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        WORKING_DIRECTORY
          ${CMAKE_CURRENT_SOURCE_DIR})
    endif(GIT_FOUND)
endmacro(ds_get_git_info)
