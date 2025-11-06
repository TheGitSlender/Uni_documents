#!/usr/bin/env python3
"""
morty_rate_of_change.py

Focus: visualize per-planet success rate and its rate-of-change (derivative) from Morty run logs.

Behavior:
- Finds the most recent morty_log_*.csv in ./logs, ./data, /mnt/data, or current dir (or set CSV_PATH below).
- Loads the CSV which is expected to include at least these columns:
    trip_index, planet, survived
  If your CSV already contains a "success_rate" column (rolling value) we ignore it and recompute fresh.
- For each planet, we compute a per-trip rolling success_rate (window = WINDOW) and then the derivative:
    deriv[t] = rolling[t] - rolling[t-1]
  We then smooth the derivative with another moving average (DERIV_SMOOTH_WINDOW) to reduce noise.
- Produces two PNGs next to the CSV:
    - <csvname>_success_rates.png
    - <csvname>_rate_of_change.png
- Prints summary stats per planet (mean abs derivative, max abs derivative).

Edit constants below (WINDOW, DERIV_SMOOTH_WINDOW) to tune smoothing.

Usage:
    python morty_rate_of_change.py
"""

import os
from pathlib import Path
import sys
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------- CONFIG ----------
CSV_PATH = "logs/morty_log_2025-11-05T08-33-12-088387.csv"

WINDOW = 15                 # rolling window to compute success rate (trips)
DERIV_SMOOTH_WINDOW = 5     # smoothing window for derivative
MIN_TRIPS_TO_PLOT = 5      # require at least this many points per planet
OUT_DIRS_TO_SEARCH = ["./logs", "./data", "/mnt/data", "."]  # search order
# ---------------------------


def find_latest_csv():
    if CSV_PATH:
        p = Path(CSV_PATH)
        if p.exists():
            return p.resolve()
        else:
            print(f"CSV_PATH is set but file not found: {CSV_PATH}", file=sys.stderr)
            return None

    candidates = []
    for d in OUT_DIRS_TO_SEARCH:
        pdir = Path(d)
        if not pdir.exists():
            continue
        candidates += list(pdir.glob("morty_log_*.csv"))
        candidates += list(pdir.glob("morty_run_*.csv"))
        candidates += list(pdir.glob("trip_data_*.csv"))
        candidates += list(pdir.glob("*.csv"))

    if not candidates:
        return None
    # choose the most recent modification time
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].resolve()


def load_and_clean_csv(path: Path):
    df = pd.read_csv(path)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Required fields: trip_index, planet, survived
    # If trip_index missing, create sequential index
    if "trip_index" not in df.columns:
        df.insert(0, "trip_index", range(1, len(df) + 1))
    # planet column: ensure int
    if "planet" not in df.columns:
        raise SystemExit("CSV missing 'planet' column. Aborting.")
    df["planet"] = df["planet"].astype(int)
    # survived: if absent try to derive from 'survival_rate' or 'survived' text
    if "survived" not in df.columns:
        if "survival_rate_percentage" in df.columns:
            df["survived"] = df["survival_rate_percentage"].apply(lambda x: 1 if float(x) > 0 else 0)
        else:
            raise SystemExit("CSV missing 'survived' column. Aborting.")
    df["survived"] = df["survived"].astype(int)
    # sort by trip_index
    df = df.sort_values("trip_index").reset_index(drop=True)
    return df


def compute_planet_time_series(df, planet, window=WINDOW):
    # filter rows for this planet
    pdf = df[df["planet"] == planet].copy()
    if pdf.empty:
        return None
    # compute rolling success rate with respect to the planet's own trips in chronological order
    # we need a time axis that is the global trip_index; but since the planet is visited intermittently,
    # we compute the planet's rolling success rate against its own event sequence.
    pdf = pdf.sort_values("trip_index").reset_index(drop=True)
    pdf["event_idx"] = np.arange(len(pdf))  # sequence of visits to this planet
    pdf["rolling_success"] = pdf["survived"].rolling(window=window, min_periods=1).mean()
    # derivative: difference between consecutive rolling_success values (per visit)
    pdf["deriv"] = pdf["rolling_success"].diff().fillna(0)
    # smooth derivative (simple moving average)
    pdf["deriv_smooth"] = pdf["deriv"].rolling(window=DERIV_SMOOTH_WINDOW, min_periods=1, center=True).mean()
    # also keep the global trip_index for plotting on x-axis
    return pdf[["trip_index", "event_idx", "survived", "rolling_success", "deriv", "deriv_smooth"]]


