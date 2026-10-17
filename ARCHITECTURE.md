# ColdGuardian AI — Architecture

```text
Synthetic shipment / facility / sensor CSVs
                  |
                  v
          Input validation
                  |
                  v
     Sensor-quality reconciliation
                  |
                  v
    Rule-based incident classification
                  |
                  v
 Explainable severity heuristic (0–100)
                  |
                  v
 Rescue eligibility filters:
 compatibility + capacity + valid ETA
                  |
                  v
        Human-reviewed outputs
     /            |             \
Incident CSV   Rescue CSV   Forecast CSV
                  |
                  v
         Automated test suites
```

## Decision safeguards
- Configured temperature ranges are treated as inclusive at their boundaries.
- Missing or conflicting sensor records lead to verification and reconciliation.
- Facilities are filtered by compatible storage, sufficient spare capacity, and a valid non-negative supplied travel time.
- Rescue recommendations are candidates only; human approval and operational confirmation are required.
- Forecasts are experimental linear extrapolations and are not validated product-safety predictions.

## Current implementation status
This diagram describes the prototype in the repository. It does not imply live telemetry, automatic alerts, an ML-trained severity model, or production deployment.
