#!/bin/bash
cd ~/riscv_bridge
source .venv/bin/activate
echo "=== Testing MPC Controller in GVSoC ==="
echo ""
python test_mpc_controller.py
