# Research Plan: Adaptive Evasion of ML Monitoring in Twin-Field QKD

## Working title

**When Eve Plays the Model: Mapping the Adaptive-Evasion Frontier of ML Monitoring for Optical-Injection-Locked Twin-Field QKD**

Short title: **Adaptive Robustness of ML-Based Attack Monitoring in OIL TF-QKD**

## Project charter

### Objective

Determine whether an attacker who chooses physically constrained reference-beam manipulations can meaningfully change simulated OIL-TF-QKD observables while keeping an ML monitor below its alarm threshold. Measure whether practical ML defenses move that boundary.

### Why this is worth doing

The supplied paper evaluates FIM and TWIRL detection on simulator-generated telemetry and reports one constrained FIM evasion search. Its limitations include shared simulator provenance between training and testing, a drift false-positive problem, and no broad query-budgeted adaptive-evasion study. Separate work has experimentally demonstrated OIL reference-beam attack scenarios. The next-step question is: **what does the monitor miss when an attacker adapts to it?**

A useful result may be either a robust detection region under the tested simulated threat model or a reproducible map of where the monitor becomes unreliable. Either result matters if the assumptions and limits are reported honestly.

### Main research question

> Over a pre-defined family of physically plausible simulated FIM, TWIRL, and combined inputs, what trade-off exists between attack impact on QKD-relevant observables and the probability that an ML monitor raises an alarm?

### Hypotheses to test

1. Random sample-level holdouts overestimate performance compared with splits that hold out entire operating regimes or contiguous attack-parameter ranges.
2. Query-budgeted optimization finds more low-alarm, high-impact cases than random search at the same simulator-evaluation budget.
3. Adversarial training and an uncertainty-based abstention policy can improve worst-case detection in some regimes, with possible costs in false alarms, abstentions, or inference time.
4. No single detector may perform well across every unseen regime. Report the boundary rather than hiding it in a pooled score.

### Intended contribution

A reproducible simulator-only benchmark and evaluation method for **adaptive, physics-constrained evasion of ML monitoring in OIL-based TF-QKD**, including:

- An attacker that controls simulator inputs rather than editing classifier features directly.
- Leakage-resistant evaluation splits.
- Adaptive attack search with explicit query budgets.
- Impact-versus-detectability frontiers.
- Baseline and defensive model comparisons.
- Clear separation between simulated evidence and hardware or composable-security claims.

This is a research target, not a guarantee of novelty or publication. Complete a focused literature review before claiming novelty or priority.

---

## Scope and claim boundaries

### In scope

- Reproducing the supplied paper’s main simulation and classifier results as far as available code allows.
- Generating simulations over attack controls and benign operating conditions.
- Searching for classifier-evasive inputs through the physical simulator.
- Testing models on held-out operating regimes and attack settings.
- Comparing at least one attack-aware defense and one uncertainty or abstention approach.
- Quantifying variation across simulation seeds, operating regimes, and repeated optimization runs.

### Out of scope

- Building optical hardware or executing attacks against a real QKD setup.
- Claiming the ML monitor makes TF-QKD secure.
- Claiming a composable security proof or finite-key bound.
- Treating simulator-derived success as evidence that real hardware can be compromised.
- Using accuracy as the only measure of detector quality.
- Optimizing abstract classifier features without producing a corresponding simulated physical trajectory.

### Safe description of results

Use wording such as:

> “We evaluated adaptive evasion within a stated numerical model of OIL-based TF-QKD. The findings characterize that simulator and threat model; hardware validation and protocol-level security certification remain open.”

Do not claim “the attack works on TF-QKD hardware,” “the system is insecure,” or “the detector guarantees security” from this project.

---

## Technical definition

### Variables

Represent one simulator run with:

- Operating conditions, theta: nominal and benign variations in laser/system parameters.
- Attack controls, a: FIM settings, TWIRL settings, or both.
- Stochastic conditions, xi: random seed, modeled noise, and stochastic measurement effects.
- Physical trajectory, z: simulated laser and reference-beam behavior over the observation window.
- Monitor features, x = g(z): telemetry supplied to the classifier.
- Monitor output, p_attack(x): predicted attack score and alarm decision.
- Impact observables, h(z): independently computed effects relevant to the QKD system, such as phase behavior or effective photon statistics.

