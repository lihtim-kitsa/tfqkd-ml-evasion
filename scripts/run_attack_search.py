import os
import sys
import optuna
import joblib
import numpy as np
import pandas as pd
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.simulator.oil_rate_equations import OILSimulator
from src.simulator.attack_injectors import FIMInjector, TWIRLInjector
from src.features.feature_extraction import extract_features

class AdversarialEvasion:
    def __init__(self, model_path, scaler_path, attack_type='fim'):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.attack_type = attack_type
        
        # Standard benign settings
        self.kappa = 1e9
        self.alpha = 3.0
        self.gamma = 1e11
        self.current_amp = 2.0e17
        
        self.simulator = OILSimulator(kappa=self.kappa, alpha=self.alpha, gamma=self.gamma)
        
    def simulate_attack(self, params):
        t_span = (0, 1e-6)
        t_eval = np.linspace(0, 1e-6, 1000)
        y0 = [1.0, 0.0, 1e8]
        base_E_ref = 1.0
        base_phi_ref = 0.0
        
        def current_func(t): return self.current_amp * (1.0 + 0.01 * np.sin(2 * np.pi * 1e5 * t))
        
        if self.attack_type == 'fim':
            injector = FIMInjector(m=params['m'], f_fim=params['f_fim'])
            def E_ref_func(t): return injector.inject_E_ref(t, base_E_ref)
            def phi_ref_func(t): return base_phi_ref
        elif self.attack_type == 'twirl':
            injector = TWIRLInjector(delta_lambda=params['delta_lambda'])
            def E_ref_func(t): return base_E_ref
            def phi_ref_func(t): return injector.inject_phi_ref(t, base_phi_ref)
            
        sol = self.simulator.simulate(t_span, y0, E_ref_func, phi_ref_func, current_func, t_eval)
        
        if not sol.success:
            return None, None
            
        features = extract_features(sol.t, sol.y[0], sol.y[1], sol.y[2])
        
        # Calculate impact (peak-to-peak phase deviation on the first window)
        impact_ptp_phi = np.max(sol.y[1][:100]) - np.min(sol.y[1][:100])
        
        # ML Score (average over the 10 windows)
        scaled_features = self.scaler.transform(features)
        probs = self.model.predict_proba(scaled_features)
        
        # probability of attack (class 1 + class 2)
        attack_probs = probs[:, 1] + probs[:, 2]
        mean_attack_score = np.mean(attack_probs)
        
        return mean_attack_score, impact_ptp_phi

    def objective(self, trial):
        if self.attack_type == 'fim':
            params = {
                'm': trial.suggest_float('m', 0.05, 0.40),
                'f_fim': trial.suggest_float('f_fim', 1e8, 1e10, log=True)
            }
        elif self.attack_type == 'twirl':
            params = {
                'delta_lambda': trial.suggest_float('delta_lambda', 0.1, 5.0, log=True)
            }
            
        score, impact = self.simulate_attack(params)
        
        if score is None:
            raise optuna.exceptions.TrialPruned()
            
        # We want to MINIMIZE attack score, and MAXIMIZE impact (so we return -impact)
        return score, -impact

def run_optimization(attack_type, n_trials=100):
    print(f"\n--- Running Bayesian Evasion Search for {attack_type.upper()} ---")
    evader = AdversarialEvasion(
        model_path='checkpoints/Split_A/XGBoost.pkl',
        scaler_path='checkpoints/Split_A/scaler.pkl',
        attack_type=attack_type
    )
    
    # Enable multithreading for optuna
    sampler = optuna.samplers.NSGAIISampler(seed=42)
    study = optuna.create_study(directions=["minimize", "minimize"], sampler=sampler)
    
    study.optimize(evader.objective, n_trials=n_trials, n_jobs=max(1, mp.cpu_count() - 1))
    
    # Extract Pareto Front
    trials = study.best_trials
    
    results = []
    for t in trials:
        score = t.values[0]
        impact = -t.values[1]
        res = {'score': score, 'impact': impact}
        res.update(t.params)
        results.append(res)
        
    df = pd.DataFrame(results)
    os.makedirs('results/tables/evasion', exist_ok=True)
    df.to_csv(f'results/tables/evasion/pareto_front_{attack_type}.csv', index=False)
    
    print(f"Found {len(trials)} optimal points on the Pareto front.")
    print("Pareto points saved to results/tables/evasion/")
    print(df.sort_values(by='score').head(10))

if __name__ == '__main__':
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    run_optimization('fim', n_trials=200)
    run_optimization('twirl', n_trials=200)
