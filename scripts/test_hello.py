#!/usr/bin/env python3
"""Test minimal hello world in GVSoC"""
import subprocess
import sys
import os

def main():
    # Compile hello_minimal.c
    print("=== Compiling hello_minimal ===")
    compile_cmd = [
        "/opt/riscv/bin/riscv32-unknown-elf-gcc",
        "-march=rv32imc", "-mabi=ilp32",
        "-O2", "-nostartfiles",
        "-Triscv.ld",
        "start.S", "hello_minimal.c",
        "-o", "hello_minimal.elf"
    ]
    
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Compilation failed:\n{result.stderr}")
        return 1
    print("Compilation OK")
    
    # Run in GVSoC
    print("\n=== Running in GVSoC ===")
    cmd = [
        "gvsoc",
        "--target", "pulp-open",
        "--binary", "hello_minimal.elf",
        "run"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Work dir: {os.getcwd()}")
    print(f"Binary exists: {os.path.exists('hello_minimal.elf')}")
    print(f"Binary size: {os.path.getsize('hello_minimal.elf')} bytes")
    print("Starting GVSoC (timeout=60s)...\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        print("=== STDOUT ===")
        print(result.stdout)
        print("\n=== STDERR ===")
        print(result.stderr)
        print(f"\n=== Return code: {result.returncode} ===")
        
        # Check for expected output
        if "HELLO_START" in result.stdout and "HELLO_DONE" in result.stdout:
            print("\n✓ Test PASSED - GVSoC execution works!")
            return 0
        else:
            print("\n✗ Test FAILED - Expected output not found")
            return 1
            
    except subprocess.TimeoutExpired:
        print("✗ GVSoC timeout after 60 seconds!")
        print("This suggests GVSoC itself is hanging or extremely slow")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
