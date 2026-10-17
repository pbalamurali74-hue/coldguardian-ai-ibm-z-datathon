"""Run ColdGuardian AI on the bundled synthetic sample data."""
from pathlib import Path
import pandas as pd
from coldguardian import run_demo

ROOT = Path(__file__).resolve().parent
incidents, rescue, forecast = run_demo(ROOT / "data", ROOT / "outputs")

print("\n=== COLDGUARDIAN AI — SYNTHETIC DEMO ===")
print("\nIncident report:")
print(incidents[["shipment_id", "incident_status", "severity_score", "severity_label"]].to_string(index=False))
print("\nRescue plan:")
print(rescue.to_string(index=False))
print("\nExperimental forecast:")
if forecast.empty:
    print("Insufficient readings to generate baseline forecast.")
else:
    print(forecast.to_string(index=False))
print("\nReports saved to:", ROOT / "outputs")
print("Synthetic data only. Human review is required; scores and forecasts are not validated.")