The attacker must choose a, and every candidate must pass through the simulator before telemetry reaches the classifier.

### Keep monitor features and impact distinct

Choose and document the attack-impact measure before running the final test set. Keep the impact calculation conceptually separate from the classifier’s prediction.

The supplied paper’s monitored feature vector includes mean photon number, photon-number variance, sideband power, phase decoherence, and QBER. Reusing the same values as both model inputs and impact targets can make interpretation circular. Prefer simulator outputs representing downstream effects, or derive several impact axes and report them separately.

Possible impact axes to discuss with a QKD/optics supervisor:

- Deviation in phase coherence or phase-decoherence behavior.
- Deviation in effective photon statistics reaching the encoder or protocol.
- Change in another protocol-relevant estimate available from the selected simulator.

A conservative simulation-only flag can be “outside the benign operating envelope” for an impact observable. Estimate that envelope from benign calibration/validation simulations only and freeze it before testing. Crossing it is a **simulated out-of-envelope effect**, not automatically a security break.

If no physically meaningful impact measure can be defended, narrow the claim to **detector evasion under simulated feature shifts** and do not call those cases successful security attacks.

### Attacker objective

Use a constrained, multi-objective formulation:

1. Generate a valid simulated attack under a and operating condition theta.
2. Require a pre-defined minimum impact on at least one impact observable, or retain impact as a continuous axis.
3. Minimize the monitor’s attack score or evade its frozen alarm threshold.
4. Record simulator evaluations used.

The main figure should plot **attack impact against detection probability or alarm score**. A scalar objective may be used inside the optimizer, but report the separate axes and disclose the scalarization.

### Threat-model assumptions

State what the attacker knows and controls:

- Does the attacker know the detector family and alarm threshold?
- Can the attacker query the detector, or only transfer from a surrogate?
- Does the attacker know exact simulator/device parameters?
- Which optical control parameters are available?
- What bounds or operational constraints apply?
- Are FIM and TWIRL concurrent, sequential, or independently selected?
- What counts as a query: one simulator evaluation, one model evaluation, or one full observation?

Start with a **black-box, score-query attacker** as the primary setting. Add a transfer setting where the attacker optimizes a surrogate and evaluates candidates on a separately trained target. Do not assume white-box access without stating it.

---

## Phase-by-phase plan

The core study is planned for eight weeks. The first two weeks produce a defensible prototype and a go/no-go decision on expanding the study.

## Phase 0 — Setup and literature check

**Duration:** 1–2 days

### Tasks

1. Create a project folder and version-controlled repository.
2. Record the supplied paper’s bibliographic details, simulator parameter ranges, feature definitions, and stated limitations.
3. Locate the code and data identified by the supplied paper. Confirm license, code version/commit, dependencies, and whether the dataset can be regenerated.
4. Read the experimental OIL reference-beam attack paper. Identify which mechanisms and measured outputs it establishes. Use it to ground the threat model; do not treat it as data for your simulator unless downloadable data are explicitly provided.
5. Search for work on:
   - Adaptive attacks on ML-based physical-system monitors.
   - Robust evaluation under simulator/domain shift.
   - OIL TF-QKD implementation attacks and countermeasures.
   - Selective prediction or abstention under distribution shift.
   - QKD-specific detector/security analyses.
6. Create a one-page novelty table: closest work, what it tests, what it does not test, and the exact gap this project addresses.
7. Ask a QKD/optics researcher or faculty member to review the proposed impact observable and attack constraints if possible.

### Deliverables

- README with project purpose and claim boundary.
- Source notes with papers and novelty matrix.
- Working environment specification.
- One-page threat-model draft.

### Exit criteria

- You can identify the model inputs and attack controls in the supplied work.
- You know whether its simulator and repository are runnable.
- You have one defensible research gap distinct from the original paper.
- You have selected at least one impact observable and can explain its relevance.

### Go/no-go decision

If the source code is unavailable, incomplete, or irreproducible, decide whether to rebuild only the minimum simulator components or narrow to an independent implementation. Do not claim reproduction if you cannot reproduce it.

---

## Phase 1 — Reproduce the baseline

**Duration:** 3–5 days

