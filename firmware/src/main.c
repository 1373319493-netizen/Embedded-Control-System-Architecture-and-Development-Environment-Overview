#include "FreeRTOS.h"
#include "task.h"
#include "board.h"
static volatile uint32_t worker_count;
static void worker_task(void *arg)
{
 (void)arg; TickType_t last = xTaskGetTickCount();
 for (;;) { xTaskDelayUntil(&last, pdMS_TO_TICKS(100)); ++worker_count; }
}
static void logger_task(void *arg)
{
 (void)arg; TickType_t last = xTaskGetTickCount(); uint32_t count = 0;
 for (;;) {
  xTaskDelayUntil(&last, pdMS_TO_TICKS(500));
  const TickType_t sample_tick = xTaskGetTickCount();
  const uint32_t sample_worker = worker_count;
  console_puts("count="); console_u32(++count);
  console_puts(" tick="); console_u32(sample_tick);
  console_puts(" worker="); console_u32(sample_worker); console_puts("\n");
 }
}
void firmware_assert(const char *file, unsigned line)
{
 taskDISABLE_INTERRUPTS(); console_puts("ERROR "); console_puts(file);
 console_puts(":"); console_u32(line); console_puts("\n"); for (;;) {}
}
void vApplicationMallocFailedHook(void) { firmware_assert("heap exhausted", 0); }
void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{ (void)task; firmware_assert(name, 0); }
void vApplicationIdleHook(void) { __asm volatile("wfi"); }
void fault_handler(void) { firmware_assert("CPU exception", 0); }
int main(void)
{
 board_init(); console_puts("Boot STM32F103RB\n");
 console_puts("FreeRTOS " tskKERNEL_VERSION_NUMBER " CPU=72000000 tick=1000Hz console=USART1 baud=115200\n");
 configASSERT(xTaskCreate(worker_task, "worker", 256, NULL, 2, NULL) == pdPASS);
 configASSERT(xTaskCreate(logger_task, "logger", 256, NULL, 1, NULL) == pdPASS);
 vTaskStartScheduler(); firmware_assert("scheduler returned", 0);
}
