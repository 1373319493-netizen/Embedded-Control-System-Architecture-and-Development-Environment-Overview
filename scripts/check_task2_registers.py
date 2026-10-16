"""Inspect guest initialization through QMP, with UART on a separate file."""
import json
import re
import shutil
import subprocess
import time
import threading
import queue
from task2 import ROOT, tool_environment


def main():
    env = tool_environment()
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    uart = reports / 'task2-register-test-uart.txt'
    args = [shutil.which('qemu-system-arm', path=env['PATH']),
            '-machine', 'stm32f103-task2', '-kernel', str(ROOT/'build/stm32f103/firmware.elf'),
            '-display', 'none', '-monitor', 'none', '-qmp', 'stdio',
            '-serial', f'file:{uart}', '-S']
    process = subprocess.Popen(args, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    checks = [
        ('RCC_CR', 0x40021000, 0x03030003, 0x03030003),
        ('RCC_CFGR', 0x40021004, 0x003FFFFF, 0x001D040A),
        ('RCC_APB2ENR', 0x40021018, 0x4005, 0x4005),
        ('GPIOA_CRH', 0x40010804, 0xFF0, 0x4B0),
        ('USART1_BRR', 0x40013808, 0xFFFF, 625),
        ('USART1_CR1', 0x4001380C, 0xFFFF, 0x200C),
        ('USART1_CR2', 0x40013810, 0xFFFF, 0),
        ('USART1_CR3', 0x40013814, 0xFFFF, 0),
    ]
    replies = queue.Queue()
    def reader():
        for line in process.stdout:
            replies.put(json.loads(line))
        replies.put({'closed': True})
    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    def request(command, **kw):
        ident = kw.setdefault('id', command)
        process.stdin.write(json.dumps(dict(execute=command, **kw)) + '\n')
        process.stdin.flush()
        deadline = time.monotonic() + 10
        while True:
            message = replies.get(timeout=max(0.01, deadline-time.monotonic()))
            if message.get('closed') or 'error' in message:
                raise RuntimeError(message)
            if message.get('id') == ident:
                return message
    values = {}
    try:
        request('qmp_capabilities')
        request('cont')
        time.sleep(3)
        request('stop')
        for name, address, _, _ in checks:
            message = request('human-monitor-command', id=name,
                              arguments={'command-line': f'xp /1wx 0x{address:x}'})
            match = re.search(r':\s+0x([0-9a-fA-F]+)', message.get('return', ''))
            if match:
                values[name] = int(match[1], 16)
        request('quit')
        process.wait(timeout=10)
        thread.join(timeout=2)
        errors = process.stderr.read()
    except BaseException:
        process.kill()
        process.wait(timeout=10)
        raise
    results = [dict(register=name, address=hex(address), value=values.get(name),
                    expected=expected, mask=mask,
                    passed=name in values and values[name] & mask == expected)
               for name, address, mask, expected in checks]
    passed = process.returncode == 0 and not errors.strip() and all(r['passed'] for r in results)
    passed = passed and 'console=USART1' in uart.read_text() and 'count=1' in uart.read_text()
    (reports/'task2-registers.json').write_text(json.dumps(dict(passed=passed, checks=results, stderr=errors), indent=2))
    print(json.dumps(results, indent=2))
    print('[PASS] USART1 initialization registers' if passed else '[FAIL] USART1 initialization registers')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
