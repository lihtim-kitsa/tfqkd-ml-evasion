# Project Brief for CERN Applications

## Project

**Numerical and data-quality audit of an OIL TF-QKD monitoring simulation**

## One-sentence summary

Built reproducible Python diagnostics for a laser-dynamics and machine-learning
monitoring pipeline, then used them to identify duplicated trajectories and strong
sampling dependence that made the saved model metrics unreliable.

## What the project demonstrates

- **Scientific computing:** working with stiff ordinary differential equations,
  solver tolerances, temporal resolution, and finite-difference estimates using
  SciPy.
- **Signal and data analysis:** time-series sampling, phase increments, FFT-derived
  features, Parquet data, and trajectory-level grouping with NumPy and pandas.
- **ML evaluation:** understanding how data leakage and non-independent samples can
  make classifier metrics look stronger than the evidence supports.
- **Research practice:** writing reproducible diagnostics, stating model assumptions,
  distinguishing simulation output from measurement, and correcting conclusions
  when an audit exposes a flaw.

## Concrete work and findings

I added two scripts that can be rerun from the repository root:

- `scripts/audit_benchmark.py` hashes ordered feature traces and checks train/test
  overlap. It found that the 150 nominal group IDs reduce to three distinct traces
  (one per operating condition); Split A shares three exact traces across train and
  test, while Split C shares 150 group IDs.
- `scripts/audit_dynamics_resolution.py` integrates the current rate equations on a
  fine grid, then compares finite-difference phase residuals at coarser output
  intervals. For the documented 100 ns diagnostic, the residual MSE changes from
  about `2.9e15` at 2 ps spacing to `4.1e20` at 2 ns spacing. This exposed a
  numerical-resolution problem in the earlier residual analysis.

These are findings about the repository's simulation and saved data. They are not
measurements of a QKD device and do not establish an operational attack detector.

## CV bullets

Choose and adapt only the bullets that accurately describe your contribution:

- Developed reproducible Python audits for a laser-dynamics/ML pipeline, using
  trajectory fingerprints to identify duplicated nominal simulations and
  train/test leakage.
- Quantified time-resolution sensitivity in a stiff ODE monitoring workflow by
  comparing phase-residual estimates across picosecond-to-nanosecond sampling.
- Applied SciPy, NumPy, pandas, and signal-processing methods to diagnose how
  numerical and data-design choices affect machine-learning evaluation.
- Documented simulator assumptions and separated computational findings from
  claims requiring experimental validation.

## Short interview description

> I worked on a Python simulation and ML-monitoring project for optical injection
> locking in a QKD context. Rather than rely on the original headline metrics, I
> added reproducible audits for trajectory duplication and time-sampling effects.
> Those checks showed that the nominal data were not independent and that the
> physics-residual score changed dramatically with sampling interval. The main
> result was a more reliable assessment of what the simulation could—and could
> not—support. The transferable part for an applied-physics role is careful work
> with dynamic systems, sampled signals, and evidence quality.

## Tailoring for CERN

For an **Applied Physics** or **Electrical/Electronics** application, emphasize
numerical modeling, time-series sampling, signal processing, and the discipline to
validate a measurement pipeline before interpreting results. For an **IT, Data
Science, or Mathematics** application, emphasize reproducible Python tooling,
data-quality audits, ML evaluation, and leakage-resistant analysis.

Do not present this as accelerator, radiation, or hardware-instrumentation
experience. It is a computational project whose methods transfer to measurement
and scientific-data workflows. Connect it to the specific duties and required
skills in the vacancy you apply for.
