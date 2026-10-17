from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

st.set_page_config(page_title="ColdGuardian AI", page_icon="🧊", layout="wide")

TEXT = {
    "English": {
        "title": "ColdGuardian AI",
        "subtitle": "A simple cold-chain safety helper",
        "demo": "DEMO DATA — NOT LIVE SHIPMENT DATA",
        "choose": "Choose a shipment",
        "safe": "Within the set temperature range",
        "hot": "Temperature is TOO HIGH",
        "cold": "Temperature is TOO LOW",
        "unknown": "Temperature information needs checking",
        "check": "Sensor information is missing or conflicting. Ask a trained person to check it.",
        "temp": "Current reported temperature",
        "range": "Allowed temperature range",
        "next": "What should happen next?",
        "high_action": "🚨 Check this shipment now. Confirm the sensor and follow your cold-chain procedure.",
        "ok_action": "✅ Keep monitoring the shipment and check the sensor data.",
        "facility": "Possible facilities to review",
        "facility_note": "These are suggestions only. A trained person must confirm before moving anything.",
        "history": "Temperature over time",
        "details": "Technical details (for staff)",
        "speak": "🔊 Read this screen aloud",
        "speech": "ColdGuardian alert. ",
        "no_facility": "No facility meets the demo compatibility and capacity rules.",
        "risk": "Review priority",
        "critical": "HIGH ATTENTION",
        "normal": "CHECK ROUTINELY",
        "verify": "VERIFY DATA",
    },
    "தமிழ்": {
        "title": "குளிர்சங்கிலி பாதுகாப்பு",
        "subtitle": "மருந்துகளின் வெப்பநிலையை கண்காணிக்க உதவும் எளிய கருவி",
        "demo": "செயற்கை மாதிரி தரவு — நேரடி தரவு அல்ல",
        "choose": "சரக்கைத் தேர்ந்தெடுக்கவும்",
        "safe": "வெப்பநிலை அனுமதிக்கப்பட்ட வரம்பில் உள்ளது",
        "hot": "வெப்பநிலை மிகவும் அதிகம்",
        "cold": "வெப்பநிலை மிகவும் குறைவு",
        "unknown": "வெப்பநிலைத் தகவலை சரிபார்க்க வேண்டும்",
        "check": "சென்சார் தகவல் இல்லை அல்லது முரண்படுகிறது. பயிற்சி பெற்ற நபரிடம் சரிபார்க்கவும்.",
        "temp": "தற்போதைய வெப்பநிலை",
        "range": "அனுமதிக்கப்பட்ட வெப்பநிலை",
        "next": "அடுத்து என்ன செய்ய வேண்டும்?",
        "high_action": "🚨 இந்த சரக்கை உடனே சரிபார்க்கவும். சென்சாரை உறுதிசெய்து நடைமுறையைப் பின்பற்றவும்.",
        "ok_action": "✅ தொடர்ந்து கண்காணித்து சென்சார் தகவலைச் சரிபார்க்கவும்.",
        "facility": "பரிசீலிக்கக்கூடிய மையங்கள்",
        "facility_note": "இவை பரிந்துரைகள் மட்டுமே. மாற்றுவதற்கு முன் பயிற்சி பெற்ற நபர் உறுதிப்படுத்த வேண்டும்.",
        "history": "காலத்தின்படி வெப்பநிலை",
        "details": "தொழில்நுட்ப விவரங்கள் (பணியாளர்களுக்கு)",
        "speak": "🔊 இந்தத் திரையைச் சத்தமாக வாசிக்கவும்",
        "speech": "குளிர்சங்கிலி எச்சரிக்கை. ",
        "no_facility": "இந்த மாதிரி விதிகளுக்கு ஏற்ற மையம் இல்லை.",
        "risk": "கவன முன்னுரிமை",
        "critical": "அதிக கவனம் தேவை",
        "normal": "வழக்கமான சரிபார்ப்பு",
        "verify": "தரவை சரிபார்க்கவும்",
    },
    "తెలుగు": {
        "title": "కోల్డ్ చైన్ భద్రత",
        "subtitle": "మందుల ఉష్ణోగ్రతను పర్యవేక్షించడానికి సులభమైన సహాయకం",
        "demo": "నమూనా డేటా మాత్రమే — ప్రత్యక్ష డేటా కాదు",
        "choose": "షిప్‌మెంట్‌ను ఎంచుకోండి",
        "safe": "ఉష్ణోగ్రత అనుమతించిన పరిధిలో ఉంది",
        "hot": "ఉష్ణోగ్రత చాలా ఎక్కువగా ఉంది",
        "cold": "ఉష్ణోగ్రత చాలా తక్కువగా ఉంది",
        "unknown": "ఉష్ణోగ్రత వివరాలను తనిఖీ చేయాలి",
        "check": "సెన్సార్ సమాచారం లేదు లేదా సరిపోలడం లేదు. శిక్షణ పొందిన వ్యక్తితో తనిఖీ చేయించండి.",
        "temp": "ప్రస్తుతం నమోదైన ఉష్ణోగ్రత",
        "range": "అనుమతించిన ఉష్ణోగ్రత పరిధి",
        "next": "తర్వాత ఏమి చేయాలి?",
        "high_action": "🚨 ఈ షిప్‌మెంట్‌ను వెంటనే తనిఖీ చేయండి. సెన్సార్‌ను నిర్ధారించి విధానాన్ని అనుసరించండి.",
        "ok_action": "✅ పర్యవేక్షణ కొనసాగించి సెన్సార్ డేటాను తనిఖీ చేయండి.",
        "facility": "పరిశీలించాల్సిన కేంద్రాలు",
        "facility_note": "ఇవి సూచనలు మాత్రమే. తరలించే ముందు శిక్షణ పొందిన వ్యక్తి నిర్ధారించాలి.",
        "history": "కాలక్రమంలో ఉష్ణోగ్రత",
        "details": "సాంకేతిక వివరాలు (సిబ్బందికి)",
        "speak": "🔊 ఈ స్క్రీన్‌ను చదివి వినిపించండి",
        "speech": "కోల్డ్ చైన్ హెచ్చరిక. ",
        "no_facility": "నమూనా నియమాలకు సరిపోయే కేంద్రం లేదు.",
        "risk": "శ్రద్ధ ప్రాధాన్యత",
        "critical": "అత్యధిక శ్రద్ధ అవసరం",
        "normal": "సాధారణ తనిఖీ",
        "verify": "డేటాను తనిఖీ చేయండి",
    },
}

