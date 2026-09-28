"""Audit trajectory independence and split leakage in a saved benchmark.

This is a diagnostic only: it does not modify the dataset, split file, or model
results. Trajectories are compared by their ordered feature arrays, so duplicated
nominal simulations with different group IDs are counted as one effective trace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = ["mu", "sigma2", "Psb", "delta_phi", "qber"]
META = ["case_type", "op_regime", "attack_regime", "seed", "group_id"]


def trajectory_fingerprint(frame: pd.DataFrame) -> str:
    ordered = frame.sort_values("window_idx" if "window_idx" in frame else frame.index.name)
    values = ordered[FEATURES].to_numpy(dtype=np.float64)
    return hashlib.sha256(values.tobytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/benchmark_v1.parquet")
    parser.add_argument("--splits", default="configs/splits.json")
    parser.add_argument("--output", default="reports/benchmark_audit.md")
    args = parser.parse_args()

    data_path = Path(args.data)
    split_path = Path(args.splits)
    df = pd.read_parquet(data_path)
    required = set(FEATURES + META)
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if "window_idx" not in df:
        df = df.copy()
        df["window_idx"] = df.groupby("group_id").cumcount()

    group_meta = df.groupby("group_id", sort=False)[META[:-1]].first()
    signatures = {
        group_id: trajectory_fingerprint(part)
        for group_id, part in df.groupby("group_id", sort=False)
    }
    group_meta["trajectory_hash"] = pd.Series(signatures)

    lines = [
        "# Benchmark Independence Audit",
        "",
        f"Dataset: `{data_path}` ({len(df):,} windows, {len(group_meta):,} group IDs).",
        "Exact feature-trace hashes are used to expose repeated trajectories with different IDs.",
        "This report does not estimate detector performance.",
        "",
        "## Distinct traces by condition",
        "",
        "| Case | Operating regime | Attack regime | Group IDs | Distinct feature traces |",
        "|---|---|---|---:|---:|",
    ]
    counts = group_meta.groupby(["case_type", "op_regime", "attack_regime"], dropna=False).agg(
        group_ids=("trajectory_hash", "size"),
        unique_traces=("trajectory_hash", "nunique"),
    )
    for key, row in counts.iterrows():
        lines.append(
            f"| {key[0]} | {key[1]} | {key[2]} | {row.group_ids} | {row.unique_traces} |"
        )

    if split_path.exists():
        splits = json.loads(split_path.read_text(encoding="utf-8"))
        lines.extend(["", "## Split overlap audit", "", "| Split | Group ID overlap | Identical trace overlap |", "|---|---:|---:|"])
        for name, spec in splits.items():
            train = set(spec["train_groups"])
            test = set(spec["test_groups"])
            shared_groups = train & test
            train_hashes = {signatures[g] for g in train if g in signatures}
            test_hashes = {signatures[g] for g in test if g in signatures}
            lines.append(f"| {name} | {len(shared_groups)} | {len(train_hashes & test_hashes)} |")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
