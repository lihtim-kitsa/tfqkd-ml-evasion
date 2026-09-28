import sys
import os
import numpy as np

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulator.oil_rate_equations import OILSimulator
from src.simulator.attack_injectors import FIMInjector, TWIRLInjector
from src.features.feature_extraction import extract_features

def run_case(case_type):
    print(f"\n--- Running case: {case_type} ---")
    simulator = OILSimulator()
    t_span = (0, 1e-6)
    t_eval = np.linspace(0, 1e-6, 1000)
    y0 = [1.0, 0.0, 1e8]
    
    base_E_ref = 1.0
    base_phi_ref = 0.0
    
    def current_func(t): return 2.0e17
    
    if case_type == 'nominal':
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return base_phi_ref
    elif case_type == 'benign-drift':
        # Introduce a slow drift in current or E_ref
        def current_func(t): return 2.0e17 * (1.0 + 0.05 * np.sin(2 * np.pi * 1e5 * t))
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return base_phi_ref
    elif case_type == 'fim':
        injector = FIMInjector(m=0.2, f_fim=5e8)
        def E_ref_func(t): return injector.inject_E_ref(t, base_E_ref)
        def phi_ref_func(t): return base_phi_ref
    elif case_type == 'twirl':
        injector = TWIRLInjector(delta_lambda=2.0)
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return injector.inject_phi_ref(t, base_phi_ref)
    
    sol = simulator.simulate(t_span, y0, E_ref_func, phi_ref_func, current_func, t_eval)
    
    if sol.success:
        print("Simulation successful.")
        features = extract_features(sol.t, sol.y[0], sol.y[1], sol.y[2])
        print("Features shape:", features.shape)
        print("Mean features for this run:")
        print("mu:", np.mean(features[:, 0]))
        print("sigma2:", np.mean(features[:, 1]))
        print("Psb:", np.mean(features[:, 2]))
        print("delta_phi:", np.mean(features[:, 3]))
        print("qber:", np.mean(features[:, 4]))
        
        # Calculate impact observable: peak-to-peak phase deviation over the whole trace
        ptp_phi = np.max(sol.y[1]) - np.min(sol.y[1])
        print("Impact Observable (Peak-to-Peak Phase Dev):", ptp_phi)
    else:
        print("Simulation failed.")

if __name__ == '__main__':
    run_case('nominal')
    run_case('benign-drift')
    run_case('fim')
    run_case('twirl')
