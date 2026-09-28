# Reproduction Status

## Baseline code and saved metrics

The repository contains generated data, model checkpoints, and result tables from
an earlier run. They are preserved for provenance, but the current validation
audits show they should not be interpreted as independent-trajectory evidence.
In particular, the nominal class is duplicated by condition, Split A leaks exact
nominal feature traces across partitions, and Split C reuses nominal groups across
train and test. Threshold-dependent metrics also need regeneration under the
revised threshold policy.

The earlier note that the baseline had been “fully reproduced” and that the drift
results “confirm” monitor failure was too strong. It did not account for trajectory
duplication, group leakage, or the lack of randomized nominal variation. The saved
percentages are historical output, not validated estimates of device performance.

## Reproduction workflow

1. Recreate the current benchmark using `python scripts\generate_data.py` only when
   preserving the existing Parquet file is not required. The generator overwrites
   `data/benchmark_v1.parquet`.
2. Run `python scripts\audit_benchmark.py` to count distinct trajectories and test
   group/hash overlap.
3. Run `python scripts\audit_dynamics_resolution.py --duration-ns 100 --step-ps 2`
   to inspect output-resolution sensitivity in the deterministic simulator.
4. Do not use current saved tables as final metrics. New data must first include
   independent, justified trajectory variation; then splits, models, calibration
   thresholds, and trajectory-level uncertainty must all be regenerated.

## Reproduction limits

Regeneration reproduces the current code, not an experimentally validated OIL
system. The TWIRL phase ramp, telemetry measurement chain, initialization, noise
model, and normalization of optical field amplitude still require validation.
Reproducibility of software output is not evidence that the simulated operating
conditions match hardware.
