/* SPDX-License-Identifier: GPL-2.0-or-later
 * Task-2 STM32F103RB subset for QEMU 7.2.0.
 * Not a complete STM32F103 model: fixed 72 MHz clock, immediate RCC ready
 * flags, GPIO register storage only, USART uses upstream F2 register model.
 */
#include "qemu/osdep.h"
#include "qapi/error.h"
#include "hw/boards.h"
#include "hw/arm/armv7m.h"
#include "hw/arm/boot.h"
#include "hw/char/stm32f2xx_usart.h"
#include "hw/qdev-properties.h"
#include "hw/qdev-properties-system.h"
#include "hw/qdev-clock.h"
#include "exec/address-spaces.h"
#include "sysemu/sysemu.h"

typedef struct {
    MemoryRegion flash, alias, ram, rcc, gpio, flash_regs;
    uint32_t rcc_regs[12], gpio_regs[7], flash_values[9];
} Task2State;

static uint64_t rcc_read(void *opaque, hwaddr offset, unsigned size)
{
    Task2State *s = opaque;
    return offset / 4 < 12 ? s->rcc_regs[offset / 4] : 0;
}

static void rcc_write(void *opaque, hwaddr offset, uint64_t value, unsigned size)
{
    Task2State *s = opaque;
    if (offset / 4 >= 12) {
        return;
    }
    if (offset == 0) {
        /* Oscillator ready flags track enable; no startup delay model. */
        value &= ~((1u << 1) | (1u << 17) | (1u << 25));
        value |= (value & 1) << 1;
        value |= (value & (1u << 16)) << 1;
        value |= (value & (1u << 24)) << 1;
    } else if (offset == 4) {
        value = (value & ~(3u << 2)) | ((value & 3) << 2);
    }
    s->rcc_regs[offset / 4] = value;
}

static uint64_t gpio_read(void *opaque, hwaddr offset, unsigned size)
{
    Task2State *s = opaque;
    return offset / 4 < 7 ? s->gpio_regs[offset / 4] : 0;
}

static void gpio_write(void *opaque, hwaddr offset, uint64_t value, unsigned size)
{
    Task2State *s = opaque;
    if (offset / 4 < 7) {
        s->gpio_regs[offset / 4] = value;
    }
}

static uint64_t flash_read(void *opaque, hwaddr offset, unsigned size)
{
    Task2State *s = opaque;
    return offset / 4 < 9 ? s->flash_values[offset / 4] : 0;
}

static void flash_write(void *opaque, hwaddr offset, uint64_t value, unsigned size)
{
    Task2State *s = opaque;
    if (offset / 4 < 9) {
        s->flash_values[offset / 4] = value;
    }
}

static const MemoryRegionOps rcc_ops = {
    .read = rcc_read, .write = rcc_write, .endianness = DEVICE_LITTLE_ENDIAN,
    .valid = { .min_access_size = 4, .max_access_size = 4 },
};
static const MemoryRegionOps gpio_ops = {
    .read = gpio_read, .write = gpio_write, .endianness = DEVICE_LITTLE_ENDIAN,
    .valid = { .min_access_size = 4, .max_access_size = 4 },
};
static const MemoryRegionOps flash_ops = {
    .read = flash_read, .write = flash_write, .endianness = DEVICE_LITTLE_ENDIAN,
    .valid = { .min_access_size = 4, .max_access_size = 4 },
};

static void task2_init(MachineState *machine)
{
    Task2State *s = g_new0(Task2State, 1);
    MemoryRegion *mem = get_system_memory();
    DeviceState *cpu, *uart;
    Clock *clock = clock_new(OBJECT(machine), "SYSCLK");
    clock_set_hz(clock, 72000000);
    memory_region_init_rom(&s->flash, OBJECT(machine), "f103.flash", 128 * 1024, &error_fatal);
    memory_region_add_subregion(mem, 0x08000000, &s->flash);
    memory_region_init_alias(&s->alias, OBJECT(machine), "f103.boot", &s->flash, 0, 128 * 1024);
    memory_region_add_subregion(mem, 0, &s->alias);
    memory_region_init_ram(&s->ram, OBJECT(machine), "f103.sram", 20 * 1024, &error_fatal);
    memory_region_add_subregion(mem, 0x20000000, &s->ram);
    s->rcc_regs[0] = 0x83;
    s->gpio_regs[0] = s->gpio_regs[1] = 0x44444444;
    memory_region_init_io(&s->rcc, OBJECT(machine), &rcc_ops, s, "f103.rcc.subset", 0x400);
    memory_region_add_subregion(mem, 0x40021000, &s->rcc);
    memory_region_init_io(&s->gpio, OBJECT(machine), &gpio_ops, s, "f103.gpioa.storage", 0x400);
    memory_region_add_subregion(mem, 0x40010800, &s->gpio);
    memory_region_init_io(&s->flash_regs, OBJECT(machine), &flash_ops, s, "f103.flash.storage", 0x400);
    memory_region_add_subregion(mem, 0x40022000, &s->flash_regs);
    cpu = qdev_new(TYPE_ARMV7M);
    qdev_prop_set_uint32(cpu, "num-irq", 60);
    qdev_prop_set_string(cpu, "cpu-type", ARM_CPU_TYPE_NAME("cortex-m3"));
    qdev_prop_set_bit(cpu, "enable-bitband", true);
    qdev_connect_clock_in(cpu, "cpuclk", clock);
    object_property_set_link(OBJECT(cpu), "memory", OBJECT(mem), &error_abort);
    sysbus_realize_and_unref(SYS_BUS_DEVICE(cpu), &error_fatal);
    uart = qdev_new(TYPE_STM32F2XX_USART);
    qdev_prop_set_chr(uart, "chardev", serial_hd(0));
    sysbus_realize_and_unref(SYS_BUS_DEVICE(uart), &error_fatal);
    sysbus_mmio_map(SYS_BUS_DEVICE(uart), 0, 0x40013800);
    sysbus_connect_irq(SYS_BUS_DEVICE(uart), 0, qdev_get_gpio_in(cpu, 37));
    armv7m_load_kernel(ARM_CPU(first_cpu), machine->kernel_filename, 0, 128 * 1024);
}

static void task2_class_init(MachineClass *mc)
{
    mc->desc = "STM32F103RB task2 subset (fixed 72MHz, USART1)";
    mc->init = task2_init;
}
DEFINE_MACHINE("stm32f103-task2", task2_class_init)
