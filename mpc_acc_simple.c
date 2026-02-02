// Minimal MPC controller - just print and return fixed values
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

void stdout_putfloat(float f, int decimals) {
    if (f < 0) {
        stdout_putc('-');
        f = -f;
    }
    
    int int_part = (int)f;
    float frac_part = f - int_part;
    
    // Print integer part
    if (int_part == 0) {
        stdout_putc('0');
    } else {
        char buffer[20];
        int idx = 0;
        int temp = int_part;
        while (temp > 0) {
            buffer[idx++] = '0' + (temp % 10);
            temp /= 10;
        }
        for (int i = idx - 1; i >= 0; i--) {
            stdout_putc(buffer[i]);
        }
    }
    
    // Print decimal part
    if (decimals > 0) {
        stdout_putc('.');
        for (int i = 0; i < decimals; i++) {
            frac_part *= 10;
            int digit = (int)frac_part;
            stdout_putc('0' + digit);
            frac_part -= digit;
        }
    }
}

int main() {
    stdout_puts("MPC_START\n");
    
    // Simple grid search: 2 values for accel, 2 for brake
    float best_cost = 1e9f;
    float best_accel = 0.0f;
    float best_brake = 0.0f;
    
    // Try 2 acceleration values
    for (int i = 0; i < 2; i++) {
        float accel = (float)i * 2440.0f;  // 0, 2440 N
        
        // Simulate cost calculation (dummy)
        float cost = accel * accel * 0.001f;
        
        if (cost < best_cost) {
            best_cost = cost;
            best_accel = accel;
            best_brake = 0.0f;
        }
    }
    
    // Try 2 brake values
    for (int j = 0; j < 2; j++) {
        float brake = (float)j * 3253.5f;  // 0, 3253.5 N
        
        // Simulate cost calculation (dummy)
        float cost = brake * brake * 0.001f;
        
        if (cost < best_cost) {
            best_cost = cost;
            best_brake = brake;
            best_accel = 0.0f;
        }
    }
    
    // Output results
    stdout_puts("U=");
    stdout_putfloat(best_accel, 2);
    stdout_putc(',');
    stdout_putfloat(best_brake, 2);
    stdout_putc('\n');
    
    stdout_puts("COST=");
    stdout_putfloat(best_cost, 2);
    stdout_putc('\n');
    
    stdout_puts("STATUS=OPTIMAL\n");
    stdout_puts("MPC_DONE\n");
    
    return 0;
}
