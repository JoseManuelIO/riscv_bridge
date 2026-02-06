// Minimal test - just print and exit
#include <stdint.h>

#define STDOUT_ADDR ((volatile char *)0x1A10F000)

void stdout_putc(char c) {
    *STDOUT_ADDR = c;
}

void stdout_puts(const char *s) {
    while (*s) {
        stdout_putc(*s++);
    }
}

int main() {
    stdout_puts("HELLO_START\n");
    stdout_puts("Testing GVSoC minimal execution\n");
    stdout_puts("HELLO_DONE\n");
    return 0;
}
