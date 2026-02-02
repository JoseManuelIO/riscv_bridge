#!/bin/bash
# Script para recompilar y probar el controlador MPC

cd ~/riscv_bridge
source .venv/bin/activate
export PATH=~/PULP/pulp-sdk/install/workstation/bin:$PATH

echo "=== Recompilando mpc_acc_controller.c ==="
/opt/riscv/bin/riscv32-unknown-elf-gcc \
  -march=rv32imc -mabi=ilp32 -O2 -nostartfiles \
  -Triscv.ld start.S mpc_acc_controller.c \
  -o mpc_acc.elf

if [ $? -eq 0 ]; then
    echo "✓ Compilación exitosa"
    ls -lh mpc_acc.elf
    echo ""
    echo "=== Probando controlador (timeout 30s) ==="
    timeout 30s python test_mpc_controller.py
else
    echo "✗ Error de compilación"
    exit 1
fi
