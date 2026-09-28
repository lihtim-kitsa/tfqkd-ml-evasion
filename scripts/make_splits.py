import pandas as pd
import numpy as np
import json
import os

def create_splits():
    print("Loading benchmark data...")
    df = pd.read_parquet('data/benchmark_v1.parquet')
    
    # We want reproducible random splits, so we use a fixed seed
    np.random.seed(42)
    
    # Get unique group_ids (each corresponds to one simulation trajectory)
    group_ids = df['group_id'].unique()
    
    splits = {}
    
    # Split A: Random 80/20 grouped split
    np.random.shuffle(group_ids)
    split_idx = int(len(group_ids) * 0.8)
    train_groups_A = group_ids[:split_idx].tolist()
    test_groups_A = group_ids[split_idx:].tolist()
    
    splits['Split_A'] = {
        'description': 'Random grouped split (80/20)',
        'train_groups': train_groups_A,
        'test_groups': test_groups_A
    }
    
    # Split B: Held-out operating regimes
    # Train: op_regime == 'standard'
    # Test: op_regime != 'standard'
    train_groups_B = df[df['op_regime'] == 'standard']['group_id'].unique().tolist()
    test_groups_B = df[df['op_regime'] != 'standard']['group_id'].unique().tolist()
    
    splits['Split_B'] = {
        'description': 'Held-out operating regimes (drift_kappa, drift_alpha)',
        'train_groups': train_groups_B,
        'test_groups': test_groups_B
    }
    
    # Split C: Held-out attack ranges
    # Train: attack_regime in ['none', 'low_freq', 'low_detuning']
    # Test: attack_regime in ['none', 'high_freq', 'high_detuning']
    train_groups_C = df[df['attack_regime'].isin(['none', 'low_freq', 'low_detuning'])]['group_id'].unique().tolist()
    test_groups_C = df[df['attack_regime'].isin(['none', 'high_freq', 'high_detuning'])]['group_id'].unique().tolist()
    
    splits['Split_C'] = {
        'description': 'Held-out attack ranges (high_freq, high_detuning)',
        'train_groups': train_groups_C,
        'test_groups': test_groups_C
    }
    
    os.makedirs('configs', exist_ok=True)
    with open('configs/splits.json', 'w') as f:
        json.dump(splits, f, indent=4)
        
    print(f"Splits generated and saved to configs/splits.json")
    print(f"Split A: {len(train_groups_A)} train groups, {len(test_groups_A)} test groups")
    print(f"Split B: {len(train_groups_B)} train groups, {len(test_groups_B)} test groups")
    print(f"Split C: {len(train_groups_C)} train groups, {len(test_groups_C)} test groups")

if __name__ == '__main__':
    create_splits()
