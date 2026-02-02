#!/usr/bin/env python3
"""
Python wrapper to call MPC controller in GVSoC and parse results
"""

import subprocess
import re
import numpy as np
import os

class GVSoCMPCController:
    def __init__(self, work_dir="~/riscv_bridge", cpu_freq=50_000_000):
        self.work_dir = os.path.expanduser(work_dir)
        self.cpu_freq = cpu_freq
        self.gapy_path = os.path.expanduser("~/PULP/pulp-sdk/install/workstation/bin/gapy")
        self.target_dir = os.path.expanduser("~/PULP/pulp-sdk/install/workstation/generators")
        self.model_dir = os.path.expanduser("~/PULP/pulp-sdk/install/workstation/models")
        self.binary_path = os.path.join(self.work_dir, "mpc_acc.elf")
        self.u_prev = np.array([[0.0], [0.0]])  # Track previous control
        
    def compute_control(self, k, t, x, w):
        """
        Compute MPC control by calling GVSoC
        
        Args:
            k: time step index (int)
            t: time in seconds (float)
            x: state vector (3x1 numpy array) [position, headway, velocity]
            w: exogenous input (2x1 numpy array) [v_front, constant]
            
        Returns:
            u: control vector (2x1 numpy array) [F_accel, F_brake]
            metadata: dict with solver info
        """
        
        # Format arguments
        x_str = f"{x[0,0]},{x[1,0]},{x[2,0]}"
        w_str = f"{w[0,0]},{w[1,0]}"
        
        # Build command (currently no arguments as GVSoC doesn't pass them correctly)
        cmd = [
            "gvsoc",
            "--target", "pulp-open",
            "--binary", self.binary_path,
            "run"
        ]
        
        # Execute GVSoC
        print(f"DEBUG: Executing command: {' '.join(cmd)}")
        print(f"DEBUG: Work dir: {self.work_dir}")
        print(f"DEBUG: Binary exists: {os.path.exists(self.binary_path)}")
        
        try:
            print("DEBUG: Starting subprocess.run...")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=300,
                cwd=self.work_dir
            )
            print(f"DEBUG: subprocess.run completed")
            print(f"DEBUG: Return code: {result.returncode}")
            output = result.stdout
            
            # DEBUG: Print GVSoC output
            print("\n=== GVSoC Output ===")
            print(output)
            print("=== End GVSoC Output ===\n")
            
        except subprocess.TimeoutExpired as e:
            print(f"DEBUG: Timeout expired after {e.timeout} seconds")
            raise RuntimeError("GVSoC execution timed out")
        except Exception as e:
            print(f"DEBUG: Exception caught: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to execute GVSoC: {e}")
        
        # Parse output
        u, metadata = self._parse_output(output)
        
        # Calculate delay from cycles
        metadata['t_delay'] = metadata['cycles'] / self.cpu_freq if metadata['cycles'] > 0 else 0.003
        
        self.u_prev = u
        
        return u, metadata
    
    def _parse_output(self, output):
        """Parse GVSoC stdout to extract control and metadata"""
        
        # Extract U vector
        u_match = re.search(r'U=([\d.,-]+)', output)
        if not u_match:
            print("ERROR: Could not find U= in output:")
            print(output)
            raise ValueError("No U= found in GVSoC output")
        
        u_str = u_match.group(1)
        u_vals = [float(x) for x in u_str.split(',')]
        u = np.array([[u_vals[0]], [u_vals[1]]])
        
        # Extract metadata
        metadata = {}
        
        cost_match = re.search(r'COST=([\d.e+-]+)', output)
        if cost_match:
            metadata['cost'] = float(cost_match.group(1))
        else:
            metadata['cost'] = 0.0
        
        iter_match = re.search(r'ITER=(\d+)', output)
        if iter_match:
            metadata['iterations'] = int(iter_match.group(1))
        else:
            metadata['iterations'] = 0
        
        cycles_match = re.search(r'CYCLES=(\d+)', output)
        if cycles_match:
            metadata['cycles'] = int(cycles_match.group(1))
        else:
            metadata['cycles'] = 150000  # Default estimate
        
        status_match = re.search(r'STATUS=(\w+)', output)
        if status_match:
            metadata['status'] = status_match.group(1)
        else:
            metadata['status'] = 'UNKNOWN'
        
        metadata['solver_status'] = 1 if metadata['status'] == 'OPTIMAL' else 0
        metadata['solver_status_msg'] = metadata['status']
        metadata['is_feasible'] = (metadata['status'] == 'OPTIMAL')
        
        return u, metadata


def test_controller():
    """Test the MPC controller with sample data"""
    
    print("=== Testing GVSoC MPC Controller ===\n")
    
    controller = GVSoCMPCController()
    
    # Test case: ego at 15 m/s, leader at 11 m/s, 60m apart
    k = 0
    t = 0.0
    x = np.array([[0.0],    # position
                  [60.0],   # headway
                  [15.0]])  # velocity
    w = np.array([[11.0],   # v_front
                  [1.0]])   # constant
    
    print(f"Input state:")
    print(f"  k = {k}")
    print(f"  t = {t} s")
    print(f"  x = [pos={x[0,0]:.1f}m, headway={x[1,0]:.1f}m, vel={x[2,0]:.1f}m/s]")
    print(f"  w = [v_front={w[0,0]:.1f}m/s, const={w[1,0]}]")
    print()
    
    # Compute control
    u, metadata = controller.compute_control(k, t, x, w)
    
    print(f"Output control:")
    print(f"  u = [F_accel={u[0,0]:.2f}N, F_brake={u[1,0]:.2f}N]")
    print()
    print(f"Metadata:")
    print(f"  Cost: {metadata['cost']:.2f}")
    print(f"  Iterations: {metadata['iterations']}")
    print(f"  Cycles: {metadata['cycles']}")
    print(f"  Delay: {metadata['t_delay']*1000:.2f} ms")
    print(f"  Status: {metadata['status']}")
    print()
    
    # Physical interpretation
    mass = 2044.0  # kg
    F_friction = 339.1329 + 0.77 * x[2,0]**2
    F_net = u[0,0] - u[1,0] - F_friction
    a = F_net / mass
    
    print(f"Physical interpretation:")
    print(f"  F_friction = {F_friction:.2f} N")
    print(f"  F_net = {F_net:.2f} N")
    print(f"  Acceleration = {a:.3f} m/s²")
    
    if a > 0:
        print(f"  → Vehicle will ACCELERATE")
    elif a < -0.1:
        print(f"  → Vehicle will DECELERATE")
    else:
        print(f"  → Vehicle will maintain speed")


if __name__ == "__main__":
    test_controller()
