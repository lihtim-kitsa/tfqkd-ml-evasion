import torch
import torch.optim as optim
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.simulator.differentiable_simulator import DifferentiableLangKobayashi, simulate_differentiable

def run_whitebox_attack():
    print("Initializing Differentiable Digital Twin (Neural ODE)...")
    device = 'cpu'
    model = DifferentiableLangKobayashi(device=device)
    
    # We want to optimize the attacker's physical controls (m, f_fim)
    optimizer = optim.Adam([model.m, model.f_fim_scaled, model.delta_lambda], lr=0.05)
    
    t_eval = torch.linspace(0, 1e-6, 100, device=device)
    y0 = torch.tensor([[1.0, 0.0, 1e8]], dtype=torch.float32, device=device)
    
    print("Starting Backpropagation through Time (Physics)...")
    for epoch in range(15):
        optimizer.zero_grad()
        
        # Forward pass through the differential equations
        y_traj = simulate_differentiable(model, t_eval=[0, 1e-6], y0=y0, t_eval_out=t_eval)
        # torchdiffeq output shape: [time_steps, batch, state_dim]
        phi = y_traj[:, 0, 1]
        
        # We want to MAXIMIZE impact (peak-to-peak phase deviation)
        # while keeping the attack inside a physical "stealth" boundary 
        # (e.g., constraining the high-frequency oscillation amplitude)
        
        impact = torch.max(phi) - torch.min(phi)
        
        # Regularization: attacker wants to minimize modulation depth to stay hidden
        m_actual = torch.sigmoid(model.m) * 0.35 + 0.05
        f_fim_actual = torch.nn.functional.softplus(model.f_fim_scaled) * 1e9
        
        stealth_penalty = 10.0 * m_actual
        
        # Loss: minimize stealth penalty, maximize impact
        loss = stealth_penalty - impact
        
        # Backpropagate EXACT physical gradients through the Lang-Kobayashi equations!
        loss.backward()
        optimizer.step()
        
        if epoch % 2 == 0:
            print(f"Epoch {epoch:02d} | Loss: {loss.item():.4f} | Impact: {impact.item():.2f} rad | m: {m_actual.item():.3f} | f_fim: {f_fim_actual.item()/1e9:.2f} GHz")
            
    print("\nWhite-Box Neural ODE Attack Complete.")
    print("We successfully backpropagated through the quantum optical simulator!")

# Wrapper to handle t_eval matching for torchdiffeq
def simulate_differentiable(model, t_eval, y0, t_eval_out):
    from torchdiffeq import odeint_adjoint as odeint
    return odeint(model, y0, t_eval_out, method='rk4', options={'step_size': 1e-9})

if __name__ == '__main__':
    run_whitebox_attack()
