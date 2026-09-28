# Physics-Constrained Attack Search and Drift Monitoring for OIL TF-QKD

This repository contains a simulator-based study of optical-injection-locked
twin-field quantum key distribution (OIL TF-QKD). It explores how supervised
classifiers respond to simulated operating-parameter drift, searches over two
simulated reference-beam manipulations, and evaluates a residual from a nominal
Lang-Kobayashi phase model.

## Research status and limits

> **Research prototype; results are exploratory.** The reported tables and figures
> have not been regenerated under the revised threshold policy. Split C contains
> overlapping nominal trajectory groups, nominal simulations are deterministic,
> the TWIRL phase ramp is a simplified simulator rule, and the PIAD implementation
> does not define a calibrated alarm threshold or report trajectory-level detection
> metrics. Nothing here establishes hardware robustness, attack feasibility, or QKD
> security.

The revised paper, [Adaptive_Evasion_OIL_TFQKD_Revised.tex](Adaptive_Evasion_OIL_TFQKD_Revised.tex),
documents the current scope, corrections, and recalculation checklist. Its reported
classifier thresholds and threshold-dependent metrics remain provisional. The
evasion-search scores are model outputs and do not depend on the alarm threshold.

## What is in the repository

| Path | Contents |
| --- | --- |
| src/simulator/oil_rate_equations.py | Lang-Kobayashi rate-equation simulator |
| src/simulator/attack_injectors.py | FIM and simplified TWIRL input functions |
| src/features/feature_extraction.py | Five per-window telemetry features |
| scripts/generate_data.py | Creates the simulation benchmark |
| scripts/make_splits.py | Creates the three trajectory-group split definitions |
| scripts/train_baselines.py | Fits Logistic Regression, XGBoost, and Random Forest models |
| scripts/run_attack_search.py | Runs the 200-evaluation-per-family NSGA-II search |
| scripts/test_physics_residual.py | Prints phase-residual values for selected conditions |
| scripts/generate_paper_figures.py | Recreates figures from saved CSV outputs |
| scripts/check_unhardened_drift.py | Drift-data diagnostic |
| scripts/test_simulator.py | Simulator smoke check |
| scripts/train_pinn_detector.py and scripts/whitebox_neural_ode_attack.py | Earlier exploratory scripts; not evidence for the revised PIAD or attack-search claims |
| data/benchmark_v1.parquet | Saved benchmark data: 7,500 windows from 750 trajectories |
| configs/splits.json | Saved train/test trajectory-group assignments |
| checkpoints/ | Saved scalers and classifier checkpoints by split |
| results/tables/ | Saved classifier and attack-search CSV results |
| results/figures/ | Figures used by the revised manuscript |
| reports/ | Earlier drafts, audits, and project notes |

## Simulated setup

Each trajectory covers 1 microsecond and is saved at 1,000 uniformly spaced points
(about 1 GS/s). The model uses nominal parameters kappa = 1e9 s^-1 and alpha = 3.
The drift cases set kappa = 1.2e9 s^-1 (20% higher) or alpha = 3.5 (about 16.7%
higher). A deterministic 100 kHz current ripple is included.

The benchmark has nominal, fast-intensity-modulation (FIM), and
trojan-wavelength-injection (TWIRL) trajectories. FIM modulates reference amplitude
over 100 MHz–10 GHz with modulation depth 0.05–0.40. The saved sampling rate has a
500 MHz Nyquist limit, so FIM components above that limit can alias in the recorded
telemetry.

The TWIRL injector currently applies

    phi_ref(t) = delta_lambda * t * 1e11

with delta_lambda supplied in nanometres. The code does not use its calculated
frequency shift or power-ratio parameter in the simulated field equations. This is
a simplified phase ramp, not a verified wavelength-to-frequency conversion or a
validated model of a detuned optical component.

The five classifier inputs are mean and variance of |E|^2, an FFT sideband quantity,
phase RMS, and a synthetic QBER proxy. The QBER proxy is deterministically computed
from phase RMS, intensity variance, and mean intensity, so the vector has four
independent quantities. The phase peak-to-peak value plotted against classifier
score is also correlated with phase-derived classifier inputs; it is not an
independent measure of physical or protocol-level impact.

## Setup

