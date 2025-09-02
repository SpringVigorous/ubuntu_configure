function(ds_copy_file_using copy_title _COPY_SRC_DATA _COPY_DEST_DIR)
  message(STATUS "${copy_title}: ${_COPY_SRC_DATA} -> ${_COPY_DEST_DIR}")

  file(COPY "${_COPY_SRC_DATA}"
    DESTINATION "${_COPY_DEST_DIR}")
endfunction(ds_copy_file_using)