#!/usr/bin/env python3
"""
Direct MPC simulation in Python - NO GVSoC dependency
Fast and fully functional
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class VehicleParams:
    """Vehicle parameters for ACC model"""
    m: float = 2044.0  # mass [kg]
    beta: float = 339.1329  # aerodynamic drag [N]
    gamma: float = 0.77  # rolling resistance [N*s^2/m^2]
    F_accel_max: float = 4880.0  # max accel force [N]
    F_brake_max: float = 6507.0  # max brake force [N]
    dt: float = 0.2  # sample time [s]

class SimpleMPCController:
    """Minimal MPC in pure Python"""
    
    def __init__(self, params: VehicleParams):
        self.params = params
        self.grid_size = 3  # 3 acceleration options + 3 brake options
        
    def vehicle_dynamics(self, x, u, w):
        """
        Single-step vehicle dynamics
        x: [position, headway, velocity]
        u: [F_accel, F_brake]
        w: [v_front]
        """
        p, h, v = x
        v_f = w[0]
        F_a, F_b = u
        
        # Net force
        F_net = F_a - F_b - self.params.beta - self.params.gamma * v**2
        
        # Acceleration
        a = F_net / self.params.m
        
        # Next state
        v_next = v + a * self.params.dt
        v_next = np.clip(v_next, 0, 40)  # Speed limit
        
        p_next = p + v_next * self.params.dt
        h_next = (p_next - p) - v_f * self.params.dt
        
        return np.array([p_next, h_next, v_next])
    
    def cost_function(self, x0, u, w):
        """Evaluate cost for a control input"""
        x = x0.copy()
        
        # Single-step cost
        p, h, v = x
        v_f = w[0]
        F_a, F_b = u
        
        # Comfort cost (penalize jerky control)
        comfort = (F_a + F_b)**2 * 0.001
        
        # Safety cost (penalize small headway)
        safety = 0
        if h < 10:
            safety = (10 - h)**2 * 10
        
        # Efficiency cost (penalize hard acceleration/braking)
        efficiency = (F_a**2 + F_b**2) * 0.0001
        
        return comfort + safety + efficiency
    
    def solve(self, x, w):
        """Solve MPC: find best control"""
        best_cost = 1e9
        best_u = np.array([0.0, 0.0])
        
        accel_values = np.linspace(0, self.params.F_accel_max, self.grid_size)
        brake_values = np.linspace(0, self.params.F_brake_max, self.grid_size)
        
        # Try all combinations (mutual exclusive: either accel OR brake)
        for F_a in accel_values:
            u = np.array([F_a, 0.0])
            cost = self.cost_function(x, u, w)
            if cost < best_cost:
                best_cost = cost
                best_u = u
        
        for F_b in brake_values:
            u = np.array([0.0, F_b])
            cost = self.cost_function(x, u, w)
            if cost < best_cost:
                best_cost = cost
                best_u = u
        
        return best_u, best_cost

def run_simulation(n_steps: int = 30, dt: float = 0.2):
    """Run closed-loop ACC simulation"""
    
    params = VehicleParams(dt=dt)
    controller = SimpleMPCController(params)
    
    # Initial conditions
    x = np.array([0.0, 60.0, 15.0])  # pos=0m, headway=60m, vel=15m/s
    w = np.array([11.0])  # Front vehicle velocity
    
    print("=" * 60)
    print("ACC SIMULATION - PYTHON MPC")
    print("=" * 60)
    print(f"\nInitial state: pos={x[0]:.1f}m, headway={x[1]:.1f}m, vel={x[2]:.1f}m/s")
    print(f"Front vehicle: v_front={w[0]:.1f}m/s")
    print(f"Simulating {n_steps} steps (dt={dt}s, total {n_steps*dt}s)\n")
    print(f"{'Step':<5} {'Time':<7} {'Pos':<8} {'Headway':<10} {'Vel':<8} {'F_accel':<10} {'F_brake':<10} {'Cost':<8}")
    print("-" * 85)
    
    results = {
        'time': [],
        'position': [],
        'headway': [],
        'velocity': [],
        'F_accel': [],
        'F_brake': [],
        'cost': []
    }
    
    # Simulation loop
    for k in range(n_steps):
        t = k * dt
        
        # Compute control
        u, cost = controller.solve(x, w)
        
        # Log results
        results['time'].append(t)
        results['position'].append(x[0])
        results['headway'].append(x[1])
        results['velocity'].append(x[2])
        results['F_accel'].append(u[0])
        results['F_brake'].append(u[1])
        results['cost'].append(cost)
        
        # Print
        print(f"{k:<5} {t:<7.1f} {x[0]:<8.1f} {x[1]:<10.1f} {x[2]:<8.2f} {u[0]:<10.1f} {u[1]:<10.1f} {cost:<8.2e}")
        
        # Update state
        x = controller.vehicle_dynamics(x, u, w)
    
    print("-" * 85)
    print("\n✓ Simulation completed successfully!")
    print(f"Final state: pos={x[0]:.1f}m, headway={x[1]:.1f}m, vel={x[2]:.1f}m/s")
    
    return results

if __name__ == "__main__":
    results = run_simulation(n_steps=30)
