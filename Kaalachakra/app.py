import streamlit as st
import requests
from datetime import datetime
import pytz

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalchakra Live", page_icon="🕉️", layout="centered")

# -------------- CUSTOM STYLE ------------------
st.markdown("""
<style>
body {background-color:#0d0d0d;color:#f5f3e7;font-family:'Open Sans',sans-serif;}
h1,h2,h3 {color:#f4d03f;text-align:center;text-shadow:0 0 10px #f7dc6f,0 0 20px #f1c40f;font-family:'Cinzel Decorative',cursive;}
.css-18e3th9{background-color:#1a1a1a!important;border:1px solid #f1c40f;border-radius:15px;padding:1rem;}
hr{border:1px solid #f4d03f;box-shadow:0 0 5px #f4d03f;}
.footer{text-align:center;margin-top:40px;font-size:0.9rem;color:#aaa;}
.footer span{color:#f1c40f;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🕉️ Kaalchakra Live</h1><h3>Realtime Panchang — Paksha | Tithi | Nakshatra | Yoga | Karana | Vaar</h3>",
            unsafe_allow_html=True)

# ------------------- INPUTS -------------------
st.sidebar.header("🌍 Location & Timezone")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz = st.sidebar.text_input("Timezone", value="Asia/Kolkata")

# ------------------- TIME ---------------------
now = datetime.now(pytz.timezone(tz))
st.markdown(f"### 🕒 {now.strftime('%A, %d %B %Y | %I:%M %p')}")

# auto-refresh every minute
st_autorefresh = st.experimental_rerun  # compatibility alias
st_autorefresh_interval = 60000

# ------------------- API CALL -----------------
API_KEY = st.secrets.get("PROKERALA_API_KEY", "")
if not API_KEY:
    st.error("⚠️  Add PROKERALA_API_KEY in Streamlit → Settings → Secrets")
else:
    url = "https://api.prokerala.com/v2/astrology/panchang"
    params = {
        "ayanamsa": 1,
        "datetime": now.isoformat(),
        "latitude": lat,
        "longitude": lon
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
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

    except Exception as e:
        st.error(f"🚫 API Error: {e}")

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)