# Benchmark v1 Split Evaluation

## Motivation
To avoid the data leakage associated with simple random sampling (which mixes highly correlated adjacent points of simulated trajectories and mixes operating conditions), we enforce rigid test splits over three suites (A, B, C).

## Model Evaluation
All models were tuned for a $1\%$ False Positive Rate threshold on an independent validation fold before evaluating on the held-out test splits.

### Split A (Random Holdout / Reproduction)
Models easily learn the simulated feature boundaries when the training set spans the full operating and attack space.
- **XGBoost:** 98.5% FIM Recall, 96.4% TWIRL Recall
- **RandomForest:** 99.1% FIM Recall, 94.8% TWIRL Recall

### Split B (Held-Out Operating Regimes)
Models are trained only on standard physical parameters ($\kappa$, $\alpha$) and tested exclusively on "benign drift" parameters.
- **Result:** Complete failure. Tree-based models flag normal drift as attacks, yielding a **100% False Positive Rate**. This formally reproduces the critical real-world failure mode on our own isolated splits.

### Split C (Held-Out Attack Regimes)
Models are trained only on low-frequency FIM and low-detuning TWIRL, and tested exclusively on high-frequency FIM and high-detuning TWIRL.
- **LogReg:** Fails completely to catch high-frequency FIM ($0\%$ recall).
- **XGBoost:** Generalizes surprisingly well! Achieves $0.56\%$ binary False Negative Rate ($95.9\%$ multiclass FIM recall, $90.7\%$ multiclass TWIRL recall).
- **Conclusion:** While tree ensembles fail against benign hardware drift, they possess some inherent robustness generalizing across variations in attack intensity within the simulated limits.
