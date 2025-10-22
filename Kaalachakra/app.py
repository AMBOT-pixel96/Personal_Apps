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
st.set_page_config(page_title="🕉️ Kaalachakra Live (Auto Mode)", page_icon="🕉️", layout="centered")

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
<h3>Auto-Detect Panchang • Sunrise-Based • Lahiri Sidereal • Offline</h3>
""", unsafe_allow_html=True)

# ------------------- LOCATION AUTO-DETECT -------------------
st.sidebar.header("📍 Location Settings")

# Auto-detect location via IP
auto = st.sidebar.checkbox("Auto-detect my location 🌍", value=True)

if auto:
    g = geocoder.ip("me")
    if g.ok and g.latlng:
        lat, lon = g.latlng
        try:
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lat=lat, lng=lon)
        except Exception:
            tz_name = "Asia/Kolkata"
        st.sidebar.success(f"📡 Detected: {g.city or 'Unknown City'} ({lat:.2f}, {lon:.2f})")
    else:
        st.sidebar.warning("⚠️ Couldn’t auto-detect. Using Delhi by default.")
        lat, lon, tz_name = 28.6139, 77.2090, "Asia/Kolkata"
else:
    lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
    lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
    tz_name = st.sidebar.text_input("Timezone (IANA, e.g. Asia/Kolkata)", value="Asia/Kolkata")

# ------------------- LIVE CLOCK -------------------
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
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')} — <span class='small'>{tz_name}</span>", unsafe_allow_html=True)

# ---------- CONSTANTS ----------
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
KARANAS_MOVABLE = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]

# ---------- HELPER FUNCTIONS ----------
def jd_to_local_dt(jd_ut):
    if not jd_ut or (isinstance(jd_ut, float) and math.isnan(jd_ut)):
        return None
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
    midnight_local = local_date.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = midnight_local.astimezone(pytz.utc)
    jd0 = swe.julday(midnight_utc.year, midnight_utc.month, midnight_utc.day, 0.0)
    sr = rise_set_one(jd0, swe.SUN,  swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.SUN,  swe.CALC_RISE, lon, lat)
    ss = rise_set_one(jd0, swe.SUN,  swe.CALC_SET,  lon, lat) or rise_set_one(jd0+1, swe.SUN,  swe.CALC_SET,  lon, lat)
    mr = rise_set_one(jd0, swe.MOON, swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_RISE, lon, lat)
    ms = rise_set_one(jd0, swe.MOON, swe.CALC_SET,  lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_SET,  lon, lat)
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
    if sr_jd is None:
        lf = local_date.replace(hour=6, minute=0).astimezone(pytz.utc)
        sr_jd = swe.julday(lf.year, lf.month, lf.day, lf.hour)
    sun, moon = sidereal_longitudes(sr_jd, lon, lat)
    elong = (moon - sun) % 360
    t_idx = int(elong // 12)
    t_name = TITHIS[t_idx]
    paksha = "Shukla" if t_idx < 15 else "Krishna"
    nak = NAKSHATRAS[int((moon % 360) // (360/27))]
    yoga = YOGAS[int(((sun + moon) % 360) // (360/27))]
    karana = (KARANAS_MOVABLE * 9)[int((elong // 6) % 60)]
    return {"tithi": t_name, "paksha": paksha, "nakshatra": nak, "yoga": yoga, "karana": karana, "sunrise": sunrise}

def rahukaal(sr, ss, weekday):
    if not sr or not ss: return None, None
    part = (ss - sr).total_seconds() / 8
    idx_map = {6:8, 0:2, 1:7, 2:5, 3:6, 4:4, 5:3}
    seg = idx_map[weekday] - 1
    start = sr + timedelta(seconds=part * seg)
    return start, start + timedelta(seconds=part)

# ------------------- MAIN -------------------
try:
    sunrise, sunset, moonrise, moonset, _ = sun_moon_rise_set(now_local, lon, lat)
    p = panchang(now_local, lon, lat)
    rk_start, rk_end = rahukaal(sunrise, sunset, now_local.weekday())

    st.markdown('<div class="row">', unsafe_allow_html=True)
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌅 Rise / Set")
    st.markdown(f"**Sunrise:** {fmt_time(sunrise)} &nbsp; **Sunset:** {fmt_time(sunset)}")
    st.markdown(f"**Moonrise:** {fmt_time(moonrise)} &nbsp; **Moonset:** {fmt_time(moonset)}")
    if rk_start: st.markdown(f"<div class='small'>☄️ <b>Rahu Kaal:</b> {fmt_time(rk_start)}–{fmt_time(rk_end)}</div>", unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Panchang (Sunrise-based)")
    st.markdown(f"🌸 **Tithi:** {p['tithi']}")
    st.markdown(f"🌗 **Paksha:** {p['paksha']}")
    st.markdown(f"✨ **Nakshatra:** {p['nakshatra']}")
    st.markdown(f"🪶 **Yoga:** {p['yoga']}")
    st.markdown(f"🌼 **Karana:** {p['karana']}")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚫 Error: {e}")

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Auto-synced with your cosmos 🌍⚡
</div>
""", unsafe_allow_html=True)