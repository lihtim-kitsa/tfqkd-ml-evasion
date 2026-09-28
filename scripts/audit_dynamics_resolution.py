"""Compare fine-grid phase dynamics with downsampled finite-difference residuals.

This diagnostic uses the current deterministic simulator equations and initial
condition. It quantifies numerical sensitivity; it does not validate the model
against an optical device or establish a detector.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.simulator.oil_rate_equations import OILSimulator


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-ns", type=float, default=20.0)
    parser.add_argument("--step-ps", type=float, default=2.0)
    parser.add_argument("--output", default="results/tables/dynamics_resolution_audit.csv")
    args = parser.parse_args()

    sim = OILSimulator(kappa=1e9, alpha=3.0, gamma=1e11)
    current_amp = 2e17
    e_ref = 1.0
    phi_ref = 0.0

    def e_ref_func(_t):
        return e_ref

    def phi_ref_func(_t):
        return phi_ref

    def current_func(t):
        return current_amp * (1 + 0.01 * np.sin(2 * np.pi * 1e5 * t))

    duration = args.duration_ns * 1e-9
    dt = args.step_ps * 1e-12
    t = np.arange(0.0, duration + 0.5 * dt, dt)
    sol = solve_ivp(
        sim._rate_equations,
        (0.0, duration),
        [1.0, 0.0, 1e8],
        args=(e_ref_func, phi_ref_func, current_func),
        method="BDF",
        rtol=1e-6,
        atol=1e-9,
        max_step=dt,
        t_eval=t,
    )
    if not sol.success:
        raise RuntimeError(sol.message)

    E, phi, N = sol.y
    G = sim.g0 * (N - sim.N_tr) / sim.N_tr
    gain_term = 0.5 * sim.alpha * (G - sim.gamma)
    detuning_term = np.full_like(t, -sim.delta_omega)
    injection_term = sim.kappa * (e_ref / (E + 1e-12)) * np.sin(phi_ref - phi)
    rhs_phi = gain_term + detuning_term + injection_term

    rows = []
    max_dt = max(1, int(round(2.0e-9 / dt)))
    for stride in sorted(set([1, max(1, int(round(10e-12 / dt))), max_dt])):
        tt = t[::stride]
        pp = phi[::stride]
        h = tt[1] - tt[0]
        dphi = np.gradient(pp, h)
        model_rhs = rhs_phi[::stride]
        resid = dphi - model_rhs
        jump = np.abs(np.diff(pp)) > np.pi
        rows.append(
            {
                "sample_step_ps": h * 1e12,
                "points": len(tt),
                "phase_increment_abs_max_rad": float(np.max(np.abs(np.diff(pp)))),
                "increments_over_pi": int(jump.sum()),
                "phase_residual_mse_rad2_s2": float(np.mean(resid**2)),
                "phase_derivative_rms_rad_s": float(np.sqrt(np.mean(dphi**2))),
                "rhs_phase_rms_rad_s": float(np.sqrt(np.mean(model_rhs**2))),
                "simulated_duration_phase_ptp_rad": float(np.ptp(pp)),
                "E_min": float(np.min(E[::stride])),
                "E_max": float(np.max(E[::stride])),
            }
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {out}")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
