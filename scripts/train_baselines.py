import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_recall_fscore_support, precision_recall_curve

def load_data(split_suite):
    print(f"\nLoading data for {split_suite}...")
    df = pd.read_parquet('data/benchmark_v1.parquet')
    
    with open('configs/splits.json', 'r') as f:
        splits = json.load(f)
        
    train_groups = splits[split_suite]['train_groups']
    test_groups = splits[split_suite]['test_groups']
    
    # We will use 20% of train groups as validation for threshold tuning
    np.random.seed(42)
    shuffled_train = np.random.permutation(train_groups)
    val_idx = int(len(shuffled_train) * 0.2)
    val_groups = shuffled_train[:val_idx].tolist()
    train_groups = shuffled_train[val_idx:].tolist()
    
    # Filter Dataframes
    train_df = df[df['group_id'].isin(train_groups)]
    val_df = df[df['group_id'].isin(val_groups)]
    test_df = df[df['group_id'].isin(test_groups)]
    
    features = ['mu', 'sigma2', 'Psb', 'delta_phi', 'qber']
    
    X_train = train_df[features].values
    y_train = train_df['label'].values
    
    X_val = val_df[features].values
    y_val = val_df['label'].values
    
    X_test = test_df[features].values
    y_test = test_df['label'].values
    y_test_binary = (y_test > 0).astype(int)
    
    # Scaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)
    
    return X_train, y_train, X_val, y_val, X_test, y_test, y_test_binary, scaler

def train_and_evaluate(split_suite):
    X_train, y_train, X_val, y_val, X_test, y_test, y_test_binary, scaler = load_data(split_suite)
    
    models = {
        'LogReg': LogisticRegression(multi_class='multinomial', max_iter=1000),
        'XGBoost': XGBClassifier(n_estimators=100, eval_metric='logloss'),
        'RandomForest': RandomForestClassifier(n_estimators=100)
    }
    
    os.makedirs(f'results/tables/{split_suite}', exist_ok=True)
    os.makedirs(f'checkpoints/{split_suite}', exist_ok=True)
    joblib.dump(scaler, f'checkpoints/{split_suite}/scaler.pkl')
    
    results_list = []
    
    for name, model in models.items():
        print(f"Training {name} on {split_suite}...")
        model.fit(X_train, y_train)
        joblib.dump(model, f'checkpoints/{split_suite}/{name}.pkl')
        
        # Binary target for threshold tuning (Attack vs Nominal)
        y_val_binary = (y_val > 0).astype(int)
        
        # Get attack probabilities (sum of FIM and TWIRL probabilities)
        val_probs = model.predict_proba(X_val)
        val_attack_probs = val_probs[:, 1] + val_probs[:, 2]
        
        # Tune threshold on validation set (target FPR = 0.05)
        fpr_curve, tpr_curve, thresholds = precision_recall_curve(y_val_binary, val_attack_probs)
        # We want to use roc_curve to get FPR
        from sklearn.metrics import roc_curve
        fpr_roc, tpr_roc, thresholds_roc = roc_curve(y_val_binary, val_attack_probs)
        
        # Find threshold where FPR is ~ 0.01 (1%)
        target_fpr = 0.01
        valid_idx = np.where(fpr_roc <= target_fpr)[0]
        if len(valid_idx) > 0:
            best_idx = valid_idx[-1]
            chosen_threshold = thresholds_roc[best_idx]
        else:
            chosen_threshold = 0.5
            
        print(f"[{name}] Chosen Threshold on Val Data: {chosen_threshold:.4f} for target FPR ~1%")
        
        # Evaluate on test set
        test_probs = model.predict_proba(X_test)
        test_attack_probs = test_probs[:, 1] + test_probs[:, 2]
        
        # Hard decisions using standard argmax for multiclass metrics
        preds = model.predict(X_test)
        
        # Binary decisions using chosen threshold
        binary_preds = (test_attack_probs >= chosen_threshold).astype(int)
        
        # Calculate Metrics
        test_fpr = np.sum((binary_preds == 1) & (y_test_binary == 0)) / max(1, np.sum(y_test_binary == 0))
        test_fnr = np.sum((binary_preds == 0) & (y_test_binary == 1)) / max(1, np.sum(y_test_binary == 1))
        
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, preds, labels=[0, 1, 2], zero_division=0)
        
        res = {
            'Model': name,
            'Split': split_suite,
            'Val_Threshold': chosen_threshold,
            'Test_FPR_Binary': test_fpr,
            'Test_FNR_Binary': test_fnr,
            'Precision_Nominal': prec[0],
            'Precision_FIM': prec[1],
            'Precision_TWIRL': prec[2],
            'Recall_Nominal': rec[0],
            'Recall_FIM': rec[1],
            'Recall_TWIRL': rec[2]
        }
        results_list.append(res)
        
    df_res = pd.DataFrame(results_list)
    df_res.to_csv(f'results/tables/{split_suite}_results.csv', index=False)
    print(df_res)
    
if __name__ == '__main__':
    for suite in ['Split_A', 'Split_B', 'Split_C']:
        train_and_evaluate(suite)
