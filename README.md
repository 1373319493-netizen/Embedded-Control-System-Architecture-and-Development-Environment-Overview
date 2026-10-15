# 六轴工业机器人嵌入式控制开发环境

本项目记录六轴机器人嵌入式运动控制课程的开发与验证过程。目前完成任务 1 的可用环境配置与验证，包含 Cortex-M3 编译检查、Python 串口回环和 PyBullet 物理测试。

**当前使用 ARM GCC 14.3.Rel1 兼容方案，尚未严格满足课件固定的 10.3-2021.10 版本要求。** 项目还没有实现 FreeRTOS 固件、六轴机械臂运动控制或 QEMU 双向通信。

## 项目结构

```text
config/local.example.cmd      本机工具路径配置模板
docs/task1-validation.md      已验证版本、结果与限制
firmware/smoke.c              Cortex-M3 编译测试源码
scripts/verify_environment.py 环境检查及报告生成
simulation/physics_smoke.py   无窗口物理仿真测试
open-dev-terminal.cmd        Windows 开发终端入口
requirements.txt             Python 依赖版本
```

`build/`、`reports/` 是自动生成的本地目录，不提交。工具安装包、虚拟环境、PyCharm 个人设置和本机路径也不提交。

## 在当前电脑使用

当前电脑已生成 `config/local.cmd`，指向已经安装好的工具和 Python 环境。

双击 `open-dev-terminal.cmd`，在弹出的终端运行：

```text
python scripts\verify_environment.py
```

也可以直接运行 `open-dev-terminal.cmd --verify`。7 项检查应显示 `[PASS]`，另有一条指定 GCC 版本不匹配的提示。结果写入 `reports/task1-verification.json`。

仅验证 Python 仿真：

```text
python simulation\physics_smoke.py
```

该脚本在后台模拟一个小方块落到地面，正常时打印最终高度约 0.025 米，不会弹出机器人图形窗口。

## 使用 PyCharm

1. 在 PyCharm 中打开本仓库文件夹。
2. 选择已有 Python 解释器。当前电脑的解释器位置可在 `config/local.cmd` 的 `ROBOT_PYTHON_DIR` 中找到，在目录末尾添加 `python.exe` 即可。
3. Python 脚本可以直接运行，例如 `simulation/physics_smoke.py`。
4. 要验证完整工具链，在 PyCharm 底部终端输入 `cmd /c open-dev-terminal.cmd --verify`。这样检查程序会加载本机 ARM、QEMU 等工具路径。
5. 要持续使用包含这些工具的命令行，输入 `cmd /c open-dev-terminal.cmd`。

仅选择 Python 解释器不会自动配置 ARM 编译器或 QEMU 的 PATH。

## 在另一台 Windows 电脑配置

1. 安装 ARM GNU 嵌入式工具链、CMake ≥3.20、QEMU ≥7.0 和 Python ≥3.8。此项目实际验证的 Python 为 64 位 3.10。
2. 创建独立 Python 环境并安装依赖：

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

3. 将 `config/local.example.cmd` 复制为 `config/local.cmd`，填写本机工具目录。`ROBOT_PYTHON_DIR` 应填写虚拟环境的 `Scripts` 目录。若工具已经在 PATH 中，对应值可以留空。
4. 双击终端入口，运行环境检查。

PyBullet 在本次 Windows 安装中需要从源码构建，使用了 Visual Studio C++ 工具。路径过长会导致构建失败，可将配置中的 `ROBOT_TEMP` 指向已创建的较短临时目录。不要直接复制其他电脑的虚拟环境。

## 后续开发

- 任务 2：确定 QEMU 实际支持的板型，搭建 FreeRTOS 基础固件。
- 任务 3：加载六轴机器人模型，验证关节状态和运动。
- 任务 4：实现通信协议及双向链路验证。

当前 QEMU 不包含课件所用的 `stm32f103` 板型。详细情况见 [任务 1 验证记录](docs/task1-validation.md)。

## GitHub 同步

远程仓库已配置为本项目的 GitHub 地址，分支为 `main`。双击 `sync-github.cmd` 会推送已经提交的改动，如需登录，按 GitHub 凭据管理器提示操作。

该脚本不会自动提交新修改。后续在 PyCharm 中检查改动并 Commit 后，再 Push 或运行同步脚本。同步是手动触发的，不会自动上传每次保存。

若本机 Git 的代理配置已失效，脚本会仅对这次推送关闭 Git HTTP 代理，不修改系统代理。需要代理联网时，应按实际网络情况调整此设置。

## 官方资料

- [ARM 工具链](https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain)
- [CMake](https://cmake.org/)
- [QEMU 下载](https://www.qemu.org/download/)
- [pyserial](https://pypi.org/project/pyserial/)
- [PyBullet](https://pypi.org/project/pybullet/)