The provided Conda environment lists the scientific Python and plotting packages:

    conda env create -f environment.yml
    conda activate adaptive-oil-qkd

Two additional packages are needed by the checked-in scripts/data format but are
not listed in environment.yml:

    python -m pip install optuna pyarrow

Use a Python environment compatible with the saved joblib checkpoints. Rebuilding
the environment or rerunning model training can produce different versions and
results.

## Reproduction workflow

Run commands from the repository root.

1. **Use the included dataset and split files for inspection.** Regenerating the
   dataset is optional and overwrites data/benchmark_v1.parquet:

       python scripts/generate_data.py

2. **Recreate split assignments only when needed.** This overwrites
   configs/splits.json:

       python scripts/make_splits.py

   The current Split C construction includes the same 150 nominal group IDs in both
   its 450-group training pool and 450-group test pool. Its reported metrics are
   therefore not valid held-out-configuration estimates. Split A also assigns
   deterministic copies of nominal trajectories distinct group IDs, which can put
   identical nominal traces on both sides of the split.

3. **Train and evaluate the supervised baselines.** This overwrites saved
   checkpoints and CSV tables:

       python scripts/train_baselines.py

   Threshold-dependent values need review before interpretation. Verify the
   threshold rule and equality convention against the revised paper, then regenerate
   validation thresholds, test FPR/FNR, and class recalls. The current code makes
   binary decisions with score >= threshold, while the manuscript describes alarms
   with score > threshold.

4. **Run the attack-search experiment** (200 simulator evaluations for each family):

       python scripts/run_attack_search.py

   The script loads the Split A XGBoost checkpoint and uses its attack score as an
   offline oracle. This does not model stealthy queries to a live system. The score
   values themselves do not depend on the alarm threshold. NSGA-II is used over a
   small number of evaluations; near-saturated tree scores can make its ranking
   signal weak.

5. **Inspect the phase-residual output:**

       python scripts/test_physics_residual.py

   This script reports residual scalars for selected conditions. It does not set a
   PIAD alarm threshold, calculate FPR/TPR, or produce ROC/AUROC metrics. PIAD uses
   the simulated carrier state N, whose hardware observability is not established.
   The saved time step is about 1 ns, compared with a 1/gamma timescale of about
   10 ps; noise, bandwidth, and quantization effects are also absent.

6. **Recreate paper figures from the currently saved CSV files:**

       python scripts/generate_paper_figures.py

   This updates files under results/figures/. It does not regenerate model metrics
   or validate the saved CSVs.

The generation and training scripts overwrite existing outputs at the same paths.
Copy any results you need to preserve before rerunning them.

## Evaluation interpretation

- **Split A:** random grouped train/test assignment. Grouping keeps a trajectory's
  ten windows together, but it does not prevent identical deterministic nominal
  trajectories with different IDs from crossing the split.
- **Split B:** trains on standard operating parameters and tests on the two fixed
  simulated drift conditions. It is not a drift-magnitude sweep, and the current
  nominal class has no spontaneous-emission, phase, or measurement noise.
- **Split C:** the current split file overlaps nominal groups between train and
  test. Do not interpret its scores as leakage-free generalization.
- **Supervised metrics:** saved thresholds and thresholded metrics are provisional
  until recomputed under the revised policy. Windows from one trajectory are
  correlated; uncertainty should be estimated by resampling trajectories.
- **PIAD:** current outputs are condition-level residual values, not validated
  detection performance. The residual is a finite-difference numerical statistic
  computed from coarse, noise-free simulated samples.
- **Attack search:** minimum scores are minima among evaluated candidates, not
  lower bounds over the continuous parameter domains. No dense-grid landscape or
  run-to-run optimizer variance is currently reported.

## Open work

Before drawing broader conclusions, the benchmark needs disjoint splits and
stochastic measurement/phase noise; model metrics need regeneration with
trajectory-level uncertainty; drift response and held-out drift-hardening need
evaluation; and PIAD needs a calibrated threshold, matched-input baselines, and
noise/bandwidth testing. The attack study needs a dense parameter sweep and an
impact measure independent of classifier features. The simplified TWIRL input needs
a physically justified wavelength and locking-response model. Hardware validation
and protocol-level QKD analysis are outside the present repository's validated
results.
