# QEMU 7.2.0：任务 2 的 STM32F103RB 最小模型

`stm32f103-task2.c` 是本项目新增的仿真模型，不是 QEMU 官方完整支持的 STM32F103 板型。

覆盖 Cortex-M3、128 KiB Flash（含零地址启动映射）、20 KiB SRAM、72 MHz CPU 时钟、SysTick/NVIC，以及地址 `0x40013800` 的 USART1。USART 复用 QEMU 7.2.0 的 `stm32f2xx_usart` 寄存器模型，字符经 QEMU chardev 输出。固件不使用 semihosting。

## 范围与限制

- CPU 时钟固定为 72 MHz。RCC 的 ready/status 位立即响应，不能验证晶振、PLL 锁定时间或动态改频。
- GPIOA 和 Flash 控制寄存器仅保存值，不能验证引脚电气行为、复用连接或 Flash 写入。
- USART 模型可以验证字符通过数据寄存器和串口后端传输；它不模拟 115200 波特率的实际线路时序，TX 写入也不严格检查 RCC/GPIO/UE/TE 门控。初始化值需另行检查。
- 未实现电机、PWM、编码器、CAN、DMA 或完整 GPIO；本模型不可作为后续运动控制外设的验收依据。
- 不支持本项目新增寄存器的快照迁移或完整系统复位。每次验证重新启动进程。
- 双向通信协议和实体板测试不属于本次串口输出验证。

## 源码准备

使用官方 QEMU 7.2.0 发布源码：
<https://download.qemu.org/qemu-7.2.0.tar.xz>

解压后执行：

```text
python prepare_source.py <qemu-7.2.0源码目录>
```

该脚本增加新板型源码和独立的 Kconfig/Meson 条目，不替换官方 STM32F100 板型。配置时使用 `--target-list=arm-softmmu --without-default-devices`，构建后须在 `-machine help` 中看到 `stm32f103-task2`。

运行方式：

```text
qemu-system-arm -machine stm32f103-task2 -kernel firmware.elf -display none -monitor none -serial stdio
```

在项目 `config/local.cmd` 将 `QEMU_STM32_BIN` 指向自编译程序的目录。验证脚本拒绝 QEMU 版本低于 7 或没有该板型的程序。

新增模型按 GPL-2.0-or-later 提供；QEMU 本身的许可及源文件版权声明以官方源码为准。
