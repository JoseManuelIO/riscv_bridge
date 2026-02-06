# MPC Simple Test

Simplified MPC controller for testing purposes - no external dependencies.

## Description

Lightweight version of the MPC controller (~105 lines) designed for quick testing and debugging without OSQP or other heavy dependencies.

## Features

- No external dependencies
- Fast compilation (<2s)
- Fixed-point arithmetic
- Minimal memory footprint
- Ideal for algorithm validation

## Build and Run

```bash
# Compile and execute
make clean all run

# View generated assembly
make disasm

# Show executable info
make info
```

## Purpose

This test is useful for:
- Validating MPC algorithm logic
- Quick iterations during development
- Testing RISC-V specific optimizations
- Learning MPC basics

## Output

```
MPC_SIMPLE_START
Computing MPC step...
U=0.5,0.2
COST=0.123
MPC_SIMPLE_DONE
```

## Comparison with Full MPC

| Feature | mpc_simple | mpc_acc_controller |
|---------|------------|-------------------|
| Lines of code | ~105 | ~490 |
| Dependencies | None | OSQP |
| Compile time | <2s | ~5s |
| Accuracy | Approximate | High precision |
| Use case | Testing | Production |

## Next Steps

Once this test works, move to the full implementation in `applications/mpc_acc/`.
