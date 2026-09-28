# Simulator Audit: Current Evidence and Open Validation

This audit supersedes the earlier single-window summary, which treated the
phase peak-to-peak value as an independent physical-impact measure. That claim was
not justified because phase-derived monitor features encode related information.

## Implemented equations and telemetry

`src/simulator/oil_rate_equations.py` integrates amplitude, phase, and carrier
number with a BDF solver. The benchmark samples a 1 microsecond trajectory at about
1 ns spacing, starting from `(E, phi, N) = (1, 0, 1e8)`. The current data-generation
script uses deterministic operating conditions and deterministic current ripple.
The nominal `seed` does not introduce noise or other trajectory-level variation.

The feature extractor computes mean and variance of `|E|^2`, an FFT sideband
quantity, phase RMS, and a synthetic QBER proxy. The QBER proxy is calculated from
the other features and is not an independently measured QBER. The carrier state
used by the phase-residual script has no demonstrated hardware-observable input.

## Reproducible diagnostics

Run:

```powershell
python scripts\audit_benchmark.py
python scripts\audit_dynamics_resolution.py --duration-ns 100 --step-ps 2
```

The benchmark audit hashes ordered feature traces. It finds 50 nominal group IDs
but one distinct trace in each of the standard, kappa-drift, and alpha-drift
conditions. Split A shares three exact traces across train and test even though
group IDs are disjoint; Split C shares 150 group IDs. See
`reports/benchmark_audit.md`.

The dynamics audit integrates the current model over 100 ns with a 2 ps maximum
solver step, then computes phase finite-difference residuals after decimation. The
residual MSE is about `2.9e15`, `9.3e17`, and `4.1e20 rad^2/s^2` at 2 ps, 10 ps, and
2 ns output, respectively. At 2 ns, two adjacent phase increments exceed pi. The
trajectory phase range is about 24.5 rad, and field amplitude spans about 0.0037 to
1012. See `results/tables/dynamics_resolution_audit.csv`.

These are numerical sensitivity results for the checked-in equations, settings,
and initial state. They do not validate the model against an OIL device, establish
that the initial transient is realistic, or demonstrate PIAD performance.

## Attack-input limitations

FIM uses sinusoidal reference-amplitude modulation over 100 MHz–10 GHz, while
saved telemetry at approximately 1 GS/s has a 500 MHz Nyquist limit. The FIM
search therefore includes frequencies that cannot be resolved without aliasing
analysis.

The TWIRL injector calculates an approximate frequency shift from wavelength, but
the ODE receives a hand-set phase ramp. It does not represent an out-of-band optical
path, wavelength-dependent reflections, watchdog response, or spectral filtering.
This model cannot support physical TWIRL claims.

## Validation needed before interpretation

- Domain-expert review of equations, units, optical-field normalization, injection
  ratio, locking range, and initial or steady state.
- Measurement-chain model with justified bandwidth, sampling, noise, and
  quantization. Solver resolution and telemetry resolution must be separate.
- Independent stochastic trajectories and a traceable calibration manifest.
- Disjoint splits at the trace and operating-condition level.
- A deployable input set and independent, protocol-relevant outcome if making
  detector-impact claims.
- A physically justified TWIRL model or removal of TWIRL from the study.
