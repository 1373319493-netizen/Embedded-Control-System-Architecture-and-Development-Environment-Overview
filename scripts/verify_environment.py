"""Task 1 verification. Writes machine-readable evidence to reports/."""
import json
from datetime import datetime, timezone
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulation.physics_smoke import run_check as physics_check


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, errors='replace', timeout=60)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def minimum_version(command, minimum):
    line = run(command, '--version').splitlines()[0]
    match = re.search(r'(\d+)\.(\d+)', line)
    if not match or tuple(map(int, match.groups())) < minimum:
        raise RuntimeError(f'Version below {minimum}: {line}')
    return line


def compile_arm():
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    obj = build / 'smoke.o'
    run('arm-none-eabi-gcc', '-mcpu=cortex-m3', '-mthumb', '-Wall', '-Werror',
        '-c', str(ROOT / 'firmware' / 'smoke.c'), '-o', str(obj))
    header = run('arm-none-eabi-readelf', '-h', str(obj))
    if 'ARM' not in header or 'ELF32' not in header:
        raise RuntimeError('Expected a 32-bit ARM ELF object')
    return 'Cortex-M3 compilation passed; ELF32 ARM object generated'


def serial_check():
    import serial
    with serial.serial_for_url('loop://', timeout=1) as port:
        data = b'robot-task1\x00\xaa\x55'
        port.write(data)
        if port.read(len(data)) != data:
            raise RuntimeError('Serial loopback mismatch')
    return f'pyserial {serial.VERSION}; binary loopback passed'


def python_check():
    if sys.version_info < (3, 8):
        raise RuntimeError('Python 3.8 or newer is required')
    return platform.python_version()


def main():
    results = []
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    checks = [
        ('ARM GCC', lambda: run('arm-none-eabi-gcc', '--version').splitlines()[0]),
        ('CMake >= 3.20', lambda: minimum_version('cmake', (3, 20))),
        ('QEMU >= 7.0', lambda: minimum_version('qemu-system-arm', (7, 0))),
        ('Python >= 3.8', python_check),
        ('Cortex-M3 compilation', compile_arm),
        ('Serial loopback', serial_check),
        ('PyBullet physics', physics_check),
    ]
    for name, fn in checks:
        try:
            detail, passed = fn(), True
        except Exception as exc:
            detail, passed = str(exc), False
        results.append(dict(check=name, passed=passed, detail=detail))
        print(f'[{"PASS" if passed else "FAIL"}] {name}: {detail}', flush=True)

    machines = None
    machine_error = None
    try:
        machines = run('qemu-system-arm', '-machine', 'help')
        (reports / 'qemu-machines.txt').write_text(machines, encoding='utf-8')
    except Exception as exc:
        machine_error = str(exc)

    exact_gcc = results[0]['passed'] and '10.3-2021.10' in results[0]['detail']
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), results=results,
                  course_gcc_version_matches=exact_gcc,
                  task2_stm32f103_available=None if machines is None else any(
                      line.split()[0] == 'stm32f103' for line in machines.splitlines() if line.split()),
                  qemu_machine_query_error=machine_error)
    (reports / 'task1-verification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if not exact_gcc:
        print('[NOTE] Course GCC 10.3-2021.10 version requirement is not satisfied.')
    return 0 if all(item['passed'] for item in results) else 1


if __name__ == '__main__':
    sys.exit(main())
