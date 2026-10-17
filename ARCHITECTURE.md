# ColdGuardian AI — Architecture

```text
Synthetic shipment / facility / sensor CSVs
                  |
                  v
           Input validation
                  |
                  v
    Sensor trust + quality reconciliation
                  |
                  v
 Observed excursion analytics (peak, deviation,
 duration estimate, last-reading recovery)
                  |
                  v
 Rule-based incident + severity heuristic
                  |
                  v
 Explainable priority queue
                  |
          +-------+--------+
          |                |
          v                v
 Facility eligibility   Experimental linear
 and supplied ETA       trend baseline
          |                |
          +-------+--------+
                  |
                  v
      Quiz-free operations dashboard
    KPIs • drill-down • CSV incident export
                  |
                  v
         Human-reviewed outputs
```

## Dashboard features
- Shipment-level queue sorted by an illustrative priority score.
- Sensor trust score (0–100) with visible reasons.
- Peak/minimum observed temperature, maximum deviation, estimated out-of-range span, and last-reading status.
- Temperature history chart showing configured temperature limits.
- Experimental linear forecast only where enough readings exist.
- Facility candidates filtered by compatible storage and sufficient capacity.

## Decision safeguards
- Configured temperature ranges are treated as inclusive at their boundaries.
- Missing or conflicting sensor records lead to verification and reconciliation.
- Facilities are filtered by compatible storage, sufficient spare capacity, and a valid non-negative supplied travel time.
- Duration is estimated only across adjacent valid samples no more than 15 minutes apart; missing gaps are not extrapolated.
- Forecasts are experimental linear extrapolations and are not validated product-safety predictions.
- Priority and trust scores are transparent heuristics, not trained ML or calibrated probabilities.
- Rescue recommendations are candidates only; human approval and operational confirmation are required.

## Current implementation status
This diagram describes the repository prototype. It does not imply live telemetry, automatic alerts, an ML-trained severity model, or production deployment. Demo records are synthetic.