lang = st.selectbox("Language / மொழி / భాష", list(TEXT.keys()), index=0)
t = TEXT[lang]

shipments = pd.read_csv(DATA / "shipments.csv")
facilities = pd.read_csv(DATA / "facilities.csv")
readings = pd.read_csv(DATA / "sensor_readings.csv")
quality = pd.read_csv(DATA / "sensor_quality_report.csv")
qmap = quality.set_index("shipment_id")["data_quality_status"].to_dict()

st.title("🧊 " + t["title"])
st.subheader(t["subtitle"])
st.error("⚠️ " + t["demo"])

options = shipments["shipment_id"].tolist()
selected = st.selectbox(t["choose"], options, format_func=lambda sid: f"📦 {sid}")
row = shipments.loc[shipments["shipment_id"] == selected].iloc[0]
temp = float(row["current_temp_c"])
low, high = float(row["min_temp_c"]), float(row["max_temp_c"])
quality_status = str(qmap.get(selected, "UNKNOWN"))
missing = "MISSING" in quality_status.upper()
too_high, too_low = temp > high, temp < low

if missing:
    headline = "🟠 " + t["unknown"]
    action = t["check"]
    color = "#8A4B00"
elif too_high:
    headline = "🔴 " + t["hot"]
    action = t["high_action"]
    color = "#B42318"
elif too_low:
    headline = "🔵 " + t["cold"]
    action = t["high_action"]
    color = "#175CD3"
