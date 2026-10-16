# 任务 2：STM32F103RB、FreeRTOS 与 USART1

## 当前结果（2026-10-17）

在本项目自编译的 **QEMU 7.2.0** 上，`stm32f103-task2` 最小模型已通过以下验证：

- FreeRTOS V10.4.6 正常启动，CPU 配置 72 MHz，SysTick 为 1 kHz。
- 100 ms 的 worker 任务与 500 ms 的日志任务正常调度。
- 关闭 semihosting，经 USART1 数据寄存器及 QEMU 串口后端输出日志。
- 最终入口复测连续 9 组样本：count 从 1 到 9，tick 从 500 到 4500，worker 从 5 到 45。
- RCC、GPIOA 和 USART1 共 8 项运行中寄存器检查全部通过。
- 将串口后端设为 null 后，固件仍运行，但标准输出为零字节、无错误输出；固件反汇编中未发现 BKPT 指令。

这完成了任务 2 的最小软件仿真验证。**不是完整 STM32F103 芯片仿真或实体板验收**，也未完成后续双向通信协议、PID、电机或机器人动作。

## 运行

在项目目录中执行：

```text
cmd /c run-task2.cmd --verify
```

持续运行可双击 `run-task2.cmd`，按 Ctrl+C 停止。只编译使用 `--build-only`。

另行检查运行中的初始化寄存器：

```text
python scripts/check_task2_registers.py
```

Python 应使用本机配置中的解释器。当前完整路径为 `D:\Codex\robot-control\work\python-env\Scripts\python.exe`。

模拟器命令：

```text
qemu-system-arm -machine stm32f103-task2 -kernel build/stm32f103/firmware.elf -display none -monitor none -serial stdio
```

没有 `-semihosting` 参数。`config/local.cmd` 中 `QEMU_STM32_BIN` 已指向 `D:\Codex\robot-control\work\tools\qemu-task2\bin`。此前的 xPack legacy 程序仍保留，但任务 2 不再使用它。

## 验证证据

本地 `reports/` 中保存：

| 文件 | 内容 |
|---|---|
| task2-console.txt | 实际 USART1 字符输出 |
| task2-verification.json | 实际程序路径、版本、启动参数及调度样本 |
| task2-qemu-stderr.txt | 模拟器错误输出，本次为空 |
| task2-registers.json | RCC/GPIO/USART 初始化寄存器值与检查结果 |
| task2-register-test-uart.txt | 寄存器检查期间独立串口文件 |
| task2-uart-negative-control.json | 关闭字符输出后端的对照结果 |

USART1 配置：PA9 复用推挽输出，PA10 浮空输入，BRR=625（72 MHz / 115200），CR1=0x200C，CR2=CR3=0，即 115200、8N1、发送与接收使能。这里验证了配置写入和发送字符路径，未验证接收协议。

## 仿真边界

新增板型源码和重建说明位于 `simulation/qemu/`。CPU 固定 72 MHz，RCC 就绪标志立即响应；GPIO 和 Flash 控制寄存器仅保存值。USART 复用上游 F2 寄存器模型，不完整模拟时钟/引脚门控或真实波特率时序。因此寄存器检查与字符传输检查是两项独立证据，不能据此推断所有外设或硬件行为正确。

500 tick 对应 500 ms 客体时间，不保证主机终端每隔精确 500 ms 打印。固件在开始打印前采样 tick 与 worker，避免打印耗时影响采样。

## 来源与构建

- [QEMU 7.2.0 官方源码](https://download.qemu.org/qemu-7.2.0.tar.xz)
- 本地源码包 SHA-256：`5b49ce2687744dad494ae90a898c52204a3406e84d072482a1e1be854eeb2157`
- 新增 `stm32f103-task2` 板型，未将官方 F100 型号改名冒充 F103。
- 同时修复 QEMU 7.2 Meson 在原生 Windows 上提取 trace 文件名时的路径分隔符问题；补丁由 `simulation/qemu/prepare_source.py` 应用。
- 本机源码、依赖与构建脚本在 `work/qemu-build/`；可运行程序和 12 个依赖 DLL 在 `work/tools/qemu-task2/bin/`，校验值在其上级 `sha256.json`。
- 固件仍采用 ARM GCC 14.3.Rel1；任务 1 的指定 GCC 10.3 版本差异没有因此消除。

