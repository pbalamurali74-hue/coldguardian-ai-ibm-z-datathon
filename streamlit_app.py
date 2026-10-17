from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from coldguardian import (
    load_inputs, build_priority_queue, experimental_linear_forecast,
    build_rescue_plan,
)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="ColdGuardian AI", page_icon="🧊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: linear-gradient(180deg,#fffdf9 0%,#fff7ed 100%); color:#242424; }
.block-container { max-width: 1440px; padding-top: 1.2rem; }
.hero { padding: 1.6rem 1.8rem; border-radius: 22px; background: linear-gradient(115deg,#fff 0%,#ffedd5 65%,#fee2e2 100%); border:1px solid #fed7aa; box-shadow:0 8px 28px #7c2d1210; }
.eyebrow { color:#c2410c; font-size:.78rem; letter-spacing:.14em; font-weight:900; }
.hero h1 { margin:.25rem 0; font-size:clamp(2rem,4vw,3.4rem); font-weight:900; color:#7f1d1d; }
.hero p { margin:.2rem 0; color:#57534e; font-size:1.04rem; }
.kpi { background:white; border:1px solid #fed7aa; border-radius:16px; padding:1rem 1.1rem; box-shadow:0 4px 16px #7c2d120a; }
.kpi-label { color:#78716c; font-size:.78rem; font-weight:800; text-transform:uppercase; letter-spacing:.07em; }
.kpi-value { color:#9a3412; font-size:2rem; font-weight:900; }
.section-title { margin-top:1rem; color:#9a3412; font-size:1.35rem; font-weight:900; }
.note { background:#fff7ed; border-left:4px solid #f97316; border-radius:8px; padding:.8rem 1rem; color:#57534e; }
div[data-testid="stDownloadButton"] button { border-radius:10px; border-color:#f97316; }
</style>
<div class="hero">
 <div class="eyebrow">DATASET DISTRACTORS • IBM Z DATATHON 2026</div>
 <h1>🧊 ColdGuardian AI</h1>
 <p>Explainable cold-chain monitoring · Sensor trust · Excursion analytics · Human-reviewed response</p>
</div>
""", unsafe_allow_html=True)

st.caption("DEMO MODE • SYNTHETIC CSV DATA • NOT A LIVE MEDICAL OR LOGISTICS SYSTEM")

try:
    shipments, facilities, readings, quality = load_inputs(ROOT / "data")
except Exception as exc:
    st.error(f"Could not load the demo dataset: {exc}")
    st.stop()

st.markdown("### Import sensor readings")
st.caption("Optional: upload CSV with timestamp, shipment_id, temperature_c. Only rows for shipment IDs in the shipment table are accepted. Uploads are session-only.")
upload = st.file_uploader("Sensor readings CSV", type=["csv"], key="sensor_upload")
if upload is not None:
    try:
        incoming = pd.read_csv(upload)
        required = {"timestamp", "shipment_id", "temperature_c"}
        if not required.issubset(set(incoming.columns)):
            st.error("Missing required columns: timestamp, shipment_id, temperature_c.")
        elif not set(incoming["shipment_id"].dropna().astype(str)).issubset(set(shipments["shipment_id"].astype(str))):
            st.error("Unknown shipment IDs found. Using bundled demo readings instead.")
        else:
            readings = incoming.copy()
            st.success(f"Loaded {len(readings)} reading rows for this session only.")
    except Exception as exc:
        st.error(f"Could not parse upload: {exc}")

queue = build_priority_queue(shipments, readings, quality)
forecasts = experimental_linear_forecast(readings, shipments)
rescue = build_rescue_plan(shipments, facilities, quality)

total = len(shipments)
outside = int(((pd.to_numeric(shipments.current_temp_c, errors="coerce") < pd.to_numeric(shipments.min_temp_c, errors="coerce")) |
               (pd.to_numeric(shipments.current_temp_c, errors="coerce") > pd.to_numeric(shipments.max_temp_c, errors="coerce"))).sum())
missing = int(quality.data_quality_status.astype(str).str.contains("MISSING|UNKNOWN", case=False, regex=True).sum())
low_trust = int((queue.sensor_trust_score < 50).sum())

cols = st.columns(4)
metrics = [
    ("SHIPMENTS MONITORED", total, "📦"),
    ("REPORTED EXCURSIONS", outside, "🌡️"),
    ("DATA QUALITY FLAGS", missing, "📡"),
    ("LOW-TRUST SENSORS", low_trust, "🛡️"),
]
for col, (label, value, emoji) in zip(cols, metrics):
    with col:
        st.markdown(f'<div class="kpi"><div class="kpi-label">{emoji} {label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">🚨 Priority action queue</div>', unsafe_allow_html=True)
st.write("Transparent heuristic ranking combines the existing incident score, sensor-trust penalty, and maximum observed temperature deviation.")
display_cols = ["shipment_id","product","reported_temp_c","incident_status","severity_score",
                "sensor_trust_score","sensor_trust_label","peak_temp_c","max_deviation_c",
                "observed_out_of_range_minutes","recovery_status","priority_score","priority_reason"]
filter_left, filter_right = st.columns([1, 1])
with filter_left:
    selected_status = st.selectbox("Filter incident status", ["All"] + sorted(queue["incident_status"].astype(str).unique().tolist()))
with filter_right:
    minimum_priority = st.slider("Minimum priority score", 0, 100, 0, 5)
filtered_queue = queue.copy()
if selected_status != "All":
    filtered_queue = filtered_queue[filtered_queue["incident_status"].astype(str) == selected_status]
filtered_queue = filtered_queue[pd.to_numeric(filtered_queue["priority_score"], errors="coerce") >= minimum_priority]
st.dataframe(filtered_queue[display_cols], use_container_width=True, hide_index=True)
st.download_button("⬇️ Export filtered priority queue (CSV)", filtered_queue.to_csv(index=False).encode("utf-8"),
                   "coldguardian_priority_queue.csv", "text/csv")

left, right = st.columns([1, 1])
with left:
    st.markdown('<div class="section-title">🔎 Shipment investigation</div>', unsafe_allow_html=True)
    options = shipments.shipment_id.tolist()
    selected = st.selectbox("Select a shipment", options, format_func=lambda sid:
                            f"{sid} — {shipments.loc[shipments.shipment_id == sid, 'product'].iloc[0]}")
    srow = shipments.loc[shipments.shipment_id == selected].iloc[0]
    qrow = queue.loc[queue.shipment_id == selected].iloc[0]
    st.metric("Reported temperature", f"{float(srow.current_temp_c):.1f} °C",
              delta=f"Allowed {srow.min_temp_c:g}–{srow.max_temp_c:g} °C")
    st.write(f"**Incident:** {qrow.incident_status}")
    st.write(f"**Sensor trust:** {int(qrow.sensor_trust_score)}/100 — {qrow.sensor_trust_label}")
    st.write(f"**Priority score:** {qrow.priority_score}/100 (illustrative heuristic)")
    st.write(f"**Why flagged:** {qrow.priority_reason}")
    st.write(f"**Sensor checks:** {qrow.sensor_trust_reasons}")
    st.markdown('<div class="note">Before any real-world action, confirm the timestamp and sensor, physically verify the shipment using approved procedures, and escalate to the responsible cold-chain professional.</div>', unsafe_allow_html=True)

    selected_report = qrow.to_frame().T
    st.download_button("📄 Export selected incident report", selected_report.to_csv(index=False).encode("utf-8"),
                       f"{selected.lower()}_incident_report.csv", "text/csv", use_container_width=True)

with right:
    st.markdown('<div class="section-title">📈 Observed temperature history</div>', unsafe_allow_html=True)
    hist = readings.loc[readings.shipment_id == selected].copy()
    hist["timestamp"] = pd.to_datetime(hist["timestamp"], errors="coerce")
    hist["temperature_c"] = pd.to_numeric(hist["temperature_c"], errors="coerce")
    hist = hist.dropna(subset=["timestamp","temperature_c"]).sort_values("timestamp")
    low, high = float(srow.min_temp_c), float(srow.max_temp_c)
    if hist.empty:
        st.warning("No valid timestamped readings. Do not infer a temperature trend from the reported value alone.")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axhspan(low, high, alpha=0.16, label="Configured safe band")
        ax.plot(hist.timestamp, hist.temperature_c, marker="o", linewidth=2.4, label="Observed demo readings")
        ax.axhline(high, linestyle="--", linewidth=1.2, label="Upper limit")
        ax.axhline(low, linestyle="--", linewidth=1.2, label="Lower limit")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xlabel("Timestamp")
        ax.grid(alpha=.2)
        ax.legend(loc="best", fontsize=8)
        fig.autofmt_xdate()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    st.write(f"**Peak observed:** {qrow.peak_temp_c if pd.notna(qrow.peak_temp_c) else 'Unknown'} °C")
    st.write(f"**Max observed deviation:** {qrow.max_deviation_c if pd.notna(qrow.max_deviation_c) else 'Unknown'} °C")
    st.write(f"**Observed out-of-range span estimate:** {qrow.observed_out_of_range_minutes if pd.notna(qrow.observed_out_of_range_minutes) else 'Unknown'} min")
    st.caption("Duration is estimated only between adjacent valid readings no more than 15 minutes apart. It is not a continuous exposure measurement.")

st.markdown('<div class="section-title">⏱️ Experimental trend baseline</div>', unsafe_allow_html=True)
if forecasts.empty:
    st.info("Not enough valid readings for the linear extrapolation baseline. At least four valid readings are required.")
else:
    selected_forecast = forecasts[forecasts.shipment_id == selected]
    if selected_forecast.empty:
        st.info("This shipment does not have enough valid history for a forecast.")
    else:
        st.dataframe(selected_forecast, use_container_width=True, hide_index=True)
        st.caption("Experimental linear extrapolation only. No held-out validation, calibrated confidence, or product-safety prediction is available.")

st.markdown('<div class="section-title">🏥 Facility candidates</div>', unsafe_allow_html=True)
st.caption("Candidates are filtered using listed storage compatibility and spare capacity. Travel times are supplied demo values, not live routing.")
selected_rescue = rescue[rescue.shipment_id == selected]
st.dataframe(selected_rescue, use_container_width=True, hide_index=True)
st.dataframe(facilities, use_container_width=True, hide_index=True)

with st.expander("Technical details and decision safeguards"):
    st.write("The priority score is a demonstration heuristic, not a trained model or calibrated risk probability.")
    st.write("Sensor trust uses transparent penalties for missing/invalid readings, duplicate timestamps, abrupt jumps, repeated identical values, quality-report flags, and conflicts with the latest reported reading.")
    st.write("The demo has no live sensors, GPS, map API, logistics API, or autonomous alerts. Synthetic data must not be used to make clinical or product-disposition decisions.")
    st.write("A high or low score does not establish whether medicine or vaccines are safe. Follow product-specific SOPs and qualified human review.")
    st.write({"shipments": total, "facilities": len(facilities), "sensor_reading_rows": len(readings),
              "quality_report_rows": len(quality), "forecast_rows": len(forecasts)})


st.markdown('<div class="section-title">🧾 Review and handoff tracker</div>', unsafe_allow_html=True)
st.caption("Track review status for this browser session and export a handoff CSV. This is not persistent storage and does not send alerts.")
if "review_states" not in st.session_state:
    st.session_state.review_states = {}
review_rows = []
for _, qr in queue.iterrows():
    sid = qr.shipment_id
    prior = st.session_state.review_states.get(sid, {})
    a, b, c = st.columns([1, 1, 2])
    with a:
        reviewed = st.checkbox(f"{sid}: reviewed", value=bool(prior.get("reviewed", False)), key=f"rev_{sid}")
    with b:
        escalated = st.checkbox("Escalated", value=bool(prior.get("escalated", False)), key=f"esc_{sid}")
    with c:
        note = st.text_input("Handoff note", value=str(prior.get("note", "")), key=f"note_{sid}")
    st.session_state.review_states[sid] = {"reviewed": reviewed, "escalated": escalated, "note": note}
    review_rows.append({"shipment_id":sid, "incident_status":qr.incident_status, "priority_score":qr.priority_score,
                        "reviewed":reviewed, "escalated":escalated, "note":note,
                        "data_notice":"Synthetic demo data; human review required"})
review_df = pd.DataFrame(review_rows)
st.download_button("⬇️ Export review / handoff checklist", review_df.to_csv(index=False).encode("utf-8"),
                   "coldguardian_review_handoff.csv", "text/csv", use_container_width=True)

st.markdown('<div class="section-title">🧪 Temperature what-if simulator</div>', unsafe_allow_html=True)
sim_id = st.selectbox("Select shipment for scenario", shipments.shipment_id.tolist(), key="scenario_shipment")
simrow = shipments.loc[shipments.shipment_id == sim_id].iloc[0]
scenario_temp = st.slider("Hypothetical temperature (°C)", -5.0, 25.0, float(simrow.current_temp_c), 0.1)
scenario_status = classify_temperature(scenario_temp, float(simrow.min_temp_c), float(simrow.max_temp_c))
st.metric("Scenario status", scenario_status, delta=f"{scenario_temp:.1f} °C")
st.caption("Scenario-only calculation: it does not edit source data, predict product safety, or authorize a transfer.")

st.markdown('<div class="section-title">🧰 Data-quality workbench</div>', unsafe_allow_html=True)
with st.expander("Inspect sensor-quality report"):
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export sensor quality report", quality.to_csv(index=False).encode("utf-8"),
                       "coldguardian_sensor_quality.csv", "text/csv")
with st.expander("Inspect raw sensor readings"):
    st.dataframe(readings, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export raw sensor readings", readings.to_csv(index=False).encode("utf-8"),
                       "coldguardian_sensor_readings.csv", "text/csv")

st.markdown('<div class="note">Safety notice: synthetic demonstration data only. This prototype supports investigation and documentation; it does not authorize product use, disposal, or transfer.</div>', unsafe_allow_html=True)
