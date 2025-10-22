import math
from datetime import datetime, timedelta, timezone

import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe
from streamlit_autorefresh import st_autorefresh

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalchakra Live (Celestial Dashboard)", page_icon="🕉️", layout="centered")

# -------------- CUSTOM STYLE ------------------
st.markdown("""
<style>
body { background:#0d0d0d; color:#f5f3e7; font-family:'Open Sans',sans-serif; }
h1,h2,h3 { color:#f4d03f; text-align:center; text-shadow:0 0 10px #f7dc6f,0 0 20px #f1c40f;
            font-family:'Cinzel Decorative',cursive; }
hr { border:1px solid #f4d03f; box-shadow:0 0 5px #f4d03f; }
.card { background:#141414; border:1px solid #f1c40f33; border-radius:14px; padding:14px; margin:8px 0; }
.row { display:flex; gap:10px; flex-wrap:wrap; }
.col { flex:1 1 220px; }
.small { opacity:0.9; font-size:0.95rem; }
.footer { text-align:center; margin-top:28px; font-size:0.9rem; color:#aaa; }
.footer span { color:#f1c40f; }
</style>
""", unsafe_allow_html=True)

# ------------------- TITLE -------------------
st.markdown("""
<h1>🕉️ Kaalchakra Live</h1>
<h3>Drik Panchang • Sunrise-Based • Topocentric • Offline</h3>
""", unsafe_allow_html=True)

# ------------------- SIDEBAR INPUTS -------------------
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

# ---------- HELPERS ----------
def jd_to_local_dt(jd_ut: float, tzinfo: pytz.BaseTzInfo) -> datetime | None:
    """Convert Julian Day (UT) to timezone-aware datetime (local)."""
    if not jd_ut or math.isnan(jd_ut):
        return None
    y, m, d, ut = swe.revjul(jd_ut, swe.GREG_CAL)  # ut in hours
    dt_utc = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=ut)
    return dt_utc.astimezone(tzinfo)

def fmt_time(dt: datetime | None) -> str:
    return dt.strftime("%I:%M %p") if dt else "—"

def safe_rise_set(jd0: float, body: int, lon: float, lat: float, event_flag: int) -> float | None:
    """Return JD of rise/set or None if not found."""
    try:
        # BIT_DISC_CENTER = use disc center (common for civil sunrise)
        ret, tret = swe.rise_trans(jd0, body, lon, lat, rsmi=event_flag | swe.BIT_DISC_CENTER)
        return tret[0] if ret >= 0 else None
    except Exception:
        return None

def sun_moon_rise_set(local_date: datetime, lon: float, lat: float, tzinfo):
    # Use midnight UTC of the same LOCAL date as a start JD for search
    midnight_local = local_date.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = midnight_local.astimezone(pytz.utc)
    jd0 = swe.julday(midnight_utc.year, midnight_utc.month, midnight_utc.day, 0.0)

    sr_jd = safe_rise_set(jd0, swe.SUN, lon, lat, swe.CALC_RISE)
    ss_jd = safe_rise_set(jd0, swe.SUN, lon, lat, swe.CALC_SET)
    mr_jd = safe_rise_set(jd0, swe.MOON, lon, lat, swe.CALC_RISE)
    ms_jd = safe_rise_set(jd0, swe.MOON, lon, lat, swe.CALC_SET)

    return (
        jd_to_local_dt(sr_jd, tzinfo),
        jd_to_local_dt(ss_jd, tzinfo),
        jd_to_local_dt(mr_jd, tzinfo),
        jd_to_local_dt(ms_jd, tzinfo),
    )

