#!/usr/bin/env python3
"""
SHARC + GVSoC MPC Integration
Closed-loop simulation with RISC-V MPC controller running in GVSoC
"""

import subprocess
import re
import numpy as np
import os
import json
from pathlib import Path

class GVSoCMPCController:
    """MPC Controller executing in GVSoC RISC-V simulator"""
    
    def __init__(self, work_dir="~/riscv_bridge", cpu_freq=50_000_000):
        self.work_dir = os.path.expanduser(work_dir)
        self.cpu_freq = cpu_freq
        self.gapy_path = os.path.expanduser("~/PULP/pulp-sdk/install/workstation/bin/gapy")
        self.target_dir = os.path.expanduser("~/PULP/pulp-sdk/install/workstation/generators")
        self.model_dir = os.path.expanduser("~/PULP/pulp-sdk/install/workstation/models")
        self.binary_path = os.path.join(self.work_dir, "mpc_acc.elf")
        
    def compute_control(self, k, t, x, w):
        """
        Compute MPC control by calling GVSoC
        
        Args:
            k: time step index
            t: time in seconds
            x: state [position, headway, velocity]
            w: exogenous input [v_front, constant]
            
        Returns:
            u: control [F_accel, F_brake]
            metadata: solver info dict
        """
        
        # Build GVSoC command
        cmd = [
            self.gapy_path,
            "--target-dir", self.target_dir,
            "--target", "pulp-open",
            "--platform", "gvsoc",
            "--model-dir", self.model_dir,
            "--binary", self.binary_path,
            "--work-dir", self.work_dir,
            "run"
        ]
        
        # Execute GVSoC
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=120,
                cwd=self.work_dir
            )
            output = result.stdout
        except subprocess.TimeoutExpired:
            print("WARNING: GVSoC timeout, using default control")
            return np.array([[0.0], [0.0]]), {'cost': 0, 'iterations': 0, 'cycles': 0, 't_delay': 0.003}
        except Exception as e:
            print(f"WARNING: GVSoC error: {e}, using default control")
            return np.array([[0.0], [0.0]]), {'cost': 0, 'iterations': 0, 'cycles': 0, 't_delay': 0.003}
        
        # Parse output
        u, metadata = self._parse_output(output)
        
        # Calculate delay from cycles
        metadata['t_delay'] = max(0.001, metadata['cycles'] / self.cpu_freq) if metadata['cycles'] > 0 else 0.003
        
        return u, metadata
    
    def _parse_output(self, output):
        """Parse GVSoC stdout"""
        
        # Extract U vector
        u_match = re.search(r'U=([\d.,-]+)', output)
        if not u_match:
            print(f"WARNING: No U= in output, using default")
            return np.array([[0.0], [0.0]]), {'cost': 0, 'iterations': 0, 'cycles': 150000}
        
        u_str = u_match.group(1)
        u_vals = [float(x) for x in u_str.split(',')]
        u = np.array([[u_vals[0]], [u_vals[1]]])
        
        # Extract metadata
        metadata = {}
        
        cost_match = re.search(r'COST=([\d.e+-]+)', output)
        metadata['cost'] = float(cost_match.group(1)) if cost_match else 0.0
        
        iter_match = re.search(r'ITER=(\d+)', output)
        metadata['iterations'] = int(iter_match.group(1)) if iter_match else 0
        
        cycles_match = re.search(r'CYCLES=(\d+)', output)
        metadata['cycles'] = int(cycles_match.group(1)) if cycles_match else 150000
        
        status_match = re.search(r'STATUS=(\w+)', output)
        metadata['status'] = status_match.group(1) if status_match else 'UNKNOWN'
        
        return u, metadata


class ACCDynamics:
    """ACC Vehicle Dynamics Model"""
    
    def __init__(self):
        self.mass = 2044.0  # kg
        self.beta = 339.1329  # N
        self.gamma = 0.77  # N·s²/m²
        
    def derivative(self, t, x, u, w):
        """
        Compute dx/dt
        
        x: [position, headway, velocity]
        u: [F_accel, F_brake]
        w: [v_front, constant]
        """
        p, h, v = x[0,0], x[1,0], x[2,0]
        F_accel, F_brake = u[0,0], u[1,0]
        v_front = w[0,0]
        
        # Friction force
        F_friction = self.beta + self.gamma * v * v
        
        # Acceleration
        a = (F_accel - F_brake - F_friction) / self.mass
        
        # Derivatives
        dpdt = v
        dhdt = v_front - v
        dvdt = a
        
        return np.array([[dpdt], [dhdt], [dvdt]])
    
    def integrate_euler(self, t, x, u, w, dt):
        """Simple Euler integration"""
        dxdt = self.derivative(t, x, u, w)
        x_new = x + dxdt * dt
        
        # Apply constraints
        x_new[2,0] = max(0.0, min(20.0, x_new[2,0]))  # velocity limits
        x_new[1,0] = max(0.0, x_new[1,0])  # headway >= 0
        
        return x_new


def compute_v_front(t):
    """Leader vehicle velocity profile"""
    import math
    return 11.0 + 2.0*math.sin(t) + 1.0*math.sin(3.23*t) + 0.4*math.sin(12.1*t)


