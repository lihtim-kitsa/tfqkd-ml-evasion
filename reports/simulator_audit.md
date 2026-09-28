# Simulator Audit and Initial Benchmarking

## Parameter Inventory and Monitor Features
The Lang-Kobayashi simulator (`sim/oil_rate_equations.py`) models an injection-locked semiconductor laser and extracts five observable features per window (`data/feature_extraction.py`):
1. **$\mu$ (Mean Photon Number):** The average photon count in the simulated window.
2. **$\sigma^2$ (Photon Number Variance):** The variance of the photon count.
3. **$P_{sb}$ (Spectral Sideband Power):** An estimate of out-of-band spectral power, obtained via FFT.
4. **$\Delta\phi$ (Phase Decoherence):** The root-mean-square (RMS) phase error over the window.
5. **QBER (Quantum Bit Error Rate):** A synthetically derived value from $\Delta\phi$ and $\sigma^2/\mu$.

## Impact Observable
To separate the classifier inputs from the attack success criterion (as mandated by the research plan), we define the independent **impact observable** as the **Peak-to-Peak Phase Deviation** ($max(\phi) - min(\phi)$) across the entire simulated window. This represents a protocol-relevant downstream effect (maximum phase mismatch) that is not directly fed into the classifier as an averaged feature. 

## Test Runs (Single Window, 1000 points)
| Case | $\mu$ | $\sigma^2$ | $P_{sb}$ | $\Delta\phi$ (RMS) | QBER | Peak-to-Peak Phase Dev (Impact) |
|---|---|---|---|---|---|---|
| **Nominal** | $1.66 \times 10^5$ | $1.88 \times 10^8$ | $9.62 \times 10^6$ | $0.339$ | $58.87$ | $22.38$ |
| **Benign Drift** | $1.96 \times 10^5$ | $1.96 \times 10^8$ | $9.79 \times 10^6$ | $0.340$ | $60.04$ | $22.40$ |
| **FIM Attack** | $1.66 \times 10^5$ | $1.86 \times 10^8$ | $10.09 \times 10^6$ | $0.358$ | $58.22$ | $22.67$ |
| **TWIRL Attack** | $0.001$ | $0.0009$ | $9.36$ | $5778.91$ | $577.9$ | $199954.38$ |

**Observations:**
- Nominal and Benign Drift display similar profiles.
- FIM modulates the signal stealthily: peak-to-peak phase deviation increases slightly, but other parameters remain close to nominal.
- TWIRL causes extreme deviation in all phase-dependent features and disrupts the laser completely.
