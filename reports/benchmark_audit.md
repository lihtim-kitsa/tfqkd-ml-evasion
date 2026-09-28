# Benchmark Independence Audit

Dataset: `data\benchmark_v1.parquet` (7,500 windows, 750 group IDs).
Exact feature-trace hashes are used to expose repeated trajectories with different IDs.
This report does not estimate detector performance.

## Distinct traces by condition

| Case | Operating regime | Attack regime | Group IDs | Distinct feature traces |
|---|---|---|---:|---:|
| fim | drift_alpha | high_freq | 50 | 50 |
| fim | drift_alpha | low_freq | 50 | 50 |
| fim | drift_kappa | high_freq | 50 | 50 |
| fim | drift_kappa | low_freq | 50 | 50 |
| fim | standard | high_freq | 50 | 50 |
| fim | standard | low_freq | 50 | 50 |
| nominal | drift_alpha | none | 50 | 1 |
| nominal | drift_kappa | none | 50 | 1 |
| nominal | standard | none | 50 | 1 |
| twirl | drift_alpha | high_detuning | 50 | 50 |
| twirl | drift_alpha | low_detuning | 50 | 50 |
| twirl | drift_kappa | high_detuning | 50 | 50 |
| twirl | drift_kappa | low_detuning | 50 | 50 |
| twirl | standard | high_detuning | 50 | 50 |
| twirl | standard | low_detuning | 50 | 50 |

## Split overlap audit

| Split | Group ID overlap | Identical trace overlap |
|---|---:|---:|
| Split_A | 0 | 3 |
| Split_B | 0 | 0 |
| Split_C | 150 | 3 |
