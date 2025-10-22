import math
from datetime import datetime, timedelta, timezone
import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe
from streamlit_autorefresh import st_autorefresh
import geocoder
from timezonefinder import TimezoneFinder

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalachakra Live (GPS Recalibration Mode)", page_icon="🕉️", layout="centered")

# -------------- STYLE ------------------
st.markdown("""
<style>
body { background:#0d0d0d; color:#f5f3e7; font-family:'Open Sans',sans-serif; }
h1,h2,h3 { color:#f4d03f; text-align:center; text-shadow:0 0 10px #f7dc6f,0 0 20px #f1c40f;
            font-family:'Cinzel Decorative',cursive; }
hr { border:1px solid #f4d03f; box-shadow:0 0 5px #f4d03f; }
.card { background:#141414; border:1px solid #f1c40f33; border-radius:14px; padding:14px; margin:8px 0; }
.row { display:flex; gap:10px; flex-wrap:wrap; }
.col { flex:1 1 260px; }
.small { opacity:0.9; font-size:0.95rem; }
.footer { text-align:center; margin-top:28px; font-size:0.9rem; color:#aaa; }
.footer span { color:#f1c40f; }
</style>
""", unsafe_allow_html=True)

# ------------------- TITLE -------------------
st.markdown("""
<h1>🕉️ Kaalachakra Live</h1>
<h3>GPS Synced • Lahiri Sidereal • Sunrise Panchang</h3>
""", unsafe_allow_html=True)

# ------------------- GPS / LOCATION SECTION -------------------
st.sidebar.header("📍 Location Settings")

# JS for GPS Recalibration
gps_script = """
<script>
function fetchGPS() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude.toFixed(6);
                const lon = pos.coords.longitude.toFixed(6);
                const coords = lat + "," + lon;
                window.parent.postMessage({type:'gps_update', value:coords}, '*');
            },
            (err) => {
                window.parent.postMessage({type:'gps_error', value:err.message}, '*');
            }
        );
    } else {
        window.parent.postMessage({type:'gps_error', value:'Geolocation not supported'}, '*');
    }
}
</script>
<button onclick="fetchGPS()" style="
    background-color:#f4d03f;
    color:#000;
    font-weight:bold;
    border:none;
    border-radius:8px;
    padding:10px 18px;
    cursor:pointer;
    box-shadow:0 0 10px #f4d03f66;
    margin:10px auto;
    display:block;
">🔄 Recalibrate GPS</button>
"""

components.html(gps_script, height=100)

# Default values
lat, lon = 28.6139, 77.2090
tz_name = "Asia/Kolkata"
coords = st.session_state.get("gps_coords", None)

# Manual fallback input
use_auto = st.sidebar.checkbox("Use auto-detect (IP/GPS)", value=True)
if not use_auto:
    lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
    lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
    tz_name = st.sidebar.text_input("Timezone", value="Asia/Kolkata")

# Handle new GPS updates (JS → Streamlit bridge)
coords_box = st.empty()
coords_msg = components.html("""
<script>
window.addEventListener('message', (event) => {
  if (event.data.type === 'gps_update') {
    const coords = event.data.value;
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set('coords', coords);
    window.location.search = searchParams.toString();
  }
});
</script>
""", height=0)

# Check for new coords in query params
params = st.experimental_get_query_params()
if "coords" in params:
    coords = params["coords"][0]
    try:
        lat, lon = map(float, coords.split(","))
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
        st.session_state["gps_coords"] = coords
        st.success(f"📡 GPS recalibrated to {lat:.4f}, {lon:.4f} ({tz_name})")
    except:
        st.warning("⚠️ GPS data invalid — using last known location.")

# ------------------- CLOCK -------------------
components.html(f"""
<div style="text-align:center; margin-top:10px;">
  <h2 id="clock" style="color:#f4d03f;text-shadow:0 0 8px #f1c40f;font-family:'Courier New',monospace;font-size:1.5rem;"></h2>
</div>
<script>
function updateClock(){{
  const tz="{tz_name}";
  const now=new Date().toLocaleString("en-US",{{timeZone:tz}});
  const d=new Date(now);
  const opts={{weekday:'long',year:'numeric',month:'long',day:'numeric',
               hour:'2-digit',minute:'2-digit',second:'2-digit'}};
  document.getElementById('clock').innerHTML=d.toLocaleString('en-IN',opts);
}}
setInterval(updateClock,1000); updateClock();
</script>
""", height=65)
st.markdown("<hr style='margin-top:6px;margin-bottom:10px;'>", unsafe_allow_html=True)

