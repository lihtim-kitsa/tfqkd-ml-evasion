# Threat Model: Adaptive Evasion in OIL TF-QKD

## Attacker Knowledge and Capabilities
- **Black-box access (primary setting):** The attacker can query the detector to obtain a score but does not have direct access to the model weights or architecture.
- **Transfer setting:** The attacker can optimize an attack against a surrogate model and transfer it to the target detector.
- **System knowledge:** The attacker knows the general principles of the OIL-based TF-QKD system but not necessarily the exact simulator/device parameters.

## Attack Controls and Constraints
- The attacker manipulates the reference beam using fast intensity modulation (FIM) and/or additional signals (TWIRL).
- The attacker is physically constrained and must operate within plausible parameter ranges for these manipulations.
- Candidate attacks must pass through the physical simulator before telemetry reaches the classifier.

## Attacker Objective
1. Generate a valid simulated attack under chosen attack controls ($a$) and operating condition ($\theta$).
2. Achieve a pre-defined minimum impact on at least one impact observable (e.g., phase decoherence or effective photon statistics).
3. Minimize the ML monitor's attack score to evade its alarm threshold.
