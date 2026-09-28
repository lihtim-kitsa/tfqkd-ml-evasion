# Current Threat-Model Status

The checked-in experiments do **not** yet instantiate a validated physical threat
model. This note separates what the code currently does from what a future study
would need to establish.

## Implemented experiment

- Attack controls are the simulator inputs in `src/simulator/attack_injectors.py`:
  reference-amplitude modulation for FIM and a simplified phase ramp for TWIRL.
- Candidate trajectories pass through the deterministic OIL rate-equation code
  before features are extracted.
- The search script reads a saved XGBoost score offline. It does not query a live
  monitor or establish that such an oracle is available to a real attacker.
- FIM frequency bounds exceed the 1 GS/s telemetry Nyquist limit; candidate
  frequencies therefore require alias-aware interpretation.
- The TWIRL implementation is not a calibrated wavelength-to-frequency or
  injection-locking model.

Consequently, the existing experiment supports only a bounded software study over
the implemented input functions. It does not establish feasibility on hardware,
access to monitor scores, or a security impact on TF-QKD.

## Requirements for a future threat model

Before treating score-based optimization as an attacker capability, specify
whether the score comes from an offline surrogate, a lab replica, or an exposed
live interface, and account for alarm consequences and query cost. State which
model and device parameters are known or estimated.

Attack bounds must be grounded in the cited experimental setup or explicitly
identified as synthetic stress-test bounds. FIM and TWIRL should be modeled
separately unless a validated combined-input model is available.

An impact requirement must be defined using a protocol- or device-relevant output
that is independent of monitor features. If no such observable is validated, report
only detector-score behavior and do not label a candidate a successful QKD attack.