st_autorefresh(interval=60000, key="kaalachakra_refresh")

# ------------------- TIME -------------------
tz = pytz.timezone(tz_name)
now_local = datetime.now(tz)
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')} — {tz_name}")

# ------------------- CONSTANTS -------------------
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
    "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
    "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
YOGAS = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti",
    "Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
    "Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
]
TITHIS = [
    "Shukla Pratipada","Shukla Dwitiya","Shukla Tritiya","Shukla Chaturthi","Shukla Panchami",
    "Shukla Shashthi","Shukla Saptami","Shukla Ashtami","Shukla Navami","Shukla Dashami",
    "Shukla Ekadashi","Shukla Dwadashi","Shukla Trayodashi","Shukla Chaturdashi","Purnima",
    "Krishna Pratipada","Krishna Dwitiya","Krishna Tritiya","Krishna Chaturthi","Krishna Panchami",
    "Krishna Shashthi","Krishna Saptami","Krishna Ashtami","Krishna Navami","Krishna Dashami",
    "Krishna Ekadashi","Krishna Dwadashi","Krishna Trayodashi","Krishna Chaturdashi","Amavasya"
]
KARANAS = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]

# ------------------- CALC HELPERS -------------------
def jd_to_local_dt(jd_ut):
    if not jd_ut: return None
    y, m, d, ut = swe.revjul(jd_ut, swe.GREG_CAL)
    dt_utc = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=ut)
    return dt_utc.astimezone(tz)

def fmt_time(dt):
    return dt.strftime("%I:%M %p") if dt else "—"

def rise_set_one(jd0, body, rsmi, lon, lat):
    try:
        ret, jdlist = swe.rise_trans(jd0, body, rsmi | swe.BIT_DISC_CENTER, (lon, lat, 0.0), 1013.25, 15.0)
        if ret >= 0:
            return jdlist[0] if isinstance(jdlist, (list, tuple)) else jdlist
    except Exception:
        pass
    return None

def sun_moon_rise_set(local_date, lon, lat):
    midnight_local = local_date.replace(hour=0, minute=0)
    midnight_utc = midnight_local.astimezone(pytz.utc)
    jd0 = swe.julday(midnight_utc.year, midnight_utc.month, midnight_utc.day, 0.0)
    sr = rise_set_one(jd0, swe.SUN,  swe.CALC_RISE, lon, lat)
    ss = rise_set_one(jd0, swe.SUN,  swe.CALC_SET,  lon, lat)
    mr = rise_set_one(jd0, swe.MOON, swe.CALC_RISE, lon, lat)
    ms = rise_set_one(jd0, swe.MOON, swe.CALC_SET,  lon, lat)
    return jd_to_local_dt(sr), jd_to_local_dt(ss), jd_to_local_dt(mr), jd_to_local_dt(ms), sr

def sidereal_longitudes(jd_ut, lon, lat):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun, _ = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    return sun[0] % 360, moon[0] % 360

def panchang(local_date, lon, lat):
    sunrise, _, _, _, sr_jd = sun_moon_rise_set(local_date, lon, lat)
    sun, moon = sidereal_longitudes(sr_jd, lon, lat)
    elong = (moon - sun) % 360
    t_idx = int(elong // 12)
    nak = NAKSHATRAS[int((moon % 360) // (360/27))]
    yoga = YOGAS[int(((sun + moon) % 360) // (360/27))]
    karana = (KARANAS * 9)[int((elong // 6) % 60)]
    return {"tithi": TITHIS[t_idx], "paksha": "Shukla" if t_idx < 15 else "Krishna",
            "nakshatra": nak, "yoga": yoga, "karana": karana, "sunrise": sunrise}

# ------------------- MAIN -------------------
try:
    sunrise, sunset, moonrise, moonset, _ = sun_moon_rise_set(now_local, lon, lat)
    p = panchang(now_local, lon, lat)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"## 📍 Location Synced — {lat:.4f}, {lon:.4f}")
    st.markdown('<div class="row">', unsafe_allow_html=True)

    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌅 Rise / Set")
    st.markdown(f"**Sunrise:** {fmt_time(sunrise)} | **Sunset:** {fmt_time(sunset)}")
    st.markdown(f"**Moonrise:** {fmt_time(moonrise)} | **Moonset:** {fmt_time(moonset)}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Panchang (Sunrise-based)")
    for key, val in p.items():
        if key != "sunrise":
            st.markdown(f"**{key.title()}:** {val}")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚫 Error: {e}")

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — GPS Recalibration Mode 🔄 Synced with your Sky 🌍✨
</div>
""", unsafe_allow_html=True)