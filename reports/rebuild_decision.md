# Research Rebuild: Decision and Evidence Gates

## Recommendation

Do not submit the current manuscript as a journal article. The saved benchmark and
the current simulator do not support independent trajectory-level performance
claims, and the current TWIRL input does not model the experimentally described
out-of-band optical signal. The best next step is a validated study of monitoring
under benign variation and reference-beam manipulation, built around a calibrated
measurement chain. Keep the work simulator-only unless a hardware collaborator can
provide traceable measurements.

This is a research direction, not a claim that a journal-ready result already
exists. Journal quality will depend on new evidence, independent review, and a
defensible contribution after literature comparison.

## What the current audit establishes

The repository diagnostics reproduce the following facts from the code and saved
artifacts:

1. The `seed` in `scripts/generate_data.py` affects randomized attack parameters,
   but the three nominal conditions are deterministic. Each has 50 group IDs and
   one distinct feature trace.
2. Split A assigns three identical feature traces across its train/test partitions.
   Split C has 150 shared nominal group IDs. Neither supports an independent
   nominal test estimate.
3. The simulator begins at `(E, phi, N) = (1, 0, 1e8)`. With the stated parameters,
   the gain is initially zero while the cavity decay term is `1e11 s^-1`. A 100 ns
   fine-grid run reaches field amplitudes from about 0.0037 to 1012 and accumulates
   about 24.5 rad peak-to-peak phase. This is a strong start-up transient; whether
   it represents any deployed operating point is unknown.
4. Under the same deterministic equations, the phase-residual MSE changes from
   `2.9e15` at 2 ps output to `4.1e20` at 2 ns output over the 100 ns diagnostic.
   The coarse trace includes phase increments above pi. Thus the existing PIAD
   scalar is strongly resolution-sensitive and cannot be treated as an alarm
   statistic until its numerical and measurement behavior is rebuilt.
5. The simulator sets `E_ref = 1`, while the laser field rapidly becomes much
   larger. This makes the modeled injection term small over much of the trajectory.
   The normalization of these field amplitudes and their mapping to optical power
   have not been established.
6. The FIM sweep extends above the 500 MHz Nyquist limit of the saved 1 GS/s
   telemetry. The TWIRL injector computes a wavelength-related frequency shift but
   the ODE input is instead a hand-set phase ramp. Neither sweep should be called
   physically constrained until these mappings are justified.

Reproduce the audits with:

```powershell
python scripts\audit_benchmark.py
python scripts\audit_dynamics_resolution.py --duration-ns 100 --step-ps 2
```

Outputs are `reports/benchmark_audit.md` and
`results/tables/dynamics_resolution_audit.csv`.

## Stronger paper concept

### Working question

**When does a monitor of OIL laser telemetry distinguish adversarial reference
manipulation from benign device and measurement variation, under a validated
measurement model?**

The primary contribution should be an evaluation protocol plus validated evidence,
not the claim that one ML algorithm is inherently secure. A stronger paper would
report how detector performance changes with operational variation, observation
bandwidth, and attack controls; it would include a physically meaningful outcome
only if that outcome can be validated against protocol or device measurements.

The 2026 experimental study by Juárez et al. establishes FIM and out-of-band
reference-signal scenarios and discusses optical watchdog/filter countermeasures.
The present TWIRL phase-ramp rule does not implement that out-of-band optical
pathway. The broader idea of adaptive ML intrusion detection for QKD also appears
in a 2026 simulation preprint for decoy-state systems. A novelty claim must
therefore be narrow and OIL-specific, and compared against both bodies of work:
[Juárez et al., *Physical Review A* (2026)](https://doi.org/10.1103/71m5-3c5n) and
[Mohamed & Al-Kuwari (2026 preprint)](https://arxiv.org/abs/2603.03502).

## Evidence gates

### Gate 1 — model and observable validity

- Obtain a domain-expert review of the rate equations, units, field normalization,
  injection ratio, initial state, and OIL locking conditions.
- Replace the arbitrary initialization with either a justified steady-state solve
  or a documented warm-up/cropping procedure. Verify the selected operating point.
- Rebuild TWIRL around a measured or cited optical path (wavelength-dependent
  transmission/reflection, watchdog response, and filtering); do not map large
  wavelength offsets to a phase ramp inside a locking equation.
- Define the detector observation chain: optical/electrical bandwidth, sampling,
  noise, quantization, and feature computation. Separate solver step from measured
  telemetry rate.
- Use only quantities available to the proposed monitor. Remove simulated carrier
  number from any deployable detector unless a sensor and measurement model exist.
- Replace the synthetic QBER proxy with protocol outputs, or name it explicitly as
  a toy feature and exclude it from QKD-level claims.

### Gate 2 — independent data and calibrated nuisance variation

- Generate independent stochastic trajectories with explicit random variables and
  a seed manifest. Do not count duplicated traces as separate runs.
- Set variation ranges from measured device data, experimental papers, or clearly
  labeled sensitivity analysis. Do not call arbitrary jitter “realistic noise.”
- Hold out entire trajectories and condition ranges. No feature-trace hash or
  parameter cell may cross train, calibration, and final test partitions.
- Include drift magnitude curves and held-out drift types/magnitudes.
- Use trajectory-clustered confidence intervals and repeat model fitting across
  seeds; do not treat correlated windows as independent observations.

### Gate 3 — fair detector comparison

- Freeze the primary threshold on independent nominal calibration trajectories at a
  declared false-alarm target.
- Compare supervised classifiers with nominal-only methods (for example robust
  Mahalanobis distance, Isolation Forest, and one-class SVM) using the same inputs.
- Report per-attack ROC/AUROC, TPR at the frozen threshold, FPR with uncertainty,
  calibration behavior, and performance by operating regime.
- Test noise and bandwidth changes. Include an adaptive attack against every
  proposed detector if attack robustness is a central claim.

### Gate 4 — adaptive search and impact

- Freeze attack parameter bounds from verified physics or experimental evidence.
- Use dense parameter sweeps for low-dimensional controls before evolutionary
  search; report score landscapes, repeated optimizer seeds, query budget, and
  comparisons with random search.
- Report alarm outcomes at a fixed calibrated threshold, and keep raw score
  separate from alarm decisions.
- Only describe candidates as high-impact if an independent, validated device or
  protocol observable supports that designation. Otherwise call the result a
  detector-score landscape.

## Scope boundary

The strongest claim available from the current repo is that its saved benchmark,
split design, PIAD residual, and TWIRL input need revalidation. That audit is useful
as an internal result, but it is not by itself a strong journal contribution.
Hardware measurements, calibrated simulator parameters, or a well-validated
protocol-level model are the main additions that could turn this into a compelling
paper. If those are unavailable, narrow the project to a reproducible methods
benchmark and make no hardware-security or key-rate claims.