def panchang_at_sunrise(local_date: datetime, lon: float, lat: float):
    """Compute Tithi, Nakshatra, Yoga, Karana, Paksha using topocentric positions at sunrise."""
    swe.set_topo(lon, lat, 0)  # observer position
    sr, _, _, _ = sun_moon_rise_set(local_date, lon, lat, tz)

    # Fallback: if sunrise not found, use 06:00 local
    calc_dt_local = sr or local_date.replace(hour=6, minute=0, second=0, microsecond=0)
    calc_dt_utc = calc_dt_local.astimezone(pytz.utc)
    jd = swe.julday(calc_dt_utc.year, calc_dt_utc.month, calc_dt_utc.day,
                    calc_dt_utc.hour + calc_dt_utc.minute/60 + calc_dt_utc.second/3600)

    sun_pos, _ = swe.calc_ut(jd, swe.SUN)   # returns (long, lat, dist, ..., ...)
    moon_pos, _ = swe.calc_ut(jd, swe.MOON)
    sun_long = sun_pos[0] % 360.0
    moon_long = moon_pos[0] % 360.0

    # Elongation
    elong = (moon_long - sun_long) % 360.0

    # Tithi
    tithi_num = int(elong // 12.0) + 1  # 1..30
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"

    # Nakshatra
    nak_size = 360.0 / 27.0
    nak_index = int((moon_long % 360.0) // nak_size)
    nakshatras = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
        "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
        "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
        "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
    ]
    nakshatra = nakshatras[nak_index]

    # Yoga
    yoga_index = int(((sun_long + moon_long) % 360.0) // nak_size)
    yogas = [
        "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti",
        "Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
        "Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
    ]
    yoga = yogas[yoga_index]

    # Karana (basic repeating set; precise fixed karanas around new/full moon not handled)
    karana_index = int((elong // 6.0) % 60)
    karanas_cycle = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"] * 9  # 63 -> take 60
    karana = karanas_cycle[karana_index]

    return {
        "paksha": paksha,
        "tithi_num": tithi_num,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "sunrise_dt": calc_dt_local
    }

def rahukaal(sr: datetime | None, ss: datetime | None, weekday: int):
    """Return Rahukaal start/end from sunrise-sunset split into 8 parts.
       weekday: Mon=0 ... Sun=6 (Python style)"""
    if not sr or not ss:
        return None, None
    day_len = (ss - sr).total_seconds()
    part = day_len / 8.0
    # Index map (1..8 segments): Sun(8), Mon(2), Tue(7), Wed(5), Thu(6), Fri(4), Sat(3)
    idx_map = {6:8, 0:2, 1:7, 2:5, 3:6, 4:4, 5:3}
    seg = idx_map[weekday] - 1  # zero-based
    start = sr + timedelta(seconds=part * seg)
    end = start + timedelta(seconds=part)
    return start, end

# ------------------- CALCULATE -------------------
try:
    # Rise/Set first
    sunrise, sunset, moonrise, moonset = sun_moon_rise_set(now_local, lon, lat, tz)
    # Panchang at sunrise
    p = panchang_at_sunrise(now_local, lon, lat)
    rk_start, rk_end = rahukaal(sunrise, sunset, now_local.weekday())

    # ------------------- RENDER -------------------
    st.markdown('<div class="row">', unsafe_allow_html=True)

    # Card: Rise/Set
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌅 Rise / Set")
    st.markdown(f"**Sunrise:** {fmt_time(sunrise)} &nbsp;&nbsp; **Sunset:** {fmt_time(sunset)}")
    st.markdown(f"**Moonrise:** {fmt_time(moonrise)} &nbsp;&nbsp; **Moonset:** {fmt_time(moonset)}")
    if rk_start and rk_end:
        st.markdown(f"<div class='small'>☄️ <b>Rahu Kaal:</b> {fmt_time(rk_start)} – {fmt_time(rk_end)}</div>",
                    unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Card: Panchang
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Panchang (Sunrise-based)")
    st.markdown(f"🌗 **Paksha:** {p['paksha']}")
    st.markdown(f"🌸 **Tithi:** {p['tithi_num']} / 30")
    st.markdown(f"✨ **Nakshatra:** {p['nakshatra']}")
    st.markdown(f"🪶 **Yoga:** {p['yoga']}")
    st.markdown(f"🌼 **Karana:** {p['karana']}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # row end
    st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)