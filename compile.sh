#!/bin/bash
# Compilación rápida
cd ~/riscv_bridge
/opt/riscv/bin/riscv32-unknown-elf-gcc -march=rv32imc -mabi=ilp32 -O2 -nostartfiles -Triscv.ld start.S mpc_acc_controller.c -o mpc_acc.elf
echo "✓ Compilado: mpc_acc.elf"
ls -lh mpc_acc.elf
