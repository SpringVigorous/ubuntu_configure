set(_proto_apply_model ${ds_proto_TARGET_DLL})

message("---------> protobuf generate")
message("---------> ${_proto_apply_model}")

if(WIN32)
  ADD_CUSTOM_TARGET(proto_generate_cmd
    COMMAND cmd /c ${CMAKE_SOURCE_DIR}/src/ai-sdk/script/proto/proto_generate-component.bat
      ${CMAKE_SOURCE_DIR}/src/ai-sdk/external/vcpkg/installed/x64-windows/tools/protobuf/protoc.exe ${CMAKE_CURRENT_SOURCE_DIR}/src/script ${CMAKE_CURRENT_SOURCE_DIR}/src/model)
  ADD_DEPENDENCIES(${_proto_apply_model} proto_generate_cmd)
else()
  ADD_CUSTOM_TARGET(proto_generate_cmd 
    COMMAND sh ${CMAKE_SOURCE_DIR}/src/ai-sdk/script/proto/proto_generate-component.sh
      ${CMAKE_SOURCE_DIR}/src/ai-sdk/external/vcpkg/installed/x64-linux/tools/protobuf/protoc ${CMAKE_CURRENT_SOURCE_DIR}/src/script ${CMAKE_CURRENT_SOURCE_DIR}/src/model)
  ADD_DEPENDENCIES(${_proto_apply_model} proto_generate_cmd)
endif()

