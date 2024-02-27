function(include_globally)
  # include path for the project globally
  set(oneValueArgs target global_path)
  cmake_parse_arguments("include" "" ${oneValueArgs} "" ${ARGN})
  if(INCLUDE_GLOBALLY)
    message(
      STATUS "Append ${include_target} include path: ${include_global_path}")
    include_directories(${include_global_path})
  endif()
endfunction()