### Tasks

1. Run the original pipeline in its documented configuration.
2. Record software versions, solver tolerances, random seeds, data-generation settings, train/test split, preprocessing, and classifier settings.
3. Reproduce the original train/test evaluation for XGBoost and Random Forest first.
4. Reproduce the benign-drift evaluation if its data-generation path is available.
5. Compare your results with the paper’s tables and figures. Record discrepancies instead of tuning until the numbers match.
6. Save generated data with a manifest describing simulation parameters, labels, feature definitions and units, seeds, split/group identifiers, and code version.
7. Establish an evaluation interface: input is a simulator-generated sample or trajectory; output includes model score, alarm decision, simulation metadata, and impact observables.

### Deliverables

- Reproduction script or notebook.
- Baseline table with per-class precision/recall, confusion matrix, and benign false-positive rate.
- Reproducibility notes listing mismatches.
- Machine-readable data manifest.

### Exit criteria

- One documented sequence regenerates the baseline.
- Results are explainable, even if they do not exactly match the paper.
- No final evaluation sample is used for preprocessing or model selection.

### Stop condition

If reproduction fails after a bounded troubleshooting period, document the failure. Proceed only if an independent simulator can be validated against known qualitative behaviors. Do not present new work as a reproduction.

---

## Phase 2 — Audit the simulator and define the benchmark

**Duration:** 4–6 days

### Tasks

1. Build a parameter inventory with attack controls, benign operating variables, solver/window settings, measurement-noise variables, monitor features, and impact observables.
2. Mark each parameter as supported by the source paper, taken from an external experimental source, an engineering assumption, or a synthetic stress-test value.
3. Check simple cases:
   - No attack, nominal conditions.
   - No attack, benign drift.
   - FIM only.
   - TWIRL only.
   - Combined attack, if supported.
4. Confirm units, feature scaling, clipping, invalid solver outputs, and label assignment.
5. Select an observation-window policy and test its sensitivity. The supplied paper notes that its window choice was not formally ablated.
6. Add a measurement chain only to a justifiable level. Candidate effects include bandwidth limitation, additive measurement noise, quantization, and missing samples. Label assumptions explicitly.
7. Choose parameter sampling:
   - Use space-filling or stratified sampling for broad coverage.
   - Use a separate local design near difficult boundaries.
   - Keep reproducible seed lists.
   - Avoid random train/test subsets of nearby trajectories.
8. Freeze benchmark v1 before final model evaluation.

### Data split design

Create separate split suites; do not collapse them into one score.

- **Split A — Reproduction:** random sample split, used only to compare with the original work.
- **Split B — Held-out operating regimes:** hold out entire groups of benign parameter combinations or operating envelopes.
- **Split C — Held-out attack ranges:** hold out contiguous intervals or combinations of FIM/TWIRL controls.
- **Split D — Shifted measurement conditions:** train on selected measurement-chain settings and test on unseen settings.
- **Split E — Combined-attack holdout:** if represented, train without some combined-attack cases and test them separately.

Group by trajectory/parameter cell and random seed. Keep related samples from one simulation run or operating configuration in one partition. Fit normalization and calibration on training/validation only.

### Deliverables

- Simulator parameter table with provenance and rationale.
- Benchmark v1 generator.
- Split manifest with group IDs and rationale.
- Simulator audit report and sanity plots.

### Exit criteria

- Every test sample is traceable to a held-out group.
- Impact is independent of classifier labels and final test data.
- A pilot timing run shows the design is computationally feasible.
- Unsupported physical values are not described as experimentally established.

---

## Phase 3 — Train reference detectors and set thresholds

**Duration:** 4–5 days

### Models

Keep the comparison focused:

1. Original supervised baseline: XGBoost.
2. Second tree baseline: Random Forest.
3. Simple reference: logistic regression or transparent threshold rule.
4. Optional anomaly baseline: one-class or density-based detector only if time and data support a fair comparison.

The question is adaptive robustness, not model count.

### Threshold setting

For each detector:

1. Train on training groups.
2. Tune on validation groups.
3. Select an alarm threshold on validation data to meet a predeclared benign false-alarm target that the simulation can estimate precisely enough.
4. Freeze the threshold before test evaluation.
5. Report achieved false-positive rate and uncertainty. If sample counts are too small to estimate it precisely, generate more benign simulations or report that limitation.

