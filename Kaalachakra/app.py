import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import pytz
import swisseph as swe

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalachakra Live", page_icon="🕉️", layout="centered")

# ------------------- PANCHANG DATA -------------------
TITHIS = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima", "Pratipada", "Dvitiya", "Tritiya",
    "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami",
    "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
    "Vaidhriti"
]

KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti", "Shakuni",
    "Chatushpada", "Naga", "Kimstughna"
]

# ------------------- STYLES -------------------
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
<h1>🕉️ Kaalachakra Live</h1>
<h3>Realtime Panchang — Paksha | Tithi | Nakshatra | Yoga | Karana | Vaar</h3>
""", unsafe_allow_html=True)

# ------------------- LOCATION INPUTS -------------------
st.sidebar.header("🌍 Location & Timezone")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz = st.sidebar.text_input("Timezone (e.g. Asia/Kolkata)", value="Asia/Kolkata")

# ------------------- LIVE CLOCK -------------------
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

# ------------------- HELPER FUNCTIONS -------------------
def jd_to_local_dt(jd):
    if jd is None:
        return None
    utc_time = swe.revjul(jd, swe.GREG_CAL)
    dt = datetime(utc_time[0], utc_time[1], utc_time[2], int(utc_time[3]), int((utc_time[3] % 1) * 60), tzinfo=pytz.utc)
    return dt.astimezone(pytz.timezone(tz))

def sun_moon_rise_set(local_date, lon, lat):
    """Accurate sunrise/sunset using Swiss Ephemeris local JD."""
    swe.set_topo(lon, lat, 0)
    local_midnight = local_date.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_midnight = local_midnight.astimezone(pytz.utc)
    jd0 = swe.julday(utc_midnight.year, utc_midnight.month, utc_midnight.day, 0)
    rsmi = swe.BIT_DISC_CENTER | swe.CALC_RISE

    def get_event(body, mode):
        try:
            ret, jdlist = swe.rise_trans(jd0, body, mode, (lon, lat, 0.0), 1013.25, 15.0)
            if ret >= 0:
                return jdlist[0]
        except Exception:
            return None
        return None

    sr = get_event(swe.SUN, swe.CALC_RISE)
    ss = get_event(swe.SUN, swe.CALC_SET)
    mr = get_event(swe.MOON, swe.CALC_RISE)
    ms = get_event(swe.MOON, swe.CALC_SET)

    return jd_to_local_dt(sr), jd_to_local_dt(ss), jd_to_local_dt(mr), jd_to_local_dt(ms), sr

def sidereal_longitudes(jd_ut, lon, lat):
    """Precise Lahiri sidereal longitudes for Sun/Moon."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun, _ = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    return sun[0] % 360, moon[0] % 360

def panchang(local_date, lon, lat):
    """Computes Panchang using true sunrise."""
    sunrise, sunset, moonrise, moonset, sr_jd = sun_moon_rise_set(local_date, lon, lat)
    sun, moon = sidereal_longitudes(sr_jd, lon, lat)
    elong = (moon - sun) % 360

    t_idx = int(elong // 12)
    paksha = "Shukla" if t_idx < 15 else "Krishna"
    tithi = TITHIS[t_idx]

    nak = NAKSHATRAS[int((moon % 360) // (360 / 27))]
    yoga = YOGAS[int(((sun + moon) % 360) // (360 / 27))]
    karana = (KARANAS * 9)[int((elong // 6) % 60)]

    return {
        "paksha": paksha,
        "tithi": tithi,
        "nakshatra": nak,
        "yoga": yoga,
        "karana": karana,
        "sunrise": sunrise,
        "sunset": sunset,
        "moonrise": moonrise,
        "moonset": moonset
    }

# ------------------- DISPLAY -------------------
now_local = datetime.now(pytz.timezone(tz))
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')}")

try:
    p = panchang(now_local, lon, lat)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("## 🌅 **Rise / Set**")
    st.markdown(f"**Sunrise:** {p['sunrise'].strftime('%I:%M %p')} | **Sunset:** {p['sunset'].strftime('%I:%M %p')}")
    st.markdown(f"**Moonrise:** {p['moonrise'].strftime('%I:%M %p')} | **Moonset:** {p['moonset'].strftime('%I:%M %p')}")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("## 🔮 **Panchang (Sunrise-based)**")
    st.markdown(f"**Tithi:** {p['tithi']}")
    st.markdown(f"**Paksha:** {p['paksha']}")
    st.markdown(f"**Nakshatra:** {p['nakshatra']}")
    st.markdown(f"**Yoga:** {p['yoga']}")
    st.markdown(f"**Karana:** {p['karana']}")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Future button placeholder for Sankalpa module
    st.markdown("""
        <div style='text-align:center;'>
            <button style='background:#f4d03f;color:#000;font-weight:bold;
            padding:10px 20px;border:none;border-radius:10px;font-size:1rem;'>
            🪔 Generate Sankalpa
            </button>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Calculation Error: {e}")

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)