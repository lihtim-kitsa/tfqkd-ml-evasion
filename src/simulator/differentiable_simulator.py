import torch
import torch.nn as nn
from torchdiffeq import odeint_adjoint as odeint
import numpy as np

class DifferentiableLangKobayashi(nn.Module):
    def __init__(self, kappa=1e9, alpha=3.0, gamma=1e11, delta_omega=0.0, device='cpu'):
        super().__init__()
        self.device = device
        self.kappa = torch.tensor(kappa, dtype=torch.float32, device=device)
        self.alpha = torch.tensor(alpha, dtype=torch.float32, device=device)
        self.gamma = torch.tensor(gamma, dtype=torch.float32, device=device)
        self.delta_omega = torch.tensor(delta_omega, dtype=torch.float32, device=device)
        self.g0 = torch.tensor(1.2e11, dtype=torch.float32, device=device)
        self.N_tr = torch.tensor(1e8, dtype=torch.float32, device=device)
        self.tau_e = torch.tensor(1e-9, dtype=torch.float32, device=device)
        self.base_I = torch.tensor(2.0e17, dtype=torch.float32, device=device)

        # Attacker's physical control knobs (made differentiable!)
        self.m = nn.Parameter(torch.tensor(0.1, dtype=torch.float32, device=device))
        self.f_fim_scaled = nn.Parameter(torch.tensor(1.0, dtype=torch.float32, device=device)) # Scaled (e.g. * 1e9)
        self.delta_lambda = nn.Parameter(torch.tensor(0.0, dtype=torch.float32, device=device))

    def forward(self, t, y):
        # y is [batch_size, 3] -> E, phi, N
        E = y[:, 0]
        phi = y[:, 1]
        N = y[:, 2]

        base_E_ref = torch.tensor(1.0, device=self.device)
        base_phi_ref = torch.tensor(0.0, device=self.device)
        
        # Attack Modulations
        # Using softplus to enforce physical constraints automatically
        m_clamped = torch.sigmoid(self.m) * 0.35 + 0.05 # [0.05, 0.40]
        f_fim = torch.nn.functional.softplus(self.f_fim_scaled) * 1e9
        
        E_ref = base_E_ref * (1.0 + m_clamped * torch.sin(2 * np.pi * f_fim * t))
        
        # TWIRL Modulation (lambda shift)
        d_lambda = torch.nn.functional.softplus(self.delta_lambda)
        phi_ref = base_phi_ref + d_lambda * t * 1e11 

        # Benign Drift
        I_inj = self.base_I * (1.0 + 0.01 * torch.sin(2 * np.pi * 1e5 * t))

        # Gain Equation
        G = self.g0 * (N - self.N_tr) / self.N_tr

        # Rate Equations
        dE_dt = 0.5 * (G - self.gamma) * E + self.kappa * E_ref * torch.cos(phi_ref - phi)
        dphi_dt = 0.5 * self.alpha * (G - self.gamma) - self.delta_omega + self.kappa * (E_ref / (E + 1e-12)) * torch.sin(phi_ref - phi)
        dN_dt = I_inj - N / self.tau_e - G * E**2

        return torch.stack([dE_dt, dphi_dt, dN_dt], dim=1)

def simulate_differentiable(model, t_span, y0, t_eval):
    # odeint_adjoint backpropagates through the ODE solver!
    # y0 should be [batch_size, 3]
    y_traj = odeint(model, y0, t_eval, method='rk4', options={'step_size': 1e-11})
    return y_traj
