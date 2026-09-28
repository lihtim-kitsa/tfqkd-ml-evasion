import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for academic paper
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
sns.set_style("whitegrid")

def plot_evasion_frontier(attack_type):
    file_path = f'results/tables/evasion/pareto_front_{attack_type}.csv'
    if not os.path.exists(file_path):
        print(f"Data not found: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    
    plt.figure(figsize=(8, 6))
    
    # We plot attack score against the phase-impact proxy.
    # The attacker wants to be bottom-right (high impact, low score)
    # So the Pareto front should be a curve.
    
    plt.scatter(df['impact'], df['score'], color='firebrick', s=100, edgecolor='black',
                label='Evaluated non-dominated candidates')
    
    # Highlight the threshold
    # Reported Split A threshold; regenerate when corrected validation policy is applied.
    plt.axhline(y=0.038, color='black', linestyle='--',
                label='Reported Split A XGBoost threshold (0.038)')
    
    plt.title(f"Evaluated Physical-Parameter Search ({attack_type.upper()})")
    plt.xlabel("Phase-impact proxy (peak-to-peak phase deviation [rad])")
    plt.ylabel("ML attack score")
    
    plt.ylim(-0.05, 1.05)
    if attack_type == 'fim':
        plt.xlim(20, 25) # FIM impact is tightly bounded around 22-23
    else:
        plt.xscale('log') # TWIRL impact can be massive
        
    plt.legend(loc='lower right')
    plt.tight_layout()
    
    os.makedirs('results/figures', exist_ok=True)
    plt.savefig(f'results/figures/evasion_frontier_{attack_type}.png', dpi=300)
    plt.close()
    print(f"Generated evasion_frontier_{attack_type}.png")

def plot_defense_comparison():
    # Data derived from our reproduction and drift tests
    labels = ['XGBoost', 'Random Forest', 'Drift-hardened XGBoost', 'Drift-hardened RF']
    
    # False Positive Rates on Drift Data (%)
    fpr_values = [100.0, 100.0, 2.48, 1.80]
    
    plt.figure(figsize=(10, 6))
    
    colors = ['salmon', 'salmon', 'lightgreen', 'lightgreen']
    bars = plt.bar(labels, fpr_values, color=colors, edgecolor='black')
    
    plt.axhline(y=1.0, color='red', linestyle='--', label='Target FPR (1%)')
    
    plt.ylabel("False Positive Rate on Benign Drift (%)")
    plt.title("Observed FPR on Unseen Simulated Parameter Drift")
    plt.xticks(rotation=45, ha='right')
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1.0, f"{yval}%", ha='center', va='bottom', fontweight='bold')
        
    plt.ylim(0, 110)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('results/figures/defense_comparison.png', dpi=300)
    plt.close()
    print("Generated defense_comparison.png")

if __name__ == '__main__':
    plot_evasion_frontier('fim')
    plot_evasion_frontier('twirl')
    plot_defense_comparison()
