#include "board.h"
#include "FreeRTOS.h"
#define REG32(a) (*(volatile uint32_t *)(a))

/* USART1, PA9 TX / PA10 RX, 115200 baud, 8N1 at PCLK2 = 72 MHz. */
void console_puts(const char *text)
{
 while (*text) {
  while (!(REG32(0x40013800UL) & (1UL << 7))) {}
  REG32(0x40013804UL) = (uint8_t)*text++;
 }
}
void console_u32(uint32_t value)
{
 char buffer[11]; unsigned pos = 10; buffer[pos] = 0;
 do { buffer[--pos] = (char)('0' + value % 10); value /= 10; } while (value);
 console_puts(buffer + pos);
}
static void wait_bits(volatile uint32_t *reg, uint32_t mask, uint32_t expected)
{
 for (uint32_t timeout = 2000000; timeout; --timeout)
     if ((*reg & mask) == expected) return;
 firmware_assert("clock timeout", 0);
}
void board_init(void)
{
 REG32(0xE000ED08UL) = 0x08000000UL; /* vector table in flash */
 REG32(0x40022000UL) = 0x12; /* flash prefetch, two wait states */
 REG32(0x40021000UL) |= 1UL << 16; /* HSE = 8 MHz on STM32-P103 */
 wait_bits((volatile uint32_t *)0x40021000UL, 1UL << 17, 1UL << 17);
 /* HSE * 9 -> 72 MHz; APB1 /2, APB2 /1. */
 REG32(0x40021004UL) = (7UL << 18) | (1UL << 16) | (4UL << 8);
 REG32(0x40021000UL) |= 1UL << 24;
 wait_bits((volatile uint32_t *)0x40021000UL, 1UL << 25, 1UL << 25);
 REG32(0x40021004UL) |= 2;
 wait_bits((volatile uint32_t *)0x40021004UL, 3UL << 2, 2UL << 2);
 REG32(0x40021018UL) |= (1UL << 14) | (1UL << 2) | 1UL;
 /* PA9 alternate-function push-pull, PA10 floating input. */
 REG32(0x40010804UL) = (REG32(0x40010804UL) & ~0xFF0UL) | 0x4B0UL;
 REG32(0x4001380CUL) = 0;
 REG32(0x40013808UL) = 625; /* 72000000 / 115200 */
 REG32(0x40013810UL) = 0;
 REG32(0x40013814UL) = 0;
 REG32(0x4001380CUL) = (1UL << 13) | (1UL << 3) | (1UL << 2);
}
