#!/bin/bash
# Direct GVSoC test without Python overhead

export PATH=~/PULP/pulp-sdk/install/workstation/bin:$PATH
cd ~/riscv_bridge

echo "=== Compiling MPC ==="
/opt/riscv/bin/riscv32-unknown-elf-gcc -march=rv32imc -mabi=ilp32 -O2 -nostartfiles -Triscv.ld start.S mpc_acc_controller.c -o mpc_acc.elf
if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi
echo "✓ Compiled"

echo ""
echo "=== Running in GVSoC (timeout 30s) ==="
timeout 30s gvsoc --target pulp-open --binary mpc_acc.elf run 2>&1 | grep -E "U=|COST=|ITER=|STATUS=|MPC_" | head -20

echo ""
echo "Exit code: $?"
