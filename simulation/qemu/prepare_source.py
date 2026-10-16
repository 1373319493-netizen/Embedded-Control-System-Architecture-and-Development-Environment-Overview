"""Add the task2 machine to an extracted, unmodified QEMU 7.2.0 source tree."""
from pathlib import Path
import shutil
import sys

source = Path(sys.argv[1]).resolve()
if (source / 'VERSION').read_text().strip() != '7.2.0':
    raise SystemExit('Expected upstream QEMU 7.2.0 source')
shutil.copyfile(Path(__file__).with_name('stm32f103-task2.c'), source / 'hw/arm/stm32f103-task2.c')
changes = {
    'configs/devices/arm-softmmu/default.mak': 'CONFIG_STM32F103_TASK2=y\n',
    'hw/arm/meson.build': "arm_ss.add(when: 'CONFIG_STM32F103_TASK2', if_true: files('stm32f103-task2.c'))\n",
    'hw/arm/Kconfig': 'config STM32F103_TASK2\n    bool\n    default y\n    select ARM_V7M\n    select STM32F2XX_USART\n',
}
for name, addition in changes.items():
    path = source / name
    text = path.read_text()
    if addition not in text:
        path.write_text(text + '\n' + addition)
print('Task2 machine added')
trace = source / 'trace/meson.build'
trace.write_text(trace.read_text().replace("item.full_path().split('/')[-1].underscorify()",
                                          'fs.name(item.full_path()).underscorify()'))
