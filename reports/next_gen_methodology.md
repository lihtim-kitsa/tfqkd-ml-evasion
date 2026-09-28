# Status of Earlier Exploratory Extensions

This file replaces an earlier proposal that described the PINN residual as a
zero-shot defense and a differentiable Neural ODE as a white-box attack. Those
claims were unsupported and conflict with the revised analysis; the original
language has been retired.

## Physics residual

The checked-in `scripts/test_physics_residual.py` produces condition-level values
from finite differences on a 1 ns output grid. It has no calibrated threshold,
ROC/TPR analysis, noise model, or hardware-observable input specification. The
new `scripts/audit_dynamics_resolution.py` shows that the scalar changes by orders
of magnitude with output spacing. It should be treated as a numerical diagnostic,
not as evidence for a detector.

## Neural ODE experiment

The exploratory training script did not establish a successful or numerically
validated adaptive attack. State magnitudes and timescales were not nondimensionalized,
and the attempted optimization did not converge. It is not part of the current
paper's claims or evidence. A future differentiable-attack study would need a
validated simulator, converged gradients, and comparison against query-matched
black-box methods before it could support a contribution.

## Re-entry criteria

Revisit either direction only after simulator calibration, independent stochastic
trajectories, matched observation models, and frozen evaluation splits are in
place. Do not describe either component as a defense or attack result based only
on the present exploratory scripts.
