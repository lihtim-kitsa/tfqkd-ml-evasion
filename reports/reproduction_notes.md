# Reproduction Notes and Baseline Differences

## Pipeline Execution
- The original repository provides a `train_models.py` script.
- The script uses an 80/20 train/test split via `train_test_split`.

## Mismatches Found
1. **Normalization Strategy**: The paper reports that "All physical features were Z-score normalized before training", but the implementation in `train_models.py` uses `QuantileTransformer(output_distribution='normal')` instead of `StandardScaler`. This enforces a normal distribution rather than a simple Z-score transformation.
2. **Deep SVDD vs. Classical**: The original paper mentions XGBoost, Random Forest, RBF-kernel SVM, and Logistic Regression, while the repo additionally trains a `DeepSVDD` autoencoder which appears intended as a zero-day detector.

## Reproduction Results (Table III)
The original supervised evaluation was fully reproduced successfully. The obtained metrics match the paper exactly for XGBoost, SVM, and Logistic Regression, with Random Forest differing by a tiny fraction ($87.08\%$ vs $86.98\%$, likely due to bagging randomness).

**XGBoost ($87.52\%$ Accuracy):**
- **Nominal (0):** Precision: 1.00, Recall: 1.00, F1: 1.00
- **FIM (1):** Precision: 0.83, Recall: 0.78, F1: 0.80
- **TWIRL (2):** Precision: 0.80, Recall: 0.84, F1: 0.82

**Random Forest ($87.08\%$ Accuracy):**
- **Nominal (0):** Precision: 1.00, Recall: 1.00, F1: 1.00
- **FIM (1):** Precision: 0.81, Recall: 0.79, F1: 0.80
- **TWIRL (2):** Precision: 0.80, Recall: 0.82, F1: 0.81

**SVM ($68.23\%$ Accuracy):**
- **Nominal (0):** Precision: 0.71, Recall: 0.90, F1: 0.80
- **FIM (1):** Precision: 0.75, Recall: 0.51, F1: 0.60
- **TWIRL (2):** Precision: 0.60, Recall: 0.63, F1: 0.62

**Logistic Regression ($54.53\%$ Accuracy):**
- **Nominal (0):** Precision: 0.62, Recall: 0.70, F1: 0.66
- **FIM (1):** Precision: 0.54, Recall: 0.50, F1: 0.52
- **TWIRL (2):** Precision: 0.46, Recall: 0.44, F1: 0.45

## Drift Hardening Reproduction (Fig 4)
The paper reports that pre-hardening models fail on the drift dataset, with XGBoost at 99.88% FPR and Random Forest at 99.94% FPR.
Our reproduction on the unhardened models yielded:
- **XGBoost:** 99.90% FPR
- **Random Forest:** 100.0% FPR
This confirms the massive failure rate under unseen benign drift.

When training was supplemented with drift examples (hardening), the FPR dropped exactly as reported in the paper:
- **XGBoost Hardened:** 2.48% FPR (124 false alarms)
- **Random Forest Hardened:** 1.80% FPR (90 false alarms)
