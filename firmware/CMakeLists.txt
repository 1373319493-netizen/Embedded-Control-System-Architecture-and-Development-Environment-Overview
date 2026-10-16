cmake_minimum_required(VERSION 3.20)
project(robot_firmware C ASM)
set(CMAKE_C_STANDARD 11)
set(KERNEL ${CMAKE_CURRENT_SOURCE_DIR}/third_party/FreeRTOS-Kernel)
add_executable(firmware src/startup.S src/main.c src/board.c
    ${KERNEL}/tasks.c ${KERNEL}/queue.c ${KERNEL}/list.c
    ${KERNEL}/portable/GCC/ARM_CM3/port.c
    ${KERNEL}/portable/MemMang/heap_4.c)
set_target_properties(firmware PROPERTIES SUFFIX ".elf")
target_include_directories(firmware PRIVATE include ${KERNEL}/include ${KERNEL}/portable/GCC/ARM_CM3)
target_compile_options(firmware PRIVATE -mcpu=cortex-m3 -mthumb -Og -g3
    -ffunction-sections -fdata-sections -Wall -Wextra)
target_link_options(firmware PRIVATE -mcpu=cortex-m3 -mthumb -nostartfiles --specs=nosys.specs
    -T${CMAKE_CURRENT_SOURCE_DIR}/stm32f103rb.ld
    -Wl,--gc-sections,-Map=${CMAKE_CURRENT_BINARY_DIR}/firmware.map)
set_property(TARGET firmware APPEND PROPERTY LINK_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/stm32f103rb.ld)
