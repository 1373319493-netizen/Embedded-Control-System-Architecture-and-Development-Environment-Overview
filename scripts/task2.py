"""Build and run FreeRTOS using the QEMU 7.2 STM32F103 task2 subset and USART1."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def tool_environment():
    env = os.environ.copy()
    local = ROOT / 'config/local.cmd'
    if local.exists():
        for key, value in re.findall(r'^set "([A-Z0-9_]+)=(.*)"\s*$', local.read_text(), re.M):
            if key in ('ARM_GCC_BIN', 'CMAKE_BIN', 'NINJA_BIN', 'QEMU_STM32_BIN') and value:
                env['PATH'] = value + os.pathsep + env['PATH']
    for tool in ('arm-none-eabi-gcc', 'cmake', 'ninja', 'qemu-system-arm'):
        if not shutil.which(tool, path=env['PATH']):
            raise RuntimeError(f'Missing {tool}. Configure config/local.cmd first.')
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Capture 7 seconds and validate scheduler ticks')
    parser.add_argument('--build-only', action='store_true')
    options = parser.parse_args()
    env = tool_environment()
    build = ROOT / 'build/stm32f103'
    cmake = shutil.which('cmake', path=env['PATH'])
    qemu = shutil.which('qemu-system-arm', path=env['PATH'])
    configure = [cmake, '-S', str(ROOT / 'firmware'), '-B', str(build), '-G', 'Ninja']
    if not (build / 'CMakeCache.txt').exists():
        configure.append('-DCMAKE_TOOLCHAIN_FILE=cmake/arm-gcc.cmake')
    subprocess.run(configure, env=env, check=True, timeout=120)
    subprocess.run([cmake, '--build', str(build)], env=env, check=True, timeout=120)
    if options.build_only:
        return 0
    version = subprocess.check_output([qemu, '--version'], env=env, text=True, timeout=10).splitlines()[0]
    match = re.search(r'version (\d+)\.(\d+)', version)
    if not match or int(match[1]) < 7:
        raise RuntimeError(f'QEMU >= 7 required; got {version}')
    machines = subprocess.check_output([qemu, '-machine', 'help'], env=env, text=True, timeout=10)
    if 'stm32f103-task2' not in machines:
        raise RuntimeError('Configured QEMU lacks stm32f103-task2. See simulation/qemu/README.md.')
    args = [qemu, '-machine', 'stm32f103-task2', '-kernel', str(build / 'firmware.elf'),
            '-display', 'none', '-monitor', 'none', '-serial', 'stdio']
    print(f'{version}\nSTM32F103RB task2 subset / FreeRTOS V10.4.6 / USART1 (semihosting disabled).', flush=True)
    if not options.verify:
        print('Press Ctrl+C to stop.', flush=True)
        process = subprocess.Popen(args, env=env)
        try:
            return process.wait()
        except KeyboardInterrupt:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)
            return 0

    process = subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stopped_by_test = False
    try:
        output, errors = process.communicate(timeout=7)
    except subprocess.TimeoutExpired:
        stopped_by_test = True
        process.terminate()
        output, errors = process.communicate(timeout=10)
    text = output.decode('utf-8', errors='replace').replace('\r', '')
    rows = [tuple(map(int, match)) for match in re.findall(r'count=(\d+) tick=(\d+) worker=(\d+)', text)]
    diagnostics = errors.decode('utf-8', errors='replace')
    passed = (stopped_by_test and 'FreeRTOS V10.4.6' in text and 'console=USART1' in text
              and not diagnostics.strip() and 'ERROR' not in text and len(rows) >= 6
              and all(row == (i, i * 500, i * 5) for i, row in enumerate(rows, 1)))
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    (reports / 'task2-console.txt').write_text(text, encoding='utf-8')
    (reports / 'task2-qemu-stderr.txt').write_text(diagnostics, encoding='utf-8')
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), board='stm32f103-task2',
                  mcu='STM32F103RB subset', kernel='V10.4.6', console='USART1',
                  qemu_version=version, qemu_executable=qemu, command=args,
                  semihosting_enabled=False, uart_verified=passed, scheduler_test_passed=passed, samples=rows,
                  note='500 ticks at 1000 Hz is 500 ms of guest time, not a hardware real-time guarantee.')
    (reports / 'task2-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(text)
    print(diagnostics, end='')
    print('[PASS] STM32F103 subset USART1 and FreeRTOS scheduler' if passed else '[FAIL] USART1/scheduler')
    return 0 if passed else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f'[FAIL] {exc}', file=sys.stderr)
        sys.exit(1)
