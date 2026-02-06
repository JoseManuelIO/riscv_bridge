// Minimal MPC controller with cycle counting
#include <stdint.h>
#include "pmsis.h"

// Direct I/O for reliable output
#define STDOUT_ADDR ((volatile char *)0x1A10F000)
void stdout_putc(char c) { *STDOUT_ADDR = c; }
void stdout_puts(const char *s) { while (*s) stdout_putc(*s++); }

void print_uint(uint32_t val) {
    if (val == 0) {
        stdout_putc('0');
        return;
    }
    char buffer[20];
    int idx = 0;
    while (val > 0) {
        buffer[idx++] = '0' + (val % 10);
        val /= 10;
    }
    for (int i = idx - 1; i >= 0; i--) stdout_putc(buffer[i]);
}

int main() {
    pmsis_init();
    
    stdout_puts("MPC_START\n");
    
    // Read cycle counter
    uint32_t cycles_start, cycles_end;
    __asm__ volatile ("csrr %0, mcycle" : "=r"(cycles_start));

    // Simple MPC computation
    float best_cost = 1e9f;
    float best_accel = 0.0f;
    
    for (int i = 0; i < 2; i++) {
        float accel = (float)i * 2440.0f;
        float cost = accel * accel * 0.001f;
        if (cost < best_cost) {
            best_cost = cost;
            best_accel = accel;
        }
    }

    __asm__ volatile ("csrr %0, mcycle" : "=r"(cycles_end));

    stdout_puts("U=");
    print_uint((uint32_t)best_accel);
    stdout_puts("\nCOST=");
    print_uint((uint32_t)best_cost);
    stdout_puts("\nCYCLES=");
    print_uint(cycles_end - cycles_start);
    stdout_puts("\nMPC_DONE\n");

    pmsis_exit(0);
    return 0;
}
