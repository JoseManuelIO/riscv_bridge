# MPC ACC Controller

Model Predictive Control implementation for Adaptive Cruise Control on RISC-V/PULP platform.

## Description

This is the main application implementing a complete MPC controller with OSQP solver for adaptive cruise control scenarios.

## Features

- Full MPC implementation (~490 lines)
- OSQP quadratic programming solver
- RISC-V optimized
- Command-line interface (stdin/stdout)
- Real-time performance monitoring

## Build and Run

```bash
# Compile
make clean all

# Execute in GVSOC
make run

# With performance statistics
make run-stats
```

## Input/Output Interface

### Input (command line arguments):
- `k`: time step index (int)
- `t`: time in seconds (float)  
- `x`: state vector [position, headway, velocity] (3 floats, comma-separated)
- `w`: exogenous input [v_front, 1.0] (2 floats, comma-separated)

### Output (stdout):
```
U=F_accel,F_brake
COST=value
ITER=count
CYCLES=count
STATUS=status_string
```

## Files

- `mpc_acc_controller.c` - Main implementation
- `Makefile` - Build configuration
- `riscv.ld` - Linker script
- `start.S` - Assembly startup code

## Dependencies

- PULP SDK
- RISC-V toolchain
- OSQP library (included)

## Performance

Typical execution on PULP-open:
- Cycles: ~XXXK
- Time: ~XXms @ 100MHz
- Memory: ~XX KB

See `make run-stats` for detailed profiling.
