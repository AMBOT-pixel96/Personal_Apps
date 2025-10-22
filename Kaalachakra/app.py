import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalchakra Live", page_icon="🕉️", layout="centered")

# -------------- CUSTOM STYLE ------------------
st.markdown("""
<style>
body {
    background-color:#0d0d0d;
    color:#f5f3e7;
    font-family:'Open Sans',sans-serif;
}
h1,h2,h3 {
    color:#f4d03f;
    text-align:center;
    text-shadow:0 0 10px #f7dc6f,0 0 20px #f1c40f;
    font-family:'Cinzel Decorative',cursive;
}
.css-18e3th9 {
    background-color:#1a1a1a!important;
    border:1px solid #f1c40f;
    border-radius:15px;
    padding:1rem;
}
hr {
    border:1px solid #f4d03f;
    box-shadow:0 0 5px #f4d03f;
}
.footer {
    text-align:center;
    margin-top:40px;
    font-size:0.9rem;
    color:#aaa;
}
.footer span { color:#f1c40f; }
</style>
""", unsafe_allow_html=True)

# ------------------- TITLE -------------------
st.markdown("""
<h1>🕉️ Kaalchakra Live</h1>
<h3>Realtime Panchang — Paksha | Tithi | Nakshatra | Yoga | Karana | Vaar</h3>
""", unsafe_allow_html=True)

# ------------------- INPUTS -------------------
st.sidebar.header("🌍 Location & Timezone")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz = st.sidebar.text_input("Timezone (e.g. Asia/Kolkata)", value="Asia/Kolkata")

# ------------------- LIVE CLOCK (JS, synced to timezone) -------------------
clock_html = f"""
<div style="text-align:center; margin-top:10px;">
  <h2 id="clock" style="
      color:#f4d03f;
      text-shadow:0px 0px 8px #f1c40f;
      font-family:'Courier New', monospace;
      font-size:1.5rem;">
  </h2>
</div>

<script>
function updateClock() {{
  const tz = "{tz}";
  const now = new Date().toLocaleString("en-US", {{timeZone: tz}});
  const dateObj = new Date(now);
  const options = {{
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
  }};
  const timeString = dateObj.toLocaleString('en-IN', options);
  document.getElementById('clock').innerHTML = timeString;
}}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
components.html(clock_html, height=65)
st.markdown("<hr style='margin-top:5px;margin-bottom:10px;'>", unsafe_allow_html=True)

# ------------------- AUTO REFRESH -------------------
# Refresh every 60 seconds (60000 ms)
st_autorefresh(interval=60000, key="kaalachakra_refresh")

# ------------------- TIME (for backend API call) -------------------
now = datetime.now(pytz.timezone(tz))
st.markdown(f"### 🕒 {now.strftime('%A, %d %B %Y | %I:%M %p')}")

# STEP 2: Panchang API call
panchang_url = "https://api.prokerala.com/v2/astrology/panchang"
formatted_dt = now.strftime("%Y-%m-%dT%H:%M:%S%z")
# Add colon in timezone offset → +05:30
formatted_dt = formatted_dt[:-2] + ":" + formatted_dt[-2:]

params = {
    "ayanamsa": 1,
    "datetime": formatted_dt,
    "latitude": lat,
    "longitude": lon
}

auth_header = {"Authorization": f"Bearer {access_token}"}

resp = requests.get(panchang_url, params=params, headers=auth_header, timeout=10)
resp.raise_for_status()
data = resp.json()
p = data.get("data", {}).get("panchang", {})

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("## 🔮 **Panchang Details**")
st.markdown(f"🌗 **Paksha:**  {p.get('paksha','—')}")
st.markdown(f"🌸 **Tithi:**  {p.get('tithi',{}).get('name','—')}")
st.markdown(f"✨ **Nakshatra:**  {p.get('nakshatra',{}).get('name','—')}")
st.markdown(f"🪶 **Yoga:**  {p.get('yoga',{}).get('name','—')}")
st.markdown(f"🌼 **Karana:**  {p.get('karana',{}).get('name','—')}")
st.markdown(f"📿 **Vaar (Day):**  {p.get('day',{}).get('name','—')}")
st.markdown("<hr>", unsafe_allow_html=True)
# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)