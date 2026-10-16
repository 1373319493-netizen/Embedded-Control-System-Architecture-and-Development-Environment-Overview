# 嵌入式固件

`smoke.c` 保留用于任务 1 的编译检查。任务 2 已加入可启动的 STM32F103RB 固件。

入口为 `src/main.c`，启动向量在 `src/startup.S`，时钟与 USART1 输出在 `src/board.c`，内存布局在 `stm32f103rb.ld`，FreeRTOS 配置在 `include/FreeRTOSConfig.h`。

采用官方 FreeRTOS V10.4.6、GCC ARM_CM3 端口和 heap_4.c。Flash 128 KiB、RAM 20 KiB、CPU 72 MHz、SysTick 1 kHz。使用 CMake 和 Ninja 编译，产物为 `build/stm32f103/firmware.elf`。

输出使用 USART1（PA9 TX / PA10 RX、115200、8N1），不包含 semihosting 调用。打印前先采样 tick 和 worker，避免串口输出耗时改变同一条记录的采样时刻。使用项目自编译 QEMU 7.2.0 和 `stm32f103-task2` 模型运行；初始化及字符输出已验证，但尚未在实体板验证。完整平台差异见 `docs/task2-stm32f103.md`。
