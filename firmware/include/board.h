#ifndef BOARD_H
#define BOARD_H
#include <stdint.h>
void board_init(void);
void console_puts(const char *text);
void console_u32(uint32_t value);
#endif