A threshold selected after inspecting test data invalidates the test estimate.

### Metrics

Report at least:

- Per-class recall and precision.
- Attack false-negative rate.
- Benign false-positive rate.
- Precision-recall curve.
- Detection probability at the frozen operating threshold.
- False alarms per fixed simulated observation volume, if windows are consistent.
- Inference latency on specified hardware, if measured.
- Calibration plot or Brier score.
- Results separately for each split suite.

Aggregate accuracy is secondary.

### Deliverables

- Frozen baseline models/configuration.
- Threshold-selection record.
- Baseline results by split and attack class.
- Memo choosing the primary target model.

### Exit criteria

- Thresholds were chosen without test-set inspection.
- Results are stratified by held-out domain.
- Model choice is not based solely on accuracy.

---

## Phase 4 — Build the adaptive attacker

**Duration:** 1–1.5 weeks

### Attack search levels

Implement in increasing difficulty:

1. **Random search baseline:** uniform or space-filling candidates over valid controls.
2. **Query-efficient black-box search:** Bayesian optimization or another suitable optimizer minimizes the detector score subject to physical-control bounds.
3. **Transfer evaluation:** optimize against a surrogate, then evaluate on the frozen target model.

Give methods equal simulator-evaluation budgets. Estimate runtime with a pilot, then set small, medium, and large budgets before viewing final test outcomes. Log every query, parameter vector, seed, solver status, score, and impact.

### Attack families

- FIM only.
- TWIRL only.
- Combined FIM+TWIRL, if simulator equations support it.
- Optional held-out control combinations for transfer tests.

Start with ranges described in the supplied paper and verify them against the source. Expand only with a source or explicit assumption. Do not optimize unconstrained abstract features.

### Candidate outcomes

Label every candidate:

- Invalid simulation or solver failure.
- Valid but below the predeclared impact criterion.
- Valid and impactful, detected.
- Valid and impactful, evaded the frozen detector.
- Valid and uncertain/abstained, if the policy includes abstention.

Log invalid solver runs but exclude them from successful-attack counts.

### Main outputs

For each attack family and test regime, record detector score/decision, impact vector, simulator parameters, query budget, regime status, optimizer, and seed.

Produce:

1. Impact-versus-detection scatter/contour plots.
2. Non-dominated Pareto frontiers.
3. Evasion rate versus query budget.
4. Adaptive search versus random search at matched budgets.
5. Examples with assumptions clearly labeled.

### Deliverables

- Attack-search scripts.
- Complete query logs.
- Attack-success and invalid-run definitions.
- First evasion-frontier figures.
- Updated threat model.

### Exit criteria

- The attack uses simulator controls only.
- Search methods receive comparable budgets.
- Impact thresholds were frozen before final search.
- Results reproduce across independent seeds to a reported degree.

---

## Phase 5 — Evaluate defenses

**Duration:** 1 week

Keep two defenses in the main study.

### Defense A — Adversarial or hard-case training

1. Generate attack candidates using training/validation data only.
2. Add a controlled subset of valid, high-impact, low-score candidates to training.
3. Retrain the classifier.
4. Tune its threshold on validation groups.
5. Evaluate on untouched, newly generated adaptive attacks and held-out regimes.

Never train on final adaptive test candidates.

### Defense B — Uncertainty/abstention

Choose one method, for example an ensemble disagreement score, calibrated predictive uncertainty, or a conformal prediction set with an explicit abstain/review outcome.

Set its threshold on validation data. Report attack detection and abstention burden. In-distribution calibration does **not** guarantee validity under domain shift; test and report shifts directly.

### Optional Defense C — Drift-aware training

Add only if drift is not already adequately represented. Test whether it changes adaptive evasion as well as benign false alarms.

### Comparison table

For each model/policy report benign false-positive rate, attack recall by family, impactful-evasion rate, abstention rate, query budget to find an evasion, held-out-regime performance, and computation/inference cost.

### Deliverables

- Frozen defense configurations.
- Training-data lineage.
- Before/after evasion frontier.
- Results table including false alarms and abstentions.