else:
    headline = "🟢 " + t["safe"]
    action = t["ok_action"]
    color = "#067647"

st.markdown(
    f'<div style="border:4px solid {color}; border-radius:20px; padding:24px; margin:12px 0;">'
    f'<div style="font-size:clamp(24px,4vw,42px);font-weight:800;color:{color};">{headline}</div>'
    f'<div style="font-size:clamp(20px,3vw,30px);margin-top:14px;">🌡️ {temp:.1f} °C</div>'
    f'<div style="font-size:20px;margin-top:8px;">{t["range"]}: {low:.1f}–{high:.1f} °C</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(f"## {t['next']}")
st.markdown(f'<div style="font-size:clamp(20px,3vw,30px);font-weight:700;padding:12px 0;">{action}</div>', unsafe_allow_html=True)

speech = f'{t["speech"]}{headline}. {t["temp"]}: {temp:.1f} degrees Celsius. {t["range"]}: {low} to {high} degrees Celsius. {action}'
speech_lang = {"English": "en-IN", "தமிழ்": "ta-IN", "తెలుగు": "te-IN"}[lang]
if st.button(t["speak"], use_container_width=True):
    safe_text = speech.replace("\\", " ").replace("'", "\\'").replace("\n", " ")
    components.html(
        f"""<script>
        const utterance = new SpeechSynthesisUtterance('{safe_text}');
        utterance.lang = '{speech_lang}';
        utterance.rate = 0.85;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        </script>""",
        height=0,
    )

st.markdown(f"## 📍 {t['facility']}")
st.caption(t["facility_note"])
eligible = facilities[
    facilities["compatible_storage"].astype(str).str.lower().isin(["true", "1", "yes"])
    & (pd.to_numeric(facilities["spare_capacity_units"], errors="coerce") >= float(row["inventory_units"]))
].copy()
eligible["travel_time_min"] = pd.to_numeric(eligible["travel_time_min"], errors="coerce")
eligible = eligible.sort_values("travel_time_min")
if eligible.empty:
    st.warning(t["no_facility"])
else:
    for _, f in eligible.iterrows():
        st.markdown(
            f'<div style="border:2px solid #D0D5DD;border-radius:14px;padding:16px;margin:8px 0;">'
            f'<div style="font-size:22px;font-weight:700;">🏥 {f["name"]}</div>'
            f'<div style="font-size:18px;">🚗 {int(f["travel_time_min"])} min &nbsp; | &nbsp; '
            f'📦 {int(f["spare_capacity_units"])} places available</div></div>',
            unsafe_allow_html=True,
        )

hist = readings[readings["shipment_id"] == selected].copy()
hist["timestamp"] = pd.to_datetime(hist["timestamp"], errors="coerce")
hist["temperature_c"] = pd.to_numeric(hist["temperature_c"], errors="coerce")
hist = hist.dropna(subset=["timestamp", "temperature_c"]).sort_values("timestamp")
if not hist.empty:
    st.markdown(f"## 📈 {t['history']}")
    st.line_chart(hist.set_index("timestamp")[["temperature_c"]], y_label="°C")
    st.caption("Demo history is synthetic. A forecast is an experimental estimate, not a guarantee.")

with st.expander(t["details"]):
    st.write({
        "shipment_id": selected,
        "product": row["product"],
        "reported_temperature_c": temp,
        "min_temp_c": low,
        "max_temp_c": high,
        "inventory_units": int(row["inventory_units"]),
        "data_quality_status": quality_status,
        "priority_from_demo_data": row["priority"],
    })
    st.dataframe(eligible, use_container_width=True)

st.download_button(
    "⬇️ Download incident data (CSV)",
    data=shipments.to_csv(index=False).encode("utf-8"),
    file_name="coldguardian_demo_shipments.csv",
    mime="text/csv",
    use_container_width=True,
)
st.caption("Decision support only. Do not move or discard medicines based only on this demo. A trained cold-chain professional must verify all actions.")
