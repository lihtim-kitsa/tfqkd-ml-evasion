import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import os
import sys

# Physics-Informed Neural Network (PINN) for the Lang-Kobayashi Digital Twin
class PINN_DigitalTwin(nn.Module):
    def __init__(self):
        super().__init__()
        # Input: time t, Output: State (E, phi, N)
        self.net = nn.Sequential(
            nn.Linear(1, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 3)
        )
        
        # Nominal Physics Parameters
        self.kappa = 1e9
        self.alpha = 3.0
        self.gamma = 1e11
        self.delta_omega = 0.0
        self.g0 = 1.2e11
        self.N_tr = 1e8
        self.tau_e = 1e-9
        self.base_I = 2.0e17

    def forward(self, t):
        return self.net(t)

    def pde_residual(self, t, E_ref_func, current_func):
        t.requires_grad_(True)
        y = self.net(t)
        
        E = y[:, 0:1]
        phi = y[:, 1:2]
        N = y[:, 2:3]
        
        # Compute derivatives using autograd
        dE_dt = torch.autograd.grad(E, t, grad_outputs=torch.ones_like(E), create_graph=True)[0]
        dphi_dt = torch.autograd.grad(phi, t, grad_outputs=torch.ones_like(phi), create_graph=True)[0]
        dN_dt = torch.autograd.grad(N, t, grad_outputs=torch.ones_like(N), create_graph=True)[0]
        
        # Physical Inputs
        E_ref = E_ref_func(t)
        phi_ref = torch.zeros_like(t) # Base phase
        I_inj = current_func(t)
        
        # Governing equations
        G = self.g0 * (N - self.N_tr) / self.N_tr
        
        eq_E = 0.5 * (G - self.gamma) * E + self.kappa * E_ref * torch.cos(phi_ref - phi)
        eq_phi = 0.5 * self.alpha * (G - self.gamma) - self.delta_omega + self.kappa * (E_ref / (E + 1e-12)) * torch.sin(phi_ref - phi)
        eq_N = I_inj - N / self.tau_e - G * E**2
        
        # Residuals
        res_E = dE_dt - eq_E
        res_phi = dphi_dt - eq_phi
        res_N = dN_dt - eq_N
        
        return torch.mean(res_E**2 + res_phi**2 + res_N**2)

def evaluate_pinn_anomaly_score(pinn, t_data, E_data, phi_data, N_data):
    """
    Given a trained PINN and observed telemetry data, compute the Physics Residual.
    If the real hardware was attacked, the standard physics residual will SPIKE.
    """
    pinn.eval()
    t_tensor = torch.tensor(t_data, dtype=torch.float32).unsqueeze(1)
    
    # Nominal expectations
    E_ref_func = lambda t: torch.ones_like(t)
    current_func = lambda t: pinn.base_I * (1.0 + 0.01 * torch.sin(2 * np.pi * 1e5 * t))
    
    # Actually, the anomaly score is the PDE residual of the OBSERVED data
    # not the network output. We check if the data obeys the equations!
    t_tensor.requires_grad_(True)
    
    # We can use finite differences for the data derivatives
    dt = t_data[1] - t_data[0]
    dE_dt = np.gradient(E_data) / dt
    dphi_dt = np.gradient(phi_data) / dt
    dN_dt = np.gradient(N_data) / dt
    
    # Convert to tensors
    E = torch.tensor(E_data, dtype=torch.float32)
    phi = torch.tensor(phi_data, dtype=torch.float32)
    N = torch.tensor(N_data, dtype=torch.float32)
    dE_dt = torch.tensor(dE_dt, dtype=torch.float32)
    dphi_dt = torch.tensor(dphi_dt, dtype=torch.float32)
    dN_dt = torch.tensor(dN_dt, dtype=torch.float32)
    
    t = torch.tensor(t_data, dtype=torch.float32)
    E_ref = torch.ones_like(E)
    phi_ref = torch.zeros_like(E)
    I_inj = pinn.base_I * (1.0 + 0.01 * torch.sin(2 * np.pi * 1e5 * t))
    
    G = pinn.g0 * (N - pinn.N_tr) / pinn.N_tr
    
    eq_E = 0.5 * (G - pinn.gamma) * E + pinn.kappa * E_ref * torch.cos(phi_ref - phi)
    eq_phi = 0.5 * pinn.alpha * (G - pinn.gamma) - pinn.delta_omega + pinn.kappa * (E_ref / (E + 1e-12)) * torch.sin(phi_ref - phi)
    eq_N = I_inj - N / pinn.tau_e - G * E**2
    
    res_E = dE_dt - eq_E
    res_phi = dphi_dt - eq_phi
    res_N = dN_dt - eq_N
    
    # Scale residuals so they are comparable
    residual_score = torch.mean((res_phi / 1e11)**2).item()
    return residual_score

if __name__ == '__main__':
    print("PINN Digital Twin module initialized.")
