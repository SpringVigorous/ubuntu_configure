
# import 3rd party deps configured by vcpkg
set(VCPKG_ROOT "${CMAKE_SOURCE_DIR}/src/ai-sdk/external/vcpkg")

# set cmake tool chain
set(CMAKE_TOOLCHAIN_FILE
    ${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake
    CACHE STRING "Vcpkg toolchain file")

set(VCPKG_VERBOSE
    ON
    CACHE BOOL "Vcpkg VCPKG_VERBOSE")