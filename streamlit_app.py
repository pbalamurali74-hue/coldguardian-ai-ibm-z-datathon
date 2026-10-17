from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
st.set_page_config(page_title="ColdGuardian | Mission Control", page_icon="🧊", layout="wide")

COPY = {
 "English": {
  "title":"COLDGUARDIAN", "subtitle":"Save the cold chain. Make the smart move.",
  "demo":"TRAINING SIMULATION • SYNTHETIC DATA • NOT A LIVE MEDICAL SYSTEM",
  "mission":"YOUR MISSION", "choose":"Choose a shipment to investigate",
  "temp":"Reported temperature", "range":"Allowed range", "quality":"Sensor signal",
  "high":"TOO WARM", "low":"TOO COLD", "ok":"IN RANGE", "unknown":"DATA MISSING",
  "round":"DECISION ROUND", "question":"What is your next move?",
  "verify":"🔎 VERIFY FIRST", "move":"🚑 PREPARE SAFE TRANSFER", "ignore":"⏳ KEEP WAITING",
  "verify_desc":"Check sensor + confirm the real shipment condition",
  "move_desc":"Request a trained person to assess a suitable facility",
  "ignore_desc":"Take no action yet",
  "score":"MISSION SCORE", "best":"SMART MOVE!", "bad":"RISKY MOVE",
  "good":"You reduced uncertainty before acting. That is a strong decision under incomplete information.",
  "badmsg":"This choice can increase risk. In real operations, follow the approved cold-chain procedure and escalate to trained staff.",
  "fac":"FACILITY OPTIONS", "facnote":"Only candidates matching storage compatibility and capacity are shown. Confirm with staff before moving products.",
  "history":"TEMPERATURE STORY", "staff":"Staff view: technical details", "speak":"🔊 Read the alert aloud",
  "read":"Alert. Shipment", "none":"No facility meets this simulation's rules.",
  "next":"Play another round", "win":"ROUND CLEARED", "lost":"LESSON UNLOCKED",
  "foot":"Game-theory learning demo: actions have different trade-offs in safety, time, and uncertainty. Scores are illustrative—not clinical or operational recommendations.",
  "what":"WHY THIS MOVE?", "payoff":"SIMULATED TRADE-OFFS", "safety":"Safety", "time":"Time", "uncertainty":"Uncertainty",
  "rule":"Rule: when information is missing or conflicting, verify before making a real-world transfer decision."
 },
 "தமிழ்": {
  "title":"குளிர்காப்பு", "subtitle":"மருந்துகளை பாதுகாப்போம். சரியான முடிவைத் தேர்வுசெய்வோம்.",
  "demo":"பயிற்சி மாதிரி • செயற்கை தரவு • நேரடி மருத்துவ அமைப்பு அல்ல",
  "mission":"உங்கள் பணி", "choose":"சரக்கைத் தேர்ந்தெடுக்கவும்",
  "temp":"பதிவான வெப்பநிலை", "range":"அனுமதிக்கப்பட்ட வரம்பு", "quality":"சென்சார் தகவல்",
  "high":"மிகவும் சூடு", "low":"மிகவும் குளிர்", "ok":"வரம்புக்குள்", "unknown":"தரவு இல்லை",
  "round":"முடிவு சுற்று", "question":"அடுத்ததாக என்ன செய்வீர்கள்?",
  "verify":"🔎 முதலில் சரிபார்க்கவும்", "move":"🚑 பாதுகாப்பான மாற்றத்தைத் தயாரிக்கவும்", "ignore":"⏳ காத்திருக்கவும்",
  "verify_desc":"சென்சாரையும் சரக்கின் உண்மை நிலையும் சரிபார்க்கவும்",
  "move_desc":"பொருத்தமான மையத்தைப் பற்றி பயிற்சி பெற்ற நபரிடம் ஆலோசிக்கவும்",
  "ignore_desc":"இப்போது நடவடிக்கை எடுக்க வேண்டாம்",
  "score":"பணி மதிப்பெண்", "best":"சிறந்த முடிவு!", "bad":"ஆபத்தான முடிவு",
  "good":"நடவடிக்கை எடுக்கும் முன் தகவலைச் சரிபார்த்தீர்கள். இது நல்ல முடிவு.",
  "badmsg":"இந்தத் தேர்வு ஆபத்தை அதிகரிக்கலாம். உண்மையான செயல்பாட்டில் அங்கீகரிக்கப்பட்ட நடைமுறையைப் பின்பற்றவும்.",
  "fac":"மையத் தேர்வுகள்", "facnote":"சேமிப்பு மற்றும் கொள்ளளவு பொருந்தும் மையங்கள் மட்டுமே காட்டப்படும். மாற்றுவதற்கு முன் பணியாளரிடம் உறுதிப்படுத்தவும்.",
  "history":"வெப்பநிலை வரலாறு", "staff":"பணியாளர்களுக்கான தொழில்நுட்ப விவரங்கள்", "speak":"🔊 எச்சரிக்கையை வாசிக்கவும்",
  "read":"எச்சரிக்கை. சரக்கு", "none":"இந்த மாதிரி விதிகளுக்கு ஏற்ற மையம் இல்லை.",
  "next":"மற்றொரு சுற்று விளையாடுங்கள்", "win":"சுற்று வெற்றி", "lost":"பாடம் கற்றீர்கள்",
  "foot":"இது விளையாட்டு அடிப்படையிலான பயிற்சி. மதிப்பெண்கள் விளக்கத்திற்காக மட்டுமே; மருத்துவ முடிவுகளுக்கான பரிந்துரை அல்ல.",
  "what":"இந்த முடிவு ஏன்?", "payoff":"மாதிரி சமநிலைகள்", "safety":"பாதுகாப்பு", "time":"நேரம்", "uncertainty":"தெளிவின்மை",
  "rule":"தரவு இல்லை அல்லது முரண்பட்டால், உண்மையான மாற்ற முடிவுக்கு முன் சரிபார்க்கவும்."
 },
 "తెలుగు": {
  "title":"కోల్డ్ గార్డియన్", "subtitle":"కోల్డ్ చైన్‌ను కాపాడండి. తెలివైన నిర్ణయం తీసుకోండి.",
  "demo":"శిక్షణ సిమ్యులేషన్ • నమూనా డేటా • ప్రత్యక్ష వైద్య వ్యవస్థ కాదు",
  "mission":"మీ లక్ష్యం", "choose":"షిప్‌మెంట్ ఎంచుకోండి",
  "temp":"నమోదైన ఉష్ణోగ్రత", "range":"అనుమతించిన పరిధి", "quality":"సెన్సార్ సమాచారం",
  "high":"చాలా వేడి", "low":"చాలా చల్లగా", "ok":"పరిధిలో ఉంది", "unknown":"డేటా లేదు",
  "round":"నిర్ణయ రౌండ్", "question":"తర్వాత మీరు ఏం చేస్తారు?",
  "verify":"🔎 ముందుగా తనిఖీ", "move":"🚑 సురక్షిత బదిలీ సిద్ధం", "ignore":"⏳ వేచి ఉండండి",
  "verify_desc":"సెన్సార్‌ను, సరుకు నిజ స్థితిని తనిఖీ చేయండి",
  "move_desc":"తగిన కేంద్రం గురించి శిక్షణ పొందిన వ్యక్తిని అడగండి",
  "ignore_desc":"ఇప్పుడే చర్య తీసుకోకండి",
  "score":"మిషన్ స్కోర్", "best":"మంచి నిర్ణయం!", "bad":"ప్రమాదకర నిర్ణయం",
  "good":"చర్యకు ముందు సమాచారాన్ని తనిఖీ చేశారు. ఇది మంచి నిర్ణయం.",
  "badmsg":"ఈ ఎంపిక ప్రమాదాన్ని పెంచవచ్చు. నిజ జీవితంలో ఆమోదించిన విధానాన్ని అనుసరించండి.",
  "fac":"కేంద్ర ఎంపికలు", "facnote":"నిల్వ మరియు సామర్థ్యం సరిపోయే కేంద్రాలే చూపబడతాయి. బదిలీకి ముందు సిబ్బందితో నిర్ధారించండి.",
  "history":"ఉష్ణోగ్రత చరిత్ర", "staff":"సిబ్బంది సాంకేతిక వివరాలు", "speak":"🔊 హెచ్చరికను చదివి వినిపించండి",
  "read":"హెచ్చరిక. షిప్‌మెంట్", "none":"నమూనా నియమాలకు సరిపోయే కేంద్రం లేదు.",
  "next":"మరో రౌండ్ ఆడండి", "win":"రౌండ్ పూర్తి", "lost":"పాఠం నేర్చుకున్నారు",
  "foot":"ఇది ఆట ఆధారిత శిక్షణ నమూనా. స్కోర్లు వివరణ కోసం మాత్రమే; వైద్య సూచనలు కావు.",
  "what":"ఈ నిర్ణయం ఎందుకు?", "payoff":"నమూనా ప్రభావాలు", "safety":"భద్రత", "time":"సమయం", "uncertainty":"అనిశ్చితి",
  "rule":"డేటా లేనప్పుడు లేదా విరుద్ధంగా ఉన్నప్పుడు, నిజమైన బదిలీ నిర్ణయానికి ముందు తనిఖీ చేయాలి."
 }
}
lang=st.selectbox("Language / மொழி / భాష", ["English","தமிழ்","తెలుగు"], key="language")
t=COPY[lang]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
:root{--ink:#292524;--muted:#6d6873;--orange:#f97316;--red:#dc2626}
html,body,[class*="css"]{font-family:'Nunito',sans-serif}
.stApp{background:linear-gradient(180deg,#fff7ed 0%,#fff 38%,#fffaf6 100%);color:var(--ink)}
.block-container{max-width:1320px;padding-top:1.2rem;padding-bottom:3rem}
h1,h2,h3,p,label,div{color:inherit}
section[data-testid="stSidebar"]{background:#fff1e6;border-right:1px solid #fed7aa}
[data-testid="stHeader"]{background:rgba(255,255,255,.82)}
.hero{position:relative;overflow:hidden;padding:clamp(24px,4vw,44px);border:1px solid #fdba74;border-radius:28px;background:linear-gradient(115deg,#fff 0%,#fff1e6 52%,#fee2e2 100%);box-shadow:0 18px 48px #9a34121a;animation:enter .7s ease-out}
.hero:after{content:'❄';position:absolute;right:3%;top:-32px;font-size:clamp(100px,18vw,230px);font-weight:900;color:#f9731612;transform:rotate(12deg);pointer-events:none}
.eyebrow{letter-spacing:2.5px;color:#c2410c;font-weight:900;font-size:12px}
.hero-title{font-size:clamp(34px,5.4vw,64px);font-weight:900;line-height:1.02;margin:12px 0;color:#991b1b}
.hero-sub{font-size:clamp(17px,2.2vw,23px);color:#57534e;max-width:760px}
.demo-pill{display:inline-block;background:#fff;color:#991b1b;border:1px solid #fca5a5;border-radius:999px;padding:9px 15px;font-weight:900;font-size:11px;margin-top:18px;box-shadow:0 5px 14px #dc262610}
.panel{border:1px solid #f1d5c2;border-radius:22px;padding:20px;background:linear-gradient(145deg,#fff,#fffaf6);box-shadow:0 10px 28px #7c2d1210;animation:enter .55s ease-out both;transition:transform .2s,box-shadow .2s}
.panel:hover{transform:translateY(-2px);box-shadow:0 15px 34px #9a34121a}
.metric{font-size:clamp(28px,4vw,44px);font-weight:900;line-height:1.15;color:#292524}
.small-label{font-size:11px;color:#9a3412;text-transform:uppercase;letter-spacing:1.6px;font-weight:900}
.big-alert{font-size:clamp(22px,2.7vw,34px);font-weight:900;animation:pulse 1.7s infinite}
.section{font-size:clamp(21px,2.5vw,27px);font-weight:900;margin:25px 0 10px;color:#991b1b}
.stCaption,.stMarkdown p{color:#57534e}
div.stButton>button{width:100%;border-radius:16px;min-height:76px;font-size:16px;font-weight:900;border:1px solid #fdba74;background:linear-gradient(120deg,#fff7ed,#ffedd5);color:#9a3412;white-space:pre-wrap;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
div.stButton>button:hover{transform:translateY(-3px);box-shadow:0 12px 24px #ea580c24;border-color:#f97316;background:linear-gradient(120deg,#ffedd5,#fee2e2);color:#7f1d1d}
div.stButton>button:focus{border-color:#dc2626;color:#7f1d1d}
div[data-testid="stDownloadButton"] button{background:linear-gradient(100deg,#ea580c,#dc2626);color:#fff;border:0;min-height:54px}
div[data-testid="stDownloadButton"] button:hover{background:linear-gradient(100deg,#c2410c,#b91c1c);color:#fff}
div[data-testid="stDataFrame"],div[data-testid="stTable"]{border:1px solid #fed7aa;border-radius:14px;overflow:hidden}
div[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,#f97316,#dc2626)}
.stAlert{border-radius:16px}
hr{border-color:#fed7aa}
@keyframes enter{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{text-shadow:0 0 0 #dc262600}50%{text-shadow:0 0 18px #dc262644}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
 <div class="eyebrow">DATASET DISTRACTORS · IBM Z DATATHON 2026</div>
 <div class="hero-title">🧊 {t['title']}</div>
 <div class="hero-sub">{t['subtitle']}</div>
 <div class="demo-pill">⚠️ {t['demo']}</div>
</div>
""",unsafe_allow_html=True)

shipments=pd.read_csv(DATA/"shipments.csv")
facilities=pd.read_csv(DATA/"facilities.csv")
readings=pd.read_csv(DATA/"sensor_readings.csv")
quality=pd.read_csv(DATA/"sensor_quality_report.csv")
qmap=quality.set_index("shipment_id")["data_quality_status"].to_dict()

st.markdown(f'<div class="section">🎮 {t["mission"]}</div>',unsafe_allow_html=True)
st.caption("PLAY A ROUND: learn how safety, time and missing information affect a decision.")
shipment_id=st.selectbox(t["choose"],shipments["shipment_id"].tolist(),format_func=lambda sid: f"📦 {sid} — {shipments.loc[shipments.shipment_id==sid,'product'].iloc[0]}")
row=shipments[shipments.shipment_id==shipment_id].iloc[0]
temp=float(row.current_temp_c); low=float(row.min_temp_c); high=float(row.max_temp_c)
qstatus=str(qmap.get(shipment_id,"UNKNOWN"))
missing="MISSING" in qstatus.upper()
too_high=temp>high; too_low=temp<low
status=t["unknown"] if missing else t["high"] if too_high else t["low"] if too_low else t["ok"]
status_icon="🟠" if missing else "🔴" if too_high else "🔵" if too_low else "🟢"
status_color="#fbbf24" if missing else "#fb7185" if too_high else "#60a5fa" if too_low else "#4ade80"

c1,c2,c3=st.columns(3)
with c1:
 st.markdown(f'<div class="panel"><div class="small-label">📦 SHIPMENT</div><div class="metric">{shipment_id}</div><div>{row["product"]}</div></div>',unsafe_allow_html=True)
with c2:
 st.markdown(f'<div class="panel"><div class="small-label">🌡️ {t["temp"]}</div><div class="metric">{temp:.1f}°C</div><div>{t["range"]}: {low:g}–{high:g}°C</div></div>',unsafe_allow_html=True)
with c3:
 st.markdown(f'<div class="panel"><div class="small-label">🚦 {t["quality"]}</div><div class="big-alert" style="color:{status_color}">{status_icon} {status}</div><div>{qstatus}</div></div>',unsafe_allow_html=True)

st.markdown(f'<div class="section">🧠 {t["round"]}: {t["question"]}</div>',unsafe_allow_html=True)
st.markdown("**Imagine you are the cold-chain response team. Which move would you choose?**")
a,b,c=st.columns(3)
with a:
 choose_verify=st.button(f'{t["verify"]}\n{t["verify_desc"]}',use_container_width=True)
with b:
 choose_transfer=st.button(f'{t["move"]}\n{t["move_desc"]}',use_container_width=True)
with c:
 choose_wait=st.button(f'{t["ignore"]}\n{t["ignore_desc"]}',use_container_width=True)

if "rounds" not in st.session_state: st.session_state.rounds=0
if "points" not in st.session_state: st.session_state.points=0
if "last_choice" not in st.session_state: st.session_state.last_choice=None
if choose_verify or choose_transfer or choose_wait:
 choice="verify" if choose_verify else "transfer" if choose_transfer else "wait"
 st.session_state.last_choice=(shipment_id,choice)
 st.session_state.rounds+=1
 # Illustrative game payoff: verify is best when data is missing/conflicting or temperature is out of range.
 best_choice="verify" if (missing or too_high or too_low) else "wait"
 points=100 if choice==best_choice else 35 if choice=="transfer" and (missing or too_high or too_low) else 0
 st.session_state.points+=points
 st.session_state.last_points=points
 st.session_state.last_best=(choice==best_choice)
 st.session_state.last_best_choice=best_choice
 st.session_state.last_reason=("Verification reduces uncertainty before a real action. The system cannot confirm physical conditions from this synthetic record." if best_choice=="verify" else "When the reading is within range and the sensor record is valid, continued monitoring is the lower-disruption choice in this training scenario.")
 st.rerun()

if st.session_state.last_choice and st.session_state.last_choice[0]==shipment_id:
 choice=st.session_state.last_choice[1]
 points=st.session_state.get("last_points",0)
 correct=st.session_state.get("last_best",False)
 st.markdown("---")
 st.markdown(f'<div class="panel" style="border-color:{"#4ade80" if correct else "#fbbf24"};animation:glow 2s infinite"><div class="eyebrow">{t["win"] if correct else t["lost"]}</div><div class="metric">{"+100" if points==100 else "+"+str(points) if points else "+0"} XP</div><div style="font-size:22px;font-weight:900;margin:8px 0">{t["best"] if correct else t["bad"]}</div><div style="font-size:18px">{t["good"] if correct else t["badmsg"]}</div><p>{st.session_state.get("last_reason","")}</p></div>',unsafe_allow_html=True)
 if correct:
  st.balloons()
 st.markdown(f'<div class="section">⚖️ {t["payoff"]}</div>',unsafe_allow_html=True)
 payoff=pd.DataFrame([
  {"Move":t["verify"],"Safety":"High","Time":"Medium","Uncertainty":"Low"},
  {"Move":t["move"],"Safety":"Depends on verification","Time":"Potentially faster","Uncertainty":"Still needs confirmation"},
  {"Move":t["ignore"],"Safety":"Poor if an alert is real","Time":"No immediate cost","Uncertainty":"Remains high"},
 ])
 st.dataframe(payoff,use_container_width=True,hide_index=True)
 st.markdown(f'**{t["what"]}** {st.session_state.last_reason}')
 st.progress(min(100,st.session_state.points%101)/100 if st.session_state.points%101 else (1.0 if st.session_state.points else 0.0),text=f'{t["score"]}: {st.session_state.points} XP  •  Rounds: {st.session_state.rounds}')
 if st.button(t["next"],use_container_width=True):
  st.session_state.last_choice=None
  st.rerun()

st.markdown(f'<div class="section">🏥 {t["fac"]}</div>',unsafe_allow_html=True)
st.caption(t["facnote"])
eligible=facilities[
 facilities["compatible_storage"].astype(str).str.lower().isin(["true","1","yes"])
 & (pd.to_numeric(facilities["spare_capacity_units"],errors="coerce")>=float(row["inventory_units"]))
].copy()
eligible["travel_time_min"]=pd.to_numeric(eligible["travel_time_min"],errors="coerce")
eligible=eligible.sort_values("travel_time_min")
if eligible.empty:
 st.warning(t["none"])
else:
 cols=st.columns(min(3,len(eligible)))
 for i,(_,f) in enumerate(eligible.iterrows()):
  with cols[i%len(cols)]:
   st.markdown(f'<div class="panel"><div style="font-size:23px">🏥 {f["name"]}</div><div class="metric">{int(f["travel_time_min"])} min</div><div>{int(f["spare_capacity_units"])} unit capacity</div><div class="small-label">candidate • confirm with staff</div></div>',unsafe_allow_html=True)

hist=readings[readings.shipment_id==shipment_id].copy()
hist["timestamp"]=pd.to_datetime(hist["timestamp"],errors="coerce")
hist["temperature_c"]=pd.to_numeric(hist["temperature_c"],errors="coerce")
hist=hist.dropna(subset=["timestamp","temperature_c"]).sort_values("timestamp")
if not hist.empty:
 st.markdown(f'<div class="section">📈 {t["history"]}</div>',unsafe_allow_html=True)
 st.line_chart(hist.set_index("timestamp")[["temperature_c"]],y_label="°C")
 st.caption("All plotted readings in this prototype are synthetic.")
with st.expander(t["staff"]):
 st.dataframe(pd.DataFrame([row]),use_container_width=True)
 st.write({"data_quality_status":qstatus,"inventory_units":int(row["inventory_units"]),"min_temp_c":low,"max_temp_c":high})
 st.dataframe(eligible,use_container_width=True)
if st.button(t["speak"],use_container_width=True):
 speech=f'{t["read"]} {shipment_id}. {status}. {t["temp"]} {temp} degrees Celsius. {t["range"]} {low} to {high} degrees Celsius.'
 # Use built-in browser speech synthesis. Text is derived from local demo data and fixed UI labels.
 components.html(f"""<script>const u=new SpeechSynthesisUtterance({speech!r});u.lang={{"English":"en-IN","தமிழ்":"ta-IN","తెలుగు":"te-IN"}}[{lang!r}];u.rate=0.86;window.speechSynthesis.cancel();window.speechSynthesis.speak(u);</script>""",height=0)
st.download_button("⬇️ Download demo shipment CSV",data=shipments.to_csv(index=False).encode("utf-8"),file_name="coldguardian_demo_shipments.csv",mime="text/csv",use_container_width=True)
st.markdown(f'<div class="panel" style="margin-top:24px"><div style="font-size:17px;font-weight:800">🛡️ {t["rule"]}</div><p>{t["foot"]}</p></div>',unsafe_allow_html=True)
