# Dataset Distractors_IBM Z Datathon 2026 Project

# ColdGuardian AI — Explainable Cold-Chain Monitoring

**Team:** Dataset Distractors  
**Institution:** SRM Institute of Science and Technology, Ramapuram  
**Team lead:** Purushotham Balamurali  
**Team members:** R Nikhil Kumar Reddy, S Sai Laasya, A Jagan Mohan Reddy  
**Event:** IBM Z Datathon 2026 — 24-hour datathon, 17–18 October 2026

## Problem

Cold-chain operations must spot temperature excursions, detect missing or conflicting sensor data, and identify response facilities that have compatible storage and enough capacity. A single temperature value is not sufficient when a data-quality report says the sensor reading is missing.

## Solution

ColdGuardian AI is a notebook-based decision-support prototype that:
- Reads shipment, facility, sensor-reading, and sensor-quality CSV files.
- Flags reported temperatures outside configured product limits.
- Routes missing or conflicting sensor records to verification.
- Provides a transparent, rule-based severity heuristic.
- Filters rescue candidates by storage compatibility and sufficient capacity, then ranks eligible facilities by supplied travel time.
- Visualizes temperature histories and provides an experimental linear trend forecast where enough readings exist.
- Exports incident, rescue, forecast, and testing reports.

## IBM Z / LinuxONE implementation

The team ran the Python/JupyterLab workflow on an IBM LinuxONE community-cloud environment, accessing the remote environment through SSH and JupyterLab.

**Stack:** Python 3.12, pandas, NumPy, Matplotlib, JupyterLab, ipywidgets, and CSV.

This demonstrates the workflow running on LinuxONE. No architecture-specific performance improvement or hardware benchmark has been measured.

## Current demo data

The demonstration data is synthetic and contains 3 shipments, 3 facilities, and 12 sensor readings.

- **SH001:** reported temperature 10.2°C against a configured range of 2–8°C; excursion review is required.
- **SH002:** the quality report indicates a missing reading; verify and reconcile sensor/shipment data.
- **SH003:** reported current temperature is 8.7°C while its quality report indicates a missing reading; reconcile this conflict before acting.

The 540 units in flagged shipments do not mean the products are damaged or unusable.

## Testing evidence

The team reports:
- Initial edge-case suite: 26 passed, 0 failed.
- Report-consistency and forecast-reliability suite: 13 passed, 0 failed.
- Total: 39 passing test cases across two suites; some coverage overlaps.

These tests cover only the implemented checks and do not establish clinical, regulatory, or production readiness.

## Important limitations

- The dataset is synthetic, not live telemetry.
- Severity scoring is a rule-based heuristic, not a trained machine-learning model.
- Forecasting uses experimental linear extrapolation and has not been evaluated on representative held-out data.
- No live sensor, GPS, mapping, or logistics integration is connected.
- Recommendations are for human-reviewed decision support only; they are not autonomous transfer or product-disposition instructions.
- Real use would require representative data, forecast evaluation, qualified domain review, security controls, monitoring, and formal validation.

## Accessible Streamlit prototype

`streamlit_app.py` provides an animated, game-inspired mission interface: users choose a shipment, make a decision, receive illustrative feedback/XP, compare safety-time-uncertainty trade-offs, view candidate facilities, and hear alerts in English/Tamil/Telugu. CSS animations, large visual status cards, and celebratory feedback are included. It uses synthetic demo CSVs and is decision support only. It uses synthetic demo CSVs and is decision support only.

Launch in an environment where Streamlit dependencies install successfully:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

The IBM LinuxONE `s390x` environment previously could not build a compatible PyArrow dependency for Streamlit. For a public browser demo, deploy this repository through Streamlit Community Cloud and select `streamlit_app.py` as the app file. The account owner must sign in and authorize deployment. The Jupyter notebook remains the LinuxONE demo path.

## Project files

- [`ColdGuardian_Dashboard.ipynb`](ColdGuardian_Dashboard.ipynb) — the team's Jupyter dashboard and analysis notebook (uploaded to this repository).
- `streamlit_app.py` — visual-first, multilingual Streamlit prototype.
- `coldguardian.py` — reusable incident, severity, facility-eligibility, and experimental forecast logic.
- `demo.py` — small command-line demonstration using bundled synthetic CSVs.
- `data/` — synthetic demo input CSVs.
- `tests/test_coldguardian.py` — standard-library unit tests.
- `requirements.txt` — Python dependencies.
- `VIDEO_SCRIPT.md` — suggested sub-three-minute demo script and judge talking points.

## Run locally or in JupyterLab

Python 3.10+ is recommended.

```bash
python -m pip install -r requirements.txt
python demo.py
python -m unittest discover -s tests -v
```

The core logic uses pandas and NumPy. If using the team's existing JupyterLab environment, the notebook workflow may also use Matplotlib and ipywidgets for plots and interactive controls.

## Open-source resources

- Python: https://www.python.org/
- pandas: https://pandas.pydata.org/
- NumPy: https://numpy.org/
- Matplotlib: https://matplotlib.org/
- JupyterLab: https://jupyter.org/
- ipywidgets: https://ipywidgets.readthedocs.io/

List other APIs, datasets, models, or libraries only if they are actually used in the submitted implementation.

## Official submission

- Submission portal: https://hack2skill.com/event/datathon-2026
- Submission walkthrough: https://youtu.be/3_L3T__zEco?si=Q-ckiVTP6ByvgZEv

**Final-submission checklist:**
- [x] Upload the Jupyter dashboard notebook used by the team.
- [x] Include a three-minute video script in `VIDEO_SCRIPT.md`.
- [ ] Run the final notebook top-to-bottom in the target LinuxONE/JupyterLab environment immediately before recording.
- [ ] Record and upload a video of no more than 3 minutes showing the problem, supporting data, solution, tech stack, actual LinuxONE instance, and implemented workflow/model.
- [ ] Confirm the submission title includes the team name and paste this repository URL into the official portal.

Never include SSH private keys, access tokens, passwords, or server credentials in this repository.