### Exit criteria

- No defense has seen final attack candidates.
- Methods use comparable benign false-alarm operating points.
- Abstention is reported as an operational outcome.

---

## Phase 6 — Statistical analysis and robustness checks

**Duration:** 4–6 days

### Required analysis

1. Repeat generation and optimization across independent seeds. Use a pilot to determine scale; aim for at least 10 independent repeats for key comparisons if feasible.
2. Compute uncertainty intervals for detection probability, false-positive rate, impactful-evasion rate, query budget, and Pareto-frontier summaries.
3. Resample at the group or operating-regime level, not only by individual examples, because examples within one simulation condition are correlated.
4. Compare methods on paired evaluation groups where possible.
5. Show class confusion and per-regime outcomes. Account for failed/invalid optimization runs.
6. Ablate random versus grouped split, measurement effects, attack family, search budget, and defense components.
7. Check leakage: training-only preprocessing; no shared trajectory groups; no test-driven thresholds or hyperparameters; no test candidates in adversarial training.
8. Maintain a result ledger linking each plotted point to configuration, code version, model, seed, and sample.

### Deliverables

- Analysis script/notebook.
- Group-aware confidence intervals.
- Ablation table.
- Leakage audit.
- Frozen result bundle and manifests.

### Exit criteria

- Main conclusions survive repeats or are qualified as unstable.
- Results are shown by regime, not only pooled.
- Simulator-assumption uncertainty is distinguished from sampling uncertainty.

---

## Phase 7 — Write, package, and share

**Duration:** 1 week

### Paper structure

1. Abstract: question, simulator-only scope, method, central measured result.
2. Introduction: OIL reference-path issue; why random holdouts do not answer adaptive robustness.
3. Related work: experimental OIL attacks, ML monitoring in QKD, adversarial robustness in physical systems.
4. Threat model: attacker knowledge, controls, constraints, query budget, impact criterion.
5. Simulator and benchmark: equations/source, parameter provenance, noise assumptions, splits.
6. Methods: classifiers, threshold policy, search algorithms, defenses.
7. Results: baseline, held-out regimes, adaptive frontier, defenses, uncertainty.
8. Limitations: simulator provenance, unvalidated measurement assumptions, no hardware, no composable-security proof.
9. Conclusion: findings within the simulator and next validation step.

### Reproducibility package

Include pinned dependencies, configs, data-generation and analysis scripts, manifests/split IDs, query logs or regeneration instructions, fixed seeds, figures from saved results, model cards, licenses/citations, and a clean reproduction path.

Do not upload generated datasets unless size/license permits. Provide scripts/manifests or a research-data archive.

### Deliverables

- 6–10 page paper or technical preprint draft.
- Reproducible repository.
- One-page CV/interview summary.
- Three core figures: threat model/evaluation pipeline; impact-versus-detection frontier; defense comparison across held-out regimes.

### Final claim review

Search for unsupported claims of hardware validation, actual exploitation, security certification, universal performance, or first-ever novelty. Replace them with precise bounded statements.

---

## Two-week minimum-result sprint

This is a prototype milestone, not a promise that a publishable paper will be finished in 14 days.

### Days 1–2: inspect and run the source

- Locate and run the supplied code.
- Record dependencies, seeds, features, attack controls, and outputs.
- Start a results ledger.
- Choose the one impact observable you can defend.

**Output:** baseline run or documented blocker and narrowed scope.

### Days 3–4: make leakage-resistant splits

- Preserve a random split for comparison.
- Create one grouped split holding out full operating/attack-parameter groups.
- Verify group separation and freeze train/validation/test IDs.

**Output:** split manifest and diagram.

### Days 5–6: reproduce and freeze a detector

- Train XGBoost and Random Forest.
- Choose one primary detector using validation results and false-alarm behavior.
- Freeze threshold on validation only.
- Evaluate both split types.

**Output:** baseline comparison and first domain-shift result.

### Days 7–9: implement constrained black-box search

- Start with the best-supported attack family in the available simulator.
- Implement random search, then one query-efficient optimizer.
- Log every candidate.
- Freeze the search configuration before using final test data.

**Output:** query logs and first impact-versus-detection plot.

### Days 10–11: add one defense

