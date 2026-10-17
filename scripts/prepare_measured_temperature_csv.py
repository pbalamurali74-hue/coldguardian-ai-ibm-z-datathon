#!/usr/bin/env python3
"""Normalize a measured temperature CSV without modifying its source file.

Use explicit column names from the original dataset. This script does not infer
product safety limits or label observations as safe/unsafe.
"""
import argparse
from pathlib import Path
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Original CSV path")
    parser.add_argument("--output", required=True, help="Output normalized CSV path")
    parser.add_argument("--temperature-col", required=True, help="Source column containing Celsius temperatures")
    parser.add_argument("--timestamp-col", help="Source column containing full timestamp")
    parser.add_argument("--date-col", help="Source date column (use with --time-col)")
    parser.add_argument("--time-col", help="Source time column (use with --date-col)")
    parser.add_argument("--series-id", default=None, help="Label for this sensor/location series")
    args = parser.parse_args()

    if bool(args.timestamp_col) == bool(args.date_col or args.time_col):
        parser.error("Choose either --timestamp-col OR both --date-col and --time-col.")
    if bool(args.date_col) != bool(args.time_col):
        parser.error("--date-col and --time-col must be supplied together.")

    source = Path(args.input)
    frame = pd.read_csv(source)
    required = [args.temperature_col]
    if args.timestamp_col:
        required.append(args.timestamp_col)
    else:
        required.extend([args.date_col, args.time_col])
    missing = [col for col in required if col not in frame.columns]
    if missing:
        parser.error(f"Columns not found: {missing}. Available columns: {list(frame.columns)}")

    if args.timestamp_col:
        timestamp = frame[args.timestamp_col]
    else:
        timestamp = frame[args.date_col].astype(str).str.strip() + " " + frame[args.time_col].astype(str).str.strip()

    out = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamp, errors="coerce", utc=True),
        "temperature_c": pd.to_numeric(frame[args.temperature_col], errors="coerce"),
    })
    out["series_id"] = args.series_id or source.stem
    out["source_file"] = source.name
    invalid = int(out[["timestamp", "temperature_c"]].isna().any(axis=1).sum())
    out = out.dropna(subset=["timestamp", "temperature_c"]).sort_values("timestamp")
    if out.empty:
        raise SystemExit("No valid timestamp/temperature rows remain. Check your column names and formats.")
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(destination, index=False)
    print(f"Wrote {len(out)} valid rows to {destination}; dropped {invalid} invalid rows.")
    print("Keep the original source file and cite the dataset. No safety classification was performed.")


if __name__ == "__main__":
    main()
