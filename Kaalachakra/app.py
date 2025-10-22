import math
from datetime import datetime, timedelta, timezone

import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe
from streamlit_autorefresh import st_autorefresh

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalchakra Live (Celestial Dashboard)", page_icon="🕉️", layout="centered")

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
<h1>🕉️ Kaalchakra Live</h1>
<h3>Drik Panchang • Sunrise-Based • Lahiri Sidereal • Offline</h3>
""", unsafe_allow_html=True)

# ------------------- SIDEBAR -------------------
st.sidebar.header("🌍 Location & Timezone")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz_name = st.sidebar.text_input("Timezone (e.g. Asia/Kolkata)", value="Asia/Kolkata")

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

# ------------------- AUTO REFRESH -------------------
st_autorefresh(interval=60000, key="kaalachakra_refresh")

# ------------------- TIME -------------------
tz = pytz.timezone(tz_name)
now_local = datetime.now(tz)
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')}")

# ---------- CONSTANTS & TABLES ----------
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
KARANAS_MOVABLE = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]  # repeating 7

# ---------- HELPERS ----------
def jd_to_local_dt(jd_ut: float) -> datetime | None:
    if not jd_ut or math.isnan(jd_ut):
        return None
    y, m, d, ut = swe.revjul(jd_ut, swe.GREG_CAL)  # 'ut' in hours
    dt_utc = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=ut)
    return dt_utc.astimezone(tz)

def fmt_time(dt: datetime | None) -> str:
    return dt.strftime("%I:%M %p") if dt else "—"

def rise_set_one(jd0_ut: float, body: int, rsmi: int, lon: float, lat: float) -> float | None:
    """
    Swiss Ephemeris rise/set correct signature:
    swe.rise_trans(jd_ut, body, rsmi, geopos=(lon,lat,alt), atpress, attemp)
    Returns (ret, jd_list), we take jd_list[0] if ret>=0
    """
    try:
        ret, jdlist = swe.rise_trans(jd0_ut, body, rsmi | swe.BIT_DISC_CENTER,
                                     (lon, lat, 0.0), 1013.25, 15.0)
        if ret >= 0:
            # jdlist can be a float or a list/tuple
            return jdlist[0] if isinstance(jdlist, (list, tuple)) else jdlist
        return None
    except Exception:
        return None

def sun_moon_rise_set(local_date: datetime, lon: float, lat: float):
    # Start searching from UTC midnight of local date
    midnight_local = local_date.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = midnight_local.astimezone(pytz.utc)
    jd0 = swe.julday(midnight_utc.year, midnight_utc.month, midnight_utc.day, 0.0)

    sr = rise_set_one(jd0, swe.SUN,  swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.SUN,  swe.CALC_RISE, lon, lat)
    ss = rise_set_one(jd0, swe.SUN,  swe.CALC_SET,  lon, lat) or rise_set_one(jd0+1, swe.SUN,  swe.CALC_SET,  lon, lat)
    mr = rise_set_one(jd0, swe.MOON, swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_RISE, lon, lat)
    ms = rise_set_one(jd0, swe.MOON, swe.CALC_SET,  lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_SET,  lon, lat)

    return (jd_to_local_dt(sr), jd_to_local_dt(ss), jd_to_local_dt(mr), jd_to_local_dt(ms), sr)

def sidereal_longitudes(jd_ut: float, lon: float, lat: float):
    """Lahiri sidereal, topocentric longitudes of Sun & Moon (0..360)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)          # Lahiri ayanamsa (Drik standard)
    swe.set_topo(lon, lat, 0.0)                # observer
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TOPO  # Swiss eph, sidereal, topo
    sun_pos, _ = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon_pos, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    return (sun_pos[0] % 360.0, moon_pos[0] % 360.0)

def panchang_at_sunrise(local_date: datetime, lon: float, lat: float):
    # Get sunrise JD; if not found, use 06:00 local fallback
    sunrise_local, _, _, _, sr_jd = sun_moon_rise_set(local_date, lon, lat)
    if sr_jd is None:
        # fallback: 06:00 local time
        local_fallback = local_date.replace(hour=6, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        sr_jd = swe.julday(local_fallback.year, local_fallback.month, local_fallback.day,
                           local_fallback.hour + local_fallback.minute/60 + local_fallback.second/3600)

    # Sidereal longitudes at sunrise
    sun_long, moon_long = sidereal_longitudes(sr_jd, lon, lat)

    # Tithi (each 12° elongation of Moon-Sun)
    elong = (moon_long - sun_long) % 360.0
    tithi_idx = int(elong // 12.0)             # 0..29
    tithi_name = TITHIS[tithi_idx]
    paksha = "Shukla" if tithi_idx < 15 else "Krishna"

    # Nakshatra (each 13°20' = 360/27)
    nak_size = 360.0 / 27.0
    nak_index = int((moon_long % 360.0) // nak_size)
    nakshatra = NAKSHATRAS[nak_index]

    # Yoga (sum of longitudes, sidereal)
    yoga_index = int(((sun_long + moon_long) % 360.0) // nak_size)
    yoga = YOGAS[yoga_index]

    # Karana (basic repeating series; precise fixed karanas not handled here)
    karana_idx = int((elong // 6.0) % 60)
    karana = (KARANAS_MOVABLE * 9)[karana_idx]  # 63 items; we use first 60

    return {
        "sunrise_local": sunrise_local,
        "tithi_name": tithi_name,
        "paksha": paksha,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana
    }

def rahukaal(sr: datetime | None, ss: datetime | None, weekday: int):
    if not sr or not ss:
        return None, None
    day_len = (ss - sr).total_seconds()
    part = day_len / 8.0
    # Python weekday(): Mon=0..Sun=6
    idx_map = {6:8, 0:2, 1:7, 2:5, 3:6, 4:4, 5:3}
    seg = idx_map[weekday] - 1
    start = sr + timedelta(seconds=part * seg)
    end = start + timedelta(seconds=part)
    return start, end

# ------------------- CALCULATE & RENDER -------------------
try:
    sunrise, sunset, moonrise, moonset, _ = sun_moon_rise_set(now_local, lon, lat)
    p = panchang_at_sunrise(now_local, lon, lat)
    rk_start, rk_end = rahukaal(sunrise, sunset, now_local.weekday())

    st.markdown('<div class="row">', unsafe_allow_html=True)

    # Rise/Set card
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌅 Rise / Set")
    st.markdown(f"**Sunrise:** {fmt_time(sunrise)} &nbsp;&nbsp; **Sunset:** {fmt_time(sunset)}")
    st.markdown(f"**Moonrise:** {fmt_time(moonrise)} &nbsp;&nbsp; **Moonset:** {fmt_time(moonset)}")
    if rk_start and rk_end:
        st.markdown(f"<div class='small'>☄️ <b>Rahu Kaal:</b> {fmt_time(rk_start)} – {fmt_time(rk_end)}</div>",
                    unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Panchang card
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Panchang (Sunrise-based, Sidereal)")
    st.markdown(f"🌸 **Tithi:** {p['tithi_name']}")
    st.markdown(f"🌗 **Paksha:** {p['paksha']}")
    st.markdown(f"✨ **Nakshatra:** {p['nakshatra']}")
    st.markdown(f"🪶 **Yoga:** {p['yoga']}")
    st.markdown(f"🌼 **Karana:** {p['karana']}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # row end
    st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")
    # st.exception(e)  # uncomment to see stack trace in UI

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)