- Choose adversarial training or uncertainty/abstention.
- Train/tune using training/validation groups only.
- Evaluate on fresh adaptive-search candidates.

**Output:** baseline-versus-defense frontier.

### Days 12–13: uncertainty and figures

- Repeat key runs across seeds if feasible.
- Add uncertainty intervals and per-regime breakdown.
- Audit group leakage, thresholds, and query budgets.
- Write figure captions and limitations.

**Output:** three core figures and result ledger.

### Day 14: package the prototype

- Write a concise 4–6 page report.
- Publish a clean repository or shareable private repo.
- Add README and one-page summary.
- Decide whether to expand, narrow the question, or address a simulator limitation.

**Output:** a reviewable artifact you can discuss honestly.

---

## Suggested repository structure

    adaptive-oil-qkd/
      README.md
      LICENSE
      CITATION.cff
      environment.yml
      configs/
        simulator.yaml
        splits.yaml
        baseline.yaml
        attack_search.yaml
        defenses.yaml
      src/
        simulator/
        features/
        data/
        models/
        attacks/
        defenses/
        evaluation/
      scripts/
        generate_data.py
        make_splits.py
        train_baselines.py
        run_attack_search.py
        train_defenses.py
        evaluate_all.py
      results/
        manifests/
        tables/
        figures/
      reports/
        threat_model.md
        simulator_audit.md
        paper_outline.md
      notebooks/
        exploratory_only/

Keep notebooks for exploration. Put final experiments in scripts/configs so results can be regenerated without manual notebook state.

---

## Decision gates and fallback paths

### Gate 1 — Simulator access

If paper code/data cannot be run, spend a fixed short period investigating. Then rebuild only minimum model components with a supervisor or narrow to a methodological benchmark. Do not claim reproduction.

### Gate 2 — Defensible impact measure

If no impact observable can be defended, report **evasion of simulated ML classification under parameter shift**, not a security-impact frontier. Ask a QKD/optics researcher for review before broadening the claim.

### Gate 3 — Combined attacks

If combined FIM+TWIRL is unsupported by the equations or assumptions, keep the main study to separate attack families and list combinations as future work.

### Gate 4 — Runtime

If simulation is too slow, run a smaller transparent pilot. Use a surrogate only to rank candidates; evaluate all final candidates through the original simulator and label surrogate-assisted search.

### Gate 5 — Weak or negative result

If no evasion is found, report search budgets and confidence limits. “No evasion found under the tested model/budget” is valid; “no evasion exists” is not.

---

## Success criteria

The project succeeds if it delivers:

1. A clear, bounded threat model.
2. A reproducible baseline or transparent report of why reproduction was impossible.
3. A grouped test protocol that prevents operating-condition leakage.
4. An attack search through simulator controls with stated constraints.
5. A predeclared, independently computed impact measure.
6. Fair comparison at frozen validation thresholds.
7. Per-regime metrics and uncertainty estimates.
8. A complete result ledger and runnable analysis.
9. Conclusions that distinguish simulator evidence from hardware security.

High attack success is not required. The contribution is the quality of the question, experiment, and evidence.

## First working session checklist

- [ ] Create the repository and put the one-sentence objective in README.
- [ ] Read the supplied paper’s methodology, limitations, and cited OIL attack source.
- [ ] Find its referenced code/data; record version and license.
- [ ] Run one nominal, one benign-drift, one FIM, and one TWIRL case if supported.
- [ ] Write down the monitor features and separate impact observable.
- [ ] Draft attacker knowledge/control assumptions.
- [ ] Set a two-day limit for resolving code/simulator blockers.
- [ ] Do not tune on the final test split.

## Starting sources

- User-supplied base paper: *ML-Based Attack Detection for Twin-Field QKD with Optical Injection Locking*. Use its stated repository and citations as starting points; verify availability, code provenance, and license before reuse.
- Juárez et al., “Reference-beam attacks against twin-field quantum key distribution using optical injection locking,” *Physical Review A* 113, 032613 (2026): https://journals.aps.org/pra/abstract/10.1103/71m5-3c5n
- CERN Applied Physics Technical Studentship (for transferable skill framing, not as validation of project fit): https://careers.cern/jobs/tsc-ap/

