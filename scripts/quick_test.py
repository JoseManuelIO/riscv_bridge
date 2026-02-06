#!/usr/bin/env python3
"""Quick test of SHARC+GVSoC integration with just 5 steps"""

import sys
sys.path.insert(0, '/home/jmini/riscv_bridge')
from run_sharc_with_gvsoc import run_simulation, plot_results

if __name__ == "__main__":
    print("Quick Test: 5 steps only")
    print()
    results = run_simulation(n_steps=5, dt=0.2, save_results=False)
    print()
    print("Test completed successfully!")