def summary_stats_from_deriv(df_series):
    # df_series is deriv_smooth
    arr = np.array(df_series.dropna(), dtype=float)
    if len(arr) == 0:
        return {"mean_abs": None, "max_abs": None, "std_abs": None}
    absarr = np.abs(arr)
    return {"mean_abs": float(absarr.mean()), "max_abs": float(absarr.max()), "std_abs": float(absarr.std())}


def plot_success_and_derivative(per_planet_data, csv_path: Path):
    out_prefix = csv_path.stem

    # Plot success rates (one figure with one subplot per planet)
    fig, axes = plt.subplots(nrows=len(per_planet_data), ncols=1, figsize=(10, 4 * len(per_planet_data)), sharex=False)
    if len(per_planet_data) == 1:
        axes = [axes]
    for ax, (p, pdf) in zip(axes, per_planet_data.items()):
        if pdf is None or len(pdf) < MIN_TRIPS_TO_PLOT:
            ax.text(0.5, 0.5, f"No data for planet {p}", ha="center", va="center")
            ax.set_title(f"Planet {p} (no data)")
            continue
        ax.plot(pdf["event_idx"], pdf["rolling_success"], marker="o", linestyle="-", label=f"planet {p}")
        ax.set_ylim(-0.05, 1.05)
        ax.set_ylabel("rolling success rate")
        ax.set_xlabel("visit # to this planet (in-order)")
        ax.set_title(f"Planet {p} rolling success rate (window={WINDOW})")
        ax.legend()
    fig.tight_layout()
    out1 = csv_path.with_name(out_prefix + "_success_rates.png")
    fig.savefig(out1)
    plt.close(fig)

    # Plot derivative (smoothed) — one subplot per planet
    fig2, axes2 = plt.subplots(nrows=len(per_planet_data), ncols=1, figsize=(10, 4 * len(per_planet_data)), sharex=False)
    if len(per_planet_data) == 1:
        axes2 = [axes2]
    for ax, (p, pdf) in zip(axes2, per_planet_data.items()):
        if pdf is None or len(pdf) < MIN_TRIPS_TO_PLOT:
            ax.text(0.5, 0.5, f"No data for planet {p}", ha="center", va="center")
            ax.set_title(f"Planet {p} derivative (no data)")
            continue
        ax.plot(pdf["event_idx"], pdf["deriv_smooth"], marker=".", linestyle="-", label=f"planet {p} deriv_smooth")
        ax.axhline(0, color="black", linewidth=0.6, linestyle="--")
        ax.set_ylabel("d(success_rate)/d(visit)")
        ax.set_xlabel("visit # to this planet (in-order)")
        ax.set_title(f"Planet {p} smoothed derivative (window={DERIV_SMOOTH_WINDOW})")
        ax.legend()
    fig2.tight_layout()
    out2 = csv_path.with_name(out_prefix + "_rate_of_change.png")
    fig2.savefig(out2)
    plt.close(fig2)

    return out1, out2


def main():
    csv_file = find_latest_csv()
    if not csv_file:
        print("No morty log CSV found in search paths. Place your morty_log_*.csv in ./logs, ./data, /mnt/data or current dir.")
        sys.exit(1)
    print("Using CSV:", csv_file)

    df = load_and_clean_csv(csv_file)
    # Build per-planet dataframes
    per_planet = {}
    stats_summary = {}
    for p in sorted(df["planet"].unique()):
        pdf = compute_planet_time_series(df, p, window=WINDOW)
        per_planet[p] = pdf
        if pdf is not None:
            stats_summary[p] = summary_stats_from_deriv(pdf["deriv_smooth"])
        else:
            stats_summary[p] = {"mean_abs": None, "max_abs": None, "std_abs": None}

    # Print summary stats (rate-of-change magnitude)
    print("\nPer-planet rate-of-change summary (smoothed derivative):")
    for p, s in stats_summary.items():
        print(f" Planet {p}: mean_abs_deriv={s['mean_abs']}, max_abs_deriv={s['max_abs']}, std_abs_deriv={s['std_abs']}")

    # Plot and save
    out1, out2 = plot_success_and_derivative(per_planet, csv_file)
    print(f"\nSaved success rate plot to: {out1}")
    print(f"Saved rate-of-change plot to: {out2}")
    print("\nInterpretation tips:")
    print(" - mean_abs_deriv: average absolute change per visit (lower => more steady).")
    print(" - max_abs_deriv: largest one-visit swing (large values indicate abrupt jumps).")
    print(" - Compare mean_abs_deriv across planets to see which planet's probability changes faster.")
    print(" - If a planet has low mean_abs_deriv and sustained high rolling_success, it's a safer pick.")
    print(" - Consider using larger WINDOW to reduce noise; smaller WINDOW makes the derivative more sensitive.")

if __name__ == '__main__':
    main()
