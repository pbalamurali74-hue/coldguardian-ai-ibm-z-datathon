import unittest
import pandas as pd
import numpy as np

from coldguardian import (
    classify_temperature,
    build_incident_report,
    build_rescue_plan,
    experimental_linear_forecast,
    analyze_sensor_trust,
    compute_excursion_metrics,
    build_priority_queue,
)


class ColdGuardianTests(unittest.TestCase):
    def setUp(self):
        self.shipments = pd.DataFrame([
            {"shipment_id":"S1","product":"Vaccine-A","min_temp_c":2.0,"max_temp_c":8.0,"current_temp_c":10.2,"inventory_units":240,"priority":"High"},
            {"shipment_id":"S2","product":"Medicine-B","min_temp_c":2.0,"max_temp_c":8.0,"current_temp_c":6.5,"inventory_units":120,"priority":"Medium"},
        ])
        self.facilities = pd.DataFrame([
            {"facility_id":"F1","name":"Compatible","compatible_storage":True,"spare_capacity_units":300,"travel_time_min":20},
            {"facility_id":"F2","name":"Too small","compatible_storage":True,"spare_capacity_units":100,"travel_time_min":5},
            {"facility_id":"F3","name":"Incompatible","compatible_storage":False,"spare_capacity_units":500,"travel_time_min":2},
        ])
        self.readings = pd.DataFrame([
            {"timestamp":"2026-10-17 08:00:00","shipment_id":"S1","temperature_c":5.0},
            {"timestamp":"2026-10-17 08:05:00","shipment_id":"S1","temperature_c":5.5},
            {"timestamp":"2026-10-17 08:10:00","shipment_id":"S1","temperature_c":6.0},
            {"timestamp":"2026-10-17 08:15:00","shipment_id":"S1","temperature_c":6.5},
        ])
        self.quality = pd.DataFrame([
            {"shipment_id":"S1","data_quality_status":"TEMPERATURE ABOVE MAX"},
            {"shipment_id":"S2","data_quality_status":"MISSING READING"},
        ])

    def test_bounds_are_inclusive(self):
        self.assertEqual(classify_temperature(2.0, 2.0, 8.0), "WITHIN CONFIGURED RANGE")
        self.assertEqual(classify_temperature(8.0, 2.0, 8.0), "WITHIN CONFIGURED RANGE")

    def test_out_of_range_values_flagged(self):
        self.assertEqual(classify_temperature(1.9, 2.0, 8.0), "BELOW LOWER LIMIT")
        self.assertEqual(classify_temperature(8.1, 2.0, 8.0), "ABOVE UPPER LIMIT")

    def test_missing_temperature_unknown(self):
        self.assertEqual(classify_temperature(np.nan, 2.0, 8.0), "UNKNOWN")

    def test_invalid_range_rejected(self):
        self.assertEqual(classify_temperature(5.0, 8.0, 2.0), "INVALID CONFIGURATION")

    def test_missing_sensor_not_assigned_facility(self):
        plan = build_rescue_plan(self.shipments, self.facilities, self.quality)
        row = plan.loc[plan.shipment_id == "S2"].iloc[0]
        self.assertEqual(row["recommended_facility"], "Not assigned")
        self.assertIn("VERIFY", row["decision"])

    def test_rescue_chooses_eligible_facility(self):
        plan = build_rescue_plan(self.shipments, self.facilities, self.quality)
        row = plan.loc[plan.shipment_id == "S1"].iloc[0]
        self.assertEqual(row["recommended_facility"], "Compatible")
        self.assertIn("HUMAN APPROVAL", row["decision"])

    def test_scores_bounded(self):
        report = build_incident_report(self.shipments, self.readings, self.quality)
        self.assertTrue(report["severity_score"].between(0, 100).all())

    def test_constant_forecast_is_flat(self):
        readings = pd.DataFrame({
            "shipment_id":["S1"]*5,
            "timestamp":pd.date_range("2026-01-01", periods=5, freq="5min"),
            "temperature_c":[5.0]*5
        })
        fc = experimental_linear_forecast(readings, self.shipments[["shipment_id", "max_temp_c"]])
        self.assertFalse(fc.empty)
        self.assertTrue(np.allclose(fc["forecast_temperature_c"], 5.0))

    def test_sensor_trust_is_bounded_and_missing_data_reduces_trust(self):
        trust = analyze_sensor_trust(self.shipments, self.readings, self.quality)
        self.assertTrue(trust["sensor_trust_score"].between(0, 100).all())
        s2 = trust.loc[trust.shipment_id == "S2"].iloc[0]
        self.assertEqual(s2["sensor_trust_score"], 0)
        self.assertIn("No valid", s2["sensor_trust_reasons"])

    def test_excursion_metrics_flag_peak_and_status(self):
        metrics = compute_excursion_metrics(self.shipments, self.readings)
        s1 = metrics.loc[metrics.shipment_id == "S1"].iloc[0]
        self.assertAlmostEqual(s1["peak_temp_c"], 6.5)
        self.assertEqual(s1["recovery_status"], "NO OBSERVED EXCURSION")

    def test_priority_queue_contains_explainable_score(self):
        queue = build_priority_queue(self.shipments, self.readings, self.quality)
        self.assertIn("priority_score", queue.columns)
        self.assertTrue(queue["priority_score"].between(0, 100).all())
        self.assertTrue(queue["priority_reason"].astype(str).str.len().gt(0).all())

    def test_short_history_is_skipped(self):
        short = pd.DataFrame({
            "shipment_id":["S1"]*3,
            "timestamp":pd.date_range("2026-01-01", periods=3, freq="5min"),
            "temperature_c":[5.0,5.2,5.4]
        })
        fc = experimental_linear_forecast(short, self.shipments[["shipment_id", "max_temp_c"]])
        self.assertTrue(fc.empty)


if __name__ == "__main__":
    unittest.main()
