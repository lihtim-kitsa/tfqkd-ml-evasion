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
    
    # We want to plot Detection Score (y-axis) vs Physical Impact (x-axis)
    # The attacker wants to be bottom-right (high impact, low score)
    # So the Pareto front should be a curve.
    
    plt.scatter(df['impact'], df['score'], color='firebrick', s=100, edgecolor='black', label='Pareto Optimal Attacks')
    
    # Highlight the threshold
    # Our XGBoost validation threshold was approx 0.05
    plt.axhline(y=0.05, color='black', linestyle='--', label='ML Alarm Threshold (1% FPR)')
    
    plt.title(f"Adaptive Evasion Frontier ({attack_type.upper()})")
    plt.xlabel("Physical Impact (Peak-to-Peak Phase Deviation [rad])")
    plt.ylabel("ML Detection Score (Attack Probability)")
    
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
    labels = ['Naive XGBoost', 'Naive Random Forest', 'Drift-Hardened XGBoost', 'Drift-Hardened RF', 'PINN (Zero-Shot)']
    
    # False Positive Rates on Drift Data (%)
    fpr_values = [99.90, 100.0, 2.48, 1.80, 0.0]
    
    plt.figure(figsize=(10, 6))
    
    colors = ['salmon', 'salmon', 'lightgreen', 'lightgreen', 'dodgerblue']
    bars = plt.bar(labels, fpr_values, color=colors, edgecolor='black')
    
    plt.axhline(y=5.0, color='red', linestyle='--', label='Acceptable Max FPR (5%)')
    
    plt.ylabel("False Positive Rate on Benign Drift (%)")
    plt.title("Robustness to Operational Hardware Drift")
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
