import pandas as pd
import joblib
import numpy as np

print("Loading drift dataset...")
df_drift = pd.read_parquet('data/drift_dataset.parquet')
X_drift = df_drift[['mu', 'sigma2', 'Psb', 'delta_phi', 'qber']].values

print("Loading scaler...")
scaler = joblib.load('checkpoints/scaler.pkl')
X_drift_scaled = scaler.transform(X_drift)

models = ['xgboost', 'randomforest', 'svm', 'logreg']
for name in models:
    model = joblib.load(f'checkpoints/{name}.pkl')
    preds = model.predict(X_drift_scaled)
    # Drift dataset only contains nominal samples (label 0) according to the paper (5,000 samples).
    # Any prediction > 0 is a False Positive.
    fp = np.sum(preds > 0)
    total = len(preds)
    fpr = fp / total
    print(f"{name} FPR on Unhardened Model: {fpr*100:.2f}% ({fp}/{total})")