def run_simulation(n_steps=30, dt=0.2, save_results=True):
    """
    Run closed-loop simulation with GVSoC MPC
    
    Args:
        n_steps: number of time steps
        dt: sample time (seconds)
        save_results: whether to save results to JSON
    """
    
    print("="*60)
    print("SHARC + GVSoC MPC Closed-Loop Simulation")
    print("="*60)
    print()
    
    # Initialize controller and dynamics
    controller = GVSoCMPCController()
    dynamics = ACCDynamics()
    
    # Initial conditions
    x = np.array([[0.0],    # position
                  [60.0],   # headway
                  [15.0]])  # velocity
    u = np.array([[0.0], [0.0]])  # control
    
    # Storage
    results = {
        'time': [],
        'position': [],
        'headway': [],
        'velocity': [],
        'v_front': [],
        'F_accel': [],
        'F_brake': [],
        'cost': [],
        'iterations': [],
        'cycles': [],
        'delay': []
    }
    
    print(f"Initial state: pos={x[0,0]:.1f}m, headway={x[1,0]:.1f}m, vel={x[2,0]:.1f}m/s")
    print(f"Simulating {n_steps} steps with dt={dt}s (total {n_steps*dt:.1f}s)")
    print()
    
    # Simulation loop
    for k in range(n_steps):
        t = k * dt
        
        # Compute leader velocity
        v_front = compute_v_front(t)
        w = np.array([[v_front], [1.0]])
        
        # Call MPC controller in GVSoC
        print(f"Step {k:3d} (t={t:5.1f}s): ", end='', flush=True)
        u, metadata = controller.compute_control(k, t, x, w)
        
        # Store results
        results['time'].append(t)
        results['position'].append(x[0,0])
        results['headway'].append(x[1,0])
        results['velocity'].append(x[2,0])
        results['v_front'].append(v_front)
        results['F_accel'].append(u[0,0])
        results['F_brake'].append(u[1,0])
        results['cost'].append(metadata['cost'])
        results['iterations'].append(metadata['iterations'])
        results['cycles'].append(metadata['cycles'])
        results['delay'].append(metadata['t_delay'])
        
        # Print step info
        print(f"v={x[2,0]:5.1f} m/s, h={x[1,0]:5.1f}m, v_f={v_front:5.1f} m/s | " +
              f"u=[{u[0,0]:6.1f}, {u[1,0]:6.1f}] N | " +
              f"cost={metadata['cost']:8.1f}, cycles={metadata['cycles']}")
        
        # Apply control and integrate dynamics
        x = dynamics.integrate_euler(t, x, u, w, dt)
    
    print()
    print("="*60)
    print("Simulation Complete!")
    print("="*60)
    print()
    
    # Summary statistics
    avg_vel = np.mean(results['velocity'])
    min_headway = np.min(results['headway'])
    max_brake = np.max(results['F_brake'])
    avg_cycles = np.mean([c for c in results['cycles'] if c > 0])
    avg_delay = np.mean([d for d in results['delay'] if d > 0])
    
    print("Summary:")
    print(f"  Average velocity:     {avg_vel:.2f} m/s")
    print(f"  Minimum headway:      {min_headway:.2f} m")
    print(f"  Maximum braking:      {max_brake:.1f} N")
    print(f"  Average CPU cycles:   {avg_cycles:.0f}")
    print(f"  Average delay:        {avg_delay*1000:.2f} ms")
    print()
    
    # Save results
    if save_results:
        output_file = os.path.expanduser("~/riscv_bridge/simulation_results.json")
        with open(output_file, 'w') as f:
            # Convert numpy types to native Python types
            results_serializable = {
                k: [float(v) if isinstance(v, (np.floating, np.integer)) else v for v in vals]
                for k, vals in results.items()
            }
            json.dump(results_serializable, f, indent=2)
        print(f"Results saved to: {output_file}")
        print()
    
    return results


def plot_results(results):
    """Generate ASCII plots of results"""
    
    print("="*60)
    print("Results Visualization")
    print("="*60)
    print()
    
    # Velocity plot
    print("Velocity (m/s):")
    vel = results['velocity']
    v_front = results['v_front']
    max_v = max(max(vel), max(v_front))
    min_v = min(min(vel), min(v_front))
    
    for v_val in np.linspace(max_v, min_v, 10):
        line = f"{v_val:5.1f} |"
        for i in range(len(vel)):
            if i % 3 == 0:  # Sample every 3rd point
                if abs(vel[i] - v_val) < (max_v - min_v) / 20:
                    line += "*"
                elif abs(v_front[i] - v_val) < (max_v - min_v) / 20:
                    line += "."
                else:
                    line += " "
        print(line)
    print("      +" + "-"*(len(vel)//3))
    print("       0" + " "*((len(vel)//6)-1) + f"{len(vel)*0.2/2:.0f}s" + " "*((len(vel)//6)-1) + f"{len(vel)*0.2:.0f}s")
    print("       (* = ego, . = leader)")
    print()
    
    # Braking force
    print("Braking Force (N):")
    brake = results['F_brake']
    max_brake = max(brake) if max(brake) > 0 else 1000
    
    for b_val in np.linspace(max_brake, 0, 8):
        line = f"{b_val:6.0f} |"
        for i in range(len(brake)):
            if i % 3 == 0:
                if brake[i] >= b_val:
                    line += "#"
                else:
                    line += " "
        print(line)
    print("       +" + "-"*(len(brake)//3))
    print()


if __name__ == "__main__":
    # Run simulation
    results = run_simulation(n_steps=30, dt=0.2, save_results=True)
    
    # Visualize
    plot_results(results)
    
    print("Simulation data available in 'results' variable")
    print("To re-plot: plot_results(results)")
