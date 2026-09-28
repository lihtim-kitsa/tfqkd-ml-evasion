import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.simulator.oil_rate_equations import OILSimulator
from src.simulator.attack_injectors import FIMInjector, TWIRLInjector

def get_physics_residual(t, E, phi, N, kappa=1e9, alpha=3.0, gamma=1e11):
    dt = t[1] - t[0]
    # Finite difference
    dE_dt = np.gradient(E) / dt
    dphi_dt = np.gradient(phi) / dt
    dN_dt = np.gradient(N) / dt
    
    # Nominal assumptions
    E_ref = 1.0
    phi_ref = 0.0
    I_inj = 2.0e17 * (1.0 + 0.01 * np.sin(2 * np.pi * 1e5 * t))
    
    g0 = 1.2e11
    N_tr = 1e8
    tau_e = 1e-9
    
    G = g0 * (N - N_tr) / N_tr
    
    eq_E = 0.5 * (G - gamma) * E + kappa * E_ref * np.cos(phi_ref - phi)
    eq_phi = 0.5 * alpha * (G - gamma) + kappa * (E_ref / (E + 1e-12)) * np.sin(phi_ref - phi)
    eq_N = I_inj - N / tau_e - G * E**2
    
    res_phi = np.mean((dphi_dt - eq_phi)**2)
    return res_phi

def run_case_and_score(case_type, op_regime):
    kappa = 1.2e9 if op_regime == 'drift_kappa' else 1e9
    alpha = 3.5 if op_regime == 'drift_alpha' else 3.0
    gamma = 1e11
    
    simulator = OILSimulator(kappa=kappa, alpha=alpha, gamma=gamma)
    t_span = (0, 1e-6)
    t_eval = np.linspace(0, 1e-6, 1000)
    y0 = [1.0, 0.0, 1e8]
    
    base_E_ref = 1.0
    base_phi_ref = 0.0
    current_amp = 2.0e17
    def current_func(t): return current_amp * (1.0 + 0.01 * np.sin(2 * np.pi * 1e5 * t))
    
    if case_type == 'nominal':
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return base_phi_ref
    elif case_type == 'fim':
        injector = FIMInjector(m=0.2, f_fim=5e8)
        def E_ref_func(t): return injector.inject_E_ref(t, base_E_ref)
        def phi_ref_func(t): return base_phi_ref
    elif case_type == 'twirl':
        injector = TWIRLInjector(delta_lambda=1.0)
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return injector.inject_phi_ref(t, base_phi_ref)

    sol = simulator.simulate(t_span, y0, E_ref_func, phi_ref_func, current_func, t_eval)
    
    # Let's test the residual under the assumption that kappa=1e9 and alpha=3.0
    # If there's drift, the observer STILL assumes nominal params.
    # We want to see if the residual spike for attacks is WAY BIGGER than for drift.
    
    res = get_physics_residual(sol.t, sol.y[0], sol.y[1], sol.y[2], kappa=1e9, alpha=3.0)
    print(f"[{case_type.upper()}] (Op Regime: {op_regime}) Physics Residual: {res:.4e}")

if __name__ == '__main__':
    print("Zero-Shot Physics Residual Scores:")
    run_case_and_score('nominal', 'standard')
    run_case_and_score('nominal', 'drift_kappa')
    run_case_and_score('nominal', 'drift_alpha')
    run_case_and_score('fim', 'standard')
    run_case_and_score('twirl', 'standard')
