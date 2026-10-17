# IBM Z Datathon 2026 — 3-Minute Video Script

**Project:** Dataset Distractors_IBM Z Datathon 2026 Project  
**Product:** ColdGuardian AI  
**Team:** Dataset Distractors

Target length: 2:45–2:55 to stay below the compulsory 3-minute maximum.

## 0:00–0:25 — Introduction and problem
**Narration:** “We are Dataset Distractors from SRM Institute of Science and Technology, Ramapuram. Our project, ColdGuardian AI, supports cold-chain incident review by highlighting reported temperature excursions, missing sensor data, and feasible response facilities.”

**Show:** Title slide and problem statement.

## 0:25–0:50 — Supporting data and incident
**Narration:** “Our demonstration uses synthetic data: three shipments, three facilities, and twelve sensor readings. SH001 reports 10.2°C against a configured 2–8°C range. SH002 and SH003 show why missing or conflicting sensor-quality data must trigger verification rather than an assumption of safety.”

**Show:** Shipment table and SH001 temperature history. Clearly state the records are synthetic.

## 0:50–1:25 — Solution and workflow
**Narration:** “ColdGuardian AI reads shipment, facility, and sensor files; checks data quality; applies transparent rule-based severity scoring; filters rescue facilities by compatible storage and capacity; and exports incident and audit reports. It also provides a what-if simulator and an experimental linear temperature trend.”

**Show:** Incident board, explainable factors, rescue candidate, and simulator.

## 1:25–1:55 — IBM Z / LinuxONE and stack
**Narration:** “We ran the Python notebook workflow on an IBM LinuxONE community-cloud instance and used JupyterLab to inspect results and export reports. Our stack includes Python, pandas, NumPy, Matplotlib, JupyterLab, ipywidgets, and CSV. This demonstrates execution on LinuxONE; we have not measured hardware-specific performance gains.”

**Show:** Actual LinuxONE instance/JupyterLab browser and a code cell running. Never show SSH keys, tokens, passwords, or private configuration.

## 1:55–2:20 — Model and testing
**Narration:** “The severity score is an explainable rule-based heuristic, not a trained machine-learning model. The short-horizon forecast is linear extrapolation and has not been validated on held-out real data. Our two implemented test suites reported 26 and 13 passing checks, with no reported failures.”

**Show:** Forecast table and reliability test results. Do not describe these tests as clinical or production validation.

## 2:20–2:50 — Value and close
**Narration:** “The value is data-quality-aware, explainable decision support that keeps humans in control. Our next steps are real sensor integration, evaluation on representative datasets, forecast accuracy testing, and validation with cold-chain experts. Thank you.”

**Show:** Closing slide with team name.

## Final recording checklist
- Video stays under 3 minutes.
- Shows problem, data supporting the problem, solution, tech stack, actual LinuxONE instance, and implemented decision workflow.
- Screen shows the working project rather than only slides.
- No credentials or access tokens are visible.
- All claims match the implemented prototype.
