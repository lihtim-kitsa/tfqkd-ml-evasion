import numpy as np
import pandas as pd
import sys
import os
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.simulator.oil_rate_equations import OILSimulator
from src.simulator.attack_injectors import FIMInjector, TWIRLInjector
from src.features.feature_extraction import extract_features

def run_simulation(args):
    # args: (seed, case_type, operating_regime, attack_regime)
    seed, case_type, op_regime_val, attack_regime_val = args
    np.random.seed(seed)
    
    # Base parameters
    kappa = 1e9
    alpha = 3.0
    gamma = 1e11
    current_amp = 2.0e17
    
    # Apply operating regime (Split B)
    if op_regime_val == 'drift_kappa':
        kappa = 1.2e9
    elif op_regime_val == 'drift_alpha':
        alpha = 3.5
        
    simulator = OILSimulator(kappa=kappa, alpha=alpha, gamma=gamma)
    t_span = (0, 1e-6)
    t_eval = np.linspace(0, 1e-6, 1000)
    y0 = [1.0, 0.0, 1e8]
    
    base_E_ref = 1.0
    base_phi_ref = 0.0
    
    # Benign noise on current
    def current_func(t): return current_amp * (1.0 + 0.01 * np.sin(2 * np.pi * 1e5 * t))
    
    if case_type == 'nominal':
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return base_phi_ref
        label = 0
    elif case_type == 'fim':
        # Apply attack regime (Split C)
        if attack_regime_val == 'low_freq':
            f_fim = np.random.uniform(1e8, 1e9)
        else: # high_freq
            f_fim = np.random.uniform(1e9, 1e10)
        m = np.random.uniform(0.05, 0.40)
        
        injector = FIMInjector(m=m, f_fim=f_fim)
        def E_ref_func(t): return injector.inject_E_ref(t, base_E_ref)
        def phi_ref_func(t): return base_phi_ref
        label = 1
    elif case_type == 'twirl':
        if attack_regime_val == 'low_detuning':
            delta_lambda = np.random.uniform(0.1, 2.5)
        else: # high_detuning
            delta_lambda = np.random.uniform(2.5, 5.0)
            
        injector = TWIRLInjector(delta_lambda=delta_lambda)
        def E_ref_func(t): return base_E_ref
        def phi_ref_func(t): return injector.inject_phi_ref(t, base_phi_ref)
        label = 2
    else:
        raise ValueError("Unknown case type")

    sol = simulator.simulate(t_span, y0, E_ref_func, phi_ref_func, current_func, t_eval)
    if not sol.success:
        return None
        
    features = extract_features(sol.t, sol.y[0], sol.y[1], sol.y[2])
    # Compute impact for each window (just to record it, max phase - min phase)
    # features shape: (10, 5)
    
    rows = []
    # window_size in extract_features is 100
    for i in range(10):
        start = i * 100
        end = start + 100
        window_phi = sol.y[1][start:end]
        impact = np.max(window_phi) - np.min(window_phi)
        
        row = {
            'mu': features[i, 0],
            'sigma2': features[i, 1],
            'Psb': features[i, 2],
            'delta_phi': features[i, 3],
            'qber': features[i, 4],
            'impact_ptp_phi': impact,
            'label': label,
            'case_type': case_type,
            'op_regime': op_regime_val,
            'attack_regime': attack_regime_val,
            'seed': seed,
            'group_id': f"{case_type}_{op_regime_val}_{attack_regime_val}_{seed}"
        }
        rows.append(row)
    return rows

def generate_benchmark():
    tasks = []
    seed_counter = 42
    
    cases = ['nominal', 'fim', 'twirl']
    op_regimes = ['standard', 'drift_kappa', 'drift_alpha']
    attack_regimes = ['none', 'low_freq', 'high_freq', 'low_detuning', 'high_detuning']
    
    # Create combinations
    for op in op_regimes:
        for c in cases:
            # Decide valid attack regimes
            if c == 'nominal':
                aregimes = ['none']
            elif c == 'fim':
                aregimes = ['low_freq', 'high_freq']
            elif c == 'twirl':
                aregimes = ['low_detuning', 'high_detuning']
            
            for ar in aregimes:
                # 50 runs per combination = 500 samples
                for _ in range(50):
                    tasks.append((seed_counter, c, op, ar))
                    seed_counter += 1
                    
    print(f"Total simulations to run: {len(tasks)}")
    
    cpu_cores = max(1, mp.cpu_count() - 1)
    results = []
    with mp.Pool(processes=cpu_cores) as pool:
        for i, res in enumerate(pool.imap_unordered(run_simulation, tasks)):
            if i % 100 == 0:
                print(f"Completed {i}/{len(tasks)}")
            if res is not None:
                results.extend(res)
                
    df = pd.DataFrame(results)
    os.makedirs('data', exist_ok=True)
    df.to_parquet('data/benchmark_v1.parquet')
    print(f"Benchmark saved to data/benchmark_v1.parquet with shape {df.shape}")

if __name__ == '__main__':
    generate_benchmark()
