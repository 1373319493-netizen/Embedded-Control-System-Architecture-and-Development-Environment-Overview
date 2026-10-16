#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H
#include <stdint.h>
void firmware_assert(const char *file, unsigned line);
#define configUSE_PREEMPTION 1
#define configCPU_CLOCK_HZ 72000000UL
#define configTICK_RATE_HZ 1000U
#define configMAX_PRIORITIES 5
#define configMINIMAL_STACK_SIZE 128U
#define configTOTAL_HEAP_SIZE (10U * 1024U)
#define configMAX_TASK_NAME_LEN 16
#define configUSE_16_BIT_TICKS 0
#define configIDLE_SHOULD_YIELD 1
#define configUSE_IDLE_HOOK 1
#define configUSE_TICK_HOOK 0
#define configCHECK_FOR_STACK_OVERFLOW 2
#define configUSE_MALLOC_FAILED_HOOK 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configSUPPORT_STATIC_ALLOCATION 0
#define configUSE_MUTEXES 0
#define configUSE_TIMERS 0
#define configUSE_CO_ROUTINES 0
#define configKERNEL_INTERRUPT_PRIORITY 255U
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 160U
#define INCLUDE_vTaskDelay 1
#define INCLUDE_xTaskDelayUntil 1
#define configASSERT(x) do { if (!(x)) firmware_assert(__FILE__, __LINE__); } while (0)
#endif
