# Adaptive Robustness and Attacker Evasion Results

## Bayesian Optimization Threat Model
We implemented a black-box optimizer (`optuna`, NSGA-II) constrained to physical controls:
- **FIM Controls:** Modulation depth $m \in [0.05, 0.40]$ and frequency $f_{fim} \in [100\text{ MHz}, 10\text{ GHz}]$.
- **TWIRL Controls:** Wavelength detuning $\Delta\lambda \in [0.1, 5.0]\text{ nm}$.
- **Objective:** Simultaneously minimize the ML detector's output attack score and maximize the downstream physical impact (Peak-to-Peak phase deviation).

## FIM Evasion Findings
The optimizer searched 200 attack candidates and mapped a Pareto front against the XGBoost classifier (baseline).
- The best evasion achievable dropped the ML probability score to **0.887**.
- At this probability, the physical impact was **22.26 rad** phase deviation (near-nominal, highly stealthy).
- Attempting to increase impact to 23.37 rad immediately raised the detection score to **0.997**.
- **Conclusion:** FIM evasion is tightly constrained by the physical simulator. The attacker cannot significantly perturb the system phase without tripping the classifier's features ($\mu$, $\sigma^2$, $P_{sb}$).

## TWIRL Evasion Findings
The optimizer searched 200 TWIRL variants.
- The lowest possible detection score found was **0.995**.
- TWIRL fundamentally disrupts the laser locking dynamics. Even at minimal detuning ($\Delta\lambda \approx 0.32$), the impact surges to 131 rad. 
- Higher impacts ($\sim 40,000$ rad) max out the detection score at **1.00**.
- **Conclusion:** TWIRL is extremely detectable. The attacker cannot tune TWIRL to evade this XGBoost monitor within the simulated parameters. 

## Final Takeaway
The ML-based monitor exhibits excellent robustness against adaptive zero-order query attacks constrained by physical injection mechanisms. However, as demonstrated in Phase 2, this robustness is deeply fragile to benign out-of-distribution drift, requiring drift-aware training or abstention policies to maintain operational viability.
