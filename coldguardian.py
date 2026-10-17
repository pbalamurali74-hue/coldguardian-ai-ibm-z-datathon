"""ColdGuardian AI decision support prototype.

Uses synthetic demo data. Severity weights are illustrative heuristics, not a
trained model. Outputs require human review and are not product-disposition advice.
"""
from pathlib import Path
import numpy as np
import pandas as pd


def load_inputs(data_dir="data"):
    root = Path(data_dir)
    required = ["shipments.csv", "facilities.csv", "sensor_readings.csv",
                "sensor_quality_report.csv"]
    missing = [name for name in required if not (root / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing input files under {root}: {missing}")
    shipments = pd.read_csv(root / "shipments.csv")
    facilities = pd.read_csv(root / "facilities.csv")
    readings = pd.read_csv(root / "sensor_readings.csv")
    quality = pd.read_csv(root / "sensor_quality_report.csv")
    return shipments, facilities, readings, quality


def classify_temperature(temp, low, high):
    """Return range status, with bounds treated as within range."""
    if pd.isna(temp) or pd.isna(low) or pd.isna(high):
        return "UNKNOWN"
    if low >= high:
        return "INVALID CONFIGURATION"
    if temp < low:
        return "BELOW LOWER LIMIT"
    if temp > high:
        return "ABOVE UPPER LIMIT"
    return "WITHIN CONFIGURED RANGE"


def build_incident_report(shipments, readings, quality):
    """Build explainable statuses and illustrative 0–100 risk scores."""
    s = shipments.copy()
    r = readings.copy()
    qmap = quality.set_index("shipment_id")["data_quality_status"].to_dict()

    for col in ["min_temp_c", "max_temp_c", "current_temp_c", "inventory_units"]:
        s[col] = pd.to_numeric(s[col], errors="coerce")
    r["timestamp"] = pd.to_datetime(r["timestamp"], errors="coerce")
    r["temperature_c"] = pd.to_numeric(r["temperature_c"], errors="coerce")

    rows = []
    for _, row in s.iterrows():
        sid = row["shipment_id"]
        temp, low, high, units = (row["current_temp_c"], row["min_temp_c"],
                                  row["max_temp_c"], row["inventory_units"])
        qstatus = qmap.get(sid, "UNKNOWN")
        tstatus = classify_temperature(temp, low, high)
        missing_sensor = qstatus == "MISSING READING"
        valid_temp = tstatus not in ["UNKNOWN", "INVALID CONFIGURATION"]
        deviation = max(low - temp, temp - high, 0) if valid_temp else np.nan

        hist = r[r["shipment_id"] == sid].dropna(
            subset=["timestamp", "temperature_c"]
        ).sort_values("timestamp")
        above_count = int((hist["temperature_c"] > high).sum()) if not hist.empty and pd.notna(high) else 0

        temp_points = min(40, round(deviation / max(high - low, 1) * 40)) if pd.notna(deviation) else 0
        sensor_points = 25 if missing_sensor or not valid_temp else 0
        inventory_points = 20 if pd.notna(units) and units >= 200 else 12 if pd.notna(units) and units >= 100 else 5 if pd.notna(units) else 0
        persistence_points = min(15, above_count * 3)
        score = min(100, temp_points + sensor_points + inventory_points + persistence_points)

        if missing_sensor:
            status = "VERIFY SENSOR / RECONCILE DATA"
            label = "VERIFY — HIGH DATA RISK"
            action = "Verify sensor and physical shipment; reconcile conflicting records; escalate."
        elif not valid_temp:
            status = tstatus
            label = "VERIFY — HIGH DATA RISK"
            action = "Obtain valid temperature/configuration data and escalate for review."
        elif deviation > 0:
            status = "REPORTED TEMPERATURE EXCURSION"
            label = "CRITICAL — REVIEW" if deviation >= 4 else "HIGH — EXCURSION REVIEW"
            action = "Follow the validated temperature-excursion SOP; qualified human review required."
        else:
            status = "WITHIN CONFIGURED RANGE — MONITOR"
            label = "MEDIUM — REVIEW" if score >= 40 else "LOW — MONITOR"
            action = "Continue monitoring and verify sensor freshness."

        rows.append({
            "shipment_id": sid, "product": row["product"],
            "reported_temp_c": temp, "min_temp_c": low, "max_temp_c": high,
            "inventory_units": units, "sensor_quality": qstatus,
            "incident_status": status, "severity_score": score,
            "severity_label": label, "temperature_points": temp_points,
            "sensor_quality_points": sensor_points,
            "inventory_impact_points": inventory_points,
            "persistence_points": persistence_points,
            "recommended_action": action,
            "explanation": f"Temperature: {tstatus}; sensor quality: {qstatus}; "
                           f"readings above upper limit: {above_count}"
        })
    return pd.DataFrame(rows).sort_values("severity_score", ascending=False).reset_index(drop=True)


def build_rescue_plan(shipments, facilities, quality):
    """Filter compatible, sufficiently large facilities for reported excursions."""
    s = shipments.copy()
    f = facilities.copy()
    qmap = quality.set_index("shipment_id")["data_quality_status"].to_dict()

    for col in ["min_temp_c", "max_temp_c", "current_temp_c", "inventory_units"]:
        s[col] = pd.to_numeric(s[col], errors="coerce")
    f["spare_capacity_units"] = pd.to_numeric(f["spare_capacity_units"], errors="coerce")
    f["travel_time_min"] = pd.to_numeric(f["travel_time_min"], errors="coerce")
    compatible = f["compatible_storage"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])

    results = []
    for _, row in s.iterrows():
        sid = row["shipment_id"]
        qstatus = qmap.get(sid, "UNKNOWN")
        temp, low, high, units = row["current_temp_c"], row["min_temp_c"], row["max_temp_c"], row["inventory_units"]

        if qstatus == "MISSING READING":
            results.append({"shipment_id": sid, "recommended_facility": "Not assigned",
                            "travel_time_min": np.nan, "decision": "VERIFY SENSOR / ESCALATE",
                            "reason": "Missing sensor data; reconcile the record before transfer planning."})
            continue
        state = classify_temperature(temp, low, high)
        if state == "UNKNOWN" or state == "INVALID CONFIGURATION":
            results.append({"shipment_id": sid, "recommended_facility": "Not assigned",
                            "travel_time_min": np.nan, "decision": "HUMAN REVIEW",
                            "reason": "Insufficient or invalid temperature data."})
            continue
        if state == "WITHIN CONFIGURED RANGE":
            results.append({"shipment_id": sid, "recommended_facility": "No transfer proposed",
                            "travel_time_min": np.nan, "decision": "MONITOR",
                            "reason": "Reported value is within configured limits."})
            continue

        candidates = f.loc[
            compatible & f["spare_capacity_units"].ge(units) &
            f["travel_time_min"].notna() & f["travel_time_min"].ge(0)
        ].sort_values("travel_time_min")

        if candidates.empty:
            results.append({"shipment_id": sid, "recommended_facility": "No eligible facility",
                            "travel_time_min": np.nan, "decision": "HUMAN ESCALATION",
                            "reason": "No compatible facility has enough capacity and a valid travel time."})
        else:
            chosen = candidates.iloc[0]
            results.append({"shipment_id": sid, "recommended_facility": chosen["name"],
                            "travel_time_min": chosen["travel_time_min"],
                            "decision": "CANDIDATE — HUMAN APPROVAL REQUIRED",
                            "reason": "Compatible storage and sufficient capacity; shortest listed travel time."})
    return pd.DataFrame(results)


def experimental_linear_forecast(readings, shipments, horizons=(5, 10, 15)):
    """Linear extrapolation baseline; requires >=4 valid readings.

    It is experimental and has not been validated on representative held-out data.
    """
    r = readings.copy()
    r["timestamp"] = pd.to_datetime(r["timestamp"], errors="coerce")
    r["temperature_c"] = pd.to_numeric(r["temperature_c"], errors="coerce")
    limits = shipments.set_index("shipment_id")["max_temp_c"].to_dict()
    rows = []
    for sid, group in r.groupby("shipment_id"):
        group = group.dropna(subset=["timestamp", "temperature_c"]).sort_values("timestamp")
        if len(group) < 4 or group["timestamp"].nunique() < 2:
            continue
        minutes = (group["timestamp"] - group["timestamp"].iloc[0]).dt.total_seconds().to_numpy() / 60
        values = group["temperature_c"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(minutes, values, 1)
        for horizon in horizons:
            prediction = float(intercept + slope * (minutes[-1] + horizon))
            upper = limits.get(sid, np.nan)
            rows.append({
                "shipment_id": sid, "minutes_ahead": int(horizon),
                "forecast_temperature_c": round(prediction, 2),
                "upper_limit_c": upper,
                "baseline_above_limit": bool(prediction > upper) if pd.notna(upper) else None,
                "trend_c_per_min": round(float(slope), 4),
                "model": "Experimental linear baseline"
            })
    return pd.DataFrame(rows)


def run_demo(data_dir="data", output_dir="."):
    shipments, facilities, readings, quality = load_inputs(data_dir)
    incidents = build_incident_report(shipments, readings, quality)
    rescue = build_rescue_plan(shipments, facilities, quality)
    forecast = experimental_linear_forecast(readings, shipments)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    incidents.to_csv(out / "coldguardian_incidents.csv", index=False)
    rescue.to_csv(out / "coldguardian_rescue_plan.csv", index=False)
    forecast.to_csv(out / "coldguardian_experimental_forecast.csv", index=False)
    return incidents, rescue, forecast
