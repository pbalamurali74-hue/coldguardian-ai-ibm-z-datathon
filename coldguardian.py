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


def analyze_sensor_trust(shipments, readings, quality):
    """Return an explainable 0–100 sensor-trust heuristic per shipment.

    This is a transparent demo heuristic, not a calibrated probability or
    validated sensor-quality model. Missing readings and conflicting records
    reduce trust; duplicate timestamps, large jumps, and stuck values are
    counted when enough history is available.
    """
    s = shipments.copy()
    r = readings.copy()
    qmap = quality.set_index("shipment_id")["data_quality_status"].to_dict()
    s["current_temp_c"] = pd.to_numeric(s["current_temp_c"], errors="coerce")
    r["timestamp"] = pd.to_datetime(r["timestamp"], errors="coerce")
    r["temperature_c"] = pd.to_numeric(r["temperature_c"], errors="coerce")
    rows = []
    for _, row in s.iterrows():
        sid = row["shipment_id"]
        hist_all = r[r["shipment_id"] == sid].copy()
        valid = hist_all.dropna(subset=["timestamp", "temperature_c"]).sort_values("timestamp")
        penalties = []
        reasons = []
        if valid.empty:
            penalties.append(65)
            reasons.append("No valid timestamped temperature readings")
        else:
            missing_ratio = 1 - len(valid) / max(len(hist_all), 1)
            if missing_ratio > 0:
                p = min(35, int(round(missing_ratio * 35)))
                penalties.append(p)
                reasons.append(f"{missing_ratio:.0%} of rows have missing/invalid fields")
            duplicates = int(valid["timestamp"].duplicated(keep=False).sum())
            if duplicates:
                penalties.append(min(20, duplicates * 5))
                reasons.append(f"{duplicates} rows share duplicate timestamps")
            values = valid["temperature_c"].to_numpy(dtype=float)
            jumps = int((np.abs(np.diff(values)) >= 3.0).sum()) if len(values) > 1 else 0
            if jumps:
                penalties.append(min(25, jumps * 10))
                reasons.append(f"{jumps} abrupt change(s) of at least 3°C")
            stuck = len(values) >= 5 and np.allclose(values[-5:], values[-1])
            if stuck:
                penalties.append(15)
                reasons.append("Last five readings are identical")
        qstatus = str(qmap.get(sid, "UNKNOWN")).upper()
        if "MISSING" in qstatus or qstatus == "UNKNOWN":
            penalties.append(45)
            reasons.append(f"Quality report status: {qstatus}")
        current = row["current_temp_c"]
        if not valid.empty and pd.notna(current) and abs(float(valid.iloc[-1]["temperature_c"]) - float(current)) > 1.0:
            penalties.append(20)
            reasons.append("Reported current temperature differs from latest reading by >1°C")
        score = max(0, min(100, 100 - sum(penalties)))
        label = "HIGH TRUST" if score >= 80 else "MEDIUM TRUST" if score >= 50 else "LOW TRUST"
        rows.append({"shipment_id": sid, "sensor_trust_score": score,
                     "sensor_trust_label": label,
                     "sensor_trust_reasons": "; ".join(reasons) if reasons else "No configured demo checks triggered",
                     "valid_readings": int(len(valid)), "total_reading_rows": int(len(hist_all))})
    return pd.DataFrame(rows)


def compute_excursion_metrics(shipments, readings):
    """Summarize observed history against each shipment's configured temperature band."""
    s = shipments.copy()
    r = readings.copy()
    r["timestamp"] = pd.to_datetime(r["timestamp"], errors="coerce")
    r["temperature_c"] = pd.to_numeric(r["temperature_c"], errors="coerce")
    rows = []
    for _, shipment in s.iterrows():
        sid = shipment["shipment_id"]
        low = pd.to_numeric(pd.Series([shipment["min_temp_c"]]), errors="coerce").iloc[0]
        high = pd.to_numeric(pd.Series([shipment["max_temp_c"]]), errors="coerce").iloc[0]
        hist = r[r["shipment_id"] == sid].dropna(subset=["timestamp", "temperature_c"]).sort_values("timestamp")
        if hist.empty or pd.isna(low) or pd.isna(high) or low >= high:
            rows.append({"shipment_id": sid, "valid_readings": len(hist), "peak_temp_c": np.nan,
                         "minimum_temp_c": np.nan, "max_deviation_c": np.nan,
                         "observed_out_of_range_minutes": np.nan, "recovery_status": "INSUFFICIENT DATA"})
            continue
        temps = hist["temperature_c"].to_numpy(dtype=float)
        outside = (temps < low) | (temps > high)
        # Estimate exposure duration only across adjacent observed samples; do not extrapolate gaps.
        duration = 0.0
        times = hist["timestamp"].tolist()
        for i in range(1, len(hist)):
            gap_min = (times[i] - times[i-1]).total_seconds() / 60
            if 0 <= gap_min <= 15 and (outside[i] or outside[i-1]):
                duration += gap_min
        latest = float(temps[-1])
        recovery = "OUT OF RANGE — REVIEW" if latest < low or latest > high else ("IN RANGE AT LAST READING" if outside.any() else "NO OBSERVED EXCURSION")
        deviations = np.maximum(low - temps, np.maximum(temps - high, 0))
        rows.append({"shipment_id": sid, "valid_readings": len(hist),
                     "peak_temp_c": round(float(np.max(temps)), 2),
                     "minimum_temp_c": round(float(np.min(temps)), 2),
                     "max_deviation_c": round(float(np.max(deviations)), 2),
                     "observed_out_of_range_minutes": round(float(duration), 1),
                     "recovery_status": recovery})
    return pd.DataFrame(rows)


def build_priority_queue(shipments, readings, quality):
    """Join incident, trust, and observed-excursion signals into a transparent queue."""
    incidents = build_incident_report(shipments, readings, quality)
    trust = analyze_sensor_trust(shipments, readings, quality)
    excursion = compute_excursion_metrics(shipments, readings)
    queue = incidents.merge(trust, on="shipment_id", how="left").merge(excursion, on="shipment_id", how="left")
    queue["priority_score"] = (
        queue["severity_score"].fillna(0) * 0.55
        + (100 - queue["sensor_trust_score"].fillna(0)) * 0.25
        + queue["max_deviation_c"].fillna(0).clip(upper=8) / 8 * 20
    ).round(1).clip(0, 100)
    queue["priority_reason"] = queue.apply(
        lambda r: f"{r['severity_label']}; sensor trust {r['sensor_trust_score']}/100; "
                  f"maximum observed deviation {r['max_deviation_c'] if pd.notna(r['max_deviation_c']) else 'unknown'}°C",
        axis=1
    )
    return queue.sort_values(["priority_score", "severity_score"], ascending=False).reset_index(drop=True)
