import math
from datetime import datetime, timedelta, timezone

import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe

# =================== CONFIG ===================
st.set_page_config(page_title="🕉️ Kaalachakra Live — v7.0", page_icon="🕉️", layout="centered")

# ============== UI STYLE ==============
st.markdown("""
<style>
body { background:#0d0d0d; color:#f5f3e7; font-family:system-ui, -apple-system, Segoe UI, Roboto, 'Open Sans', sans-serif; }
h1,h2,h3 { color:#f4d03f; text-align:center; text-shadow:0 0 10px #f7dc6f, 0 0 20px #f1c40f; font-family:'Cinzel Decorative',cursive; }
hr { border:1px solid #f4d03f; box-shadow:0 0 5px #f4d03f; }
.card { background:#141414; border:1px solid #f1c40f33; border-radius:14px; padding:14px; margin:10px 0; }
.row { display:flex; gap:12px; flex-wrap:wrap; }
.col { flex:1 1 320px; }
.small { opacity:0.9; font-size:0.95rem; }
.kbutton { background:#f4d03f; color:#000; font-weight:700; padding:10px 18px; border:none; border-radius:10px; cursor:pointer; box-shadow:0 0 10px #f4d03f66; }
.footer { text-align:center; margin-top:28px; font-size:0.9rem; color:#aaa; }
.footer span { color:#f1c40f; }
code { background:#000; padding:2px 6px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# ============== TITLE ==============
st.markdown("<h1>🕉️ Kaalachakra Live</h1><h3>Drik-style • Sunrise-based • Lahiri Sidereal • Topocentric</h3>", unsafe_allow_html=True)

# ============== CONSTANT TABLES ==============
TITHIS = [
    "Shukla Pratipada","Shukla Dwitiya","Shukla Tritiya","Shukla Chaturthi","Shukla Panchami",
    "Shukla Shashthi","Shukla Saptami","Shukla Ashtami","Shukla Navami","Shukla Dashami",
    "Shukla Ekadashi","Shukla Dwadashi","Shukla Trayodashi","Shukla Chaturdashi","Purnima",
    "Krishna Pratipada","Krishna Dwitiya","Krishna Tritiya","Krishna Chaturthi","Krishna Panchami",
    "Krishna Shashthi","Krishna Saptami","Krishna Ashtami","Krishna Navami","Krishna Dashami",
    "Krishna Ekadashi","Krishna Dwadashi","Krishna Trayodashi","Krishna Chaturdashi","Amavasya"
]
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
KARANAS_MOVABLE = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]  # repeating sequence

# ============== SIDEBAR INPUTS ==============
st.sidebar.header("🌍 Location & Settings")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz_name = st.sidebar.text_input("Timezone (IANA, e.g. Asia/Kolkata)", value="Asia/Kolkata")
show_debug = st.sidebar.checkbox("Show debug panel", value=False)

# ============== LIVE CLOCK ==============
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
st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)

tz = pytz.timezone(tz_name)
now_local = datetime.now(tz)
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')} — <span class='small'>{tz_name}</span>", unsafe_allow_html=True)

# ============== CORE ASTRONOMY HELPERS ==============
def jd_to_local_dt(jd_ut: float) -> datetime | None:
    if jd_ut is None or (isinstance(jd_ut, float) and math.isnan(jd_ut)):
        return None
    y, m, d, ut = swe.revjul(jd_ut, swe.GREG_CAL)  # UT hours
    dt_utc = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=ut)
    return dt_utc.astimezone(tz)

def fmt_time(dt: datetime | None) -> str:
    return dt.strftime("%I:%M %p") if dt else "—"

def rise_set_one(jd0_ut: float, body: int, mode: int, lon: float, lat: float) -> float | None:
    """Version-proof sunrise/sunset/moonrise/moonset."""
    try:
        ret, jdlist = swe.rise_trans(
            jd0_ut, body, mode | swe.BIT_DISC_CENTER,
            (lon, lat, 0.0), 1013.25, 15.0
        )
        if ret >= 0:
            return jdlist[0] if isinstance(jdlist, (list, tuple)) else jdlist
    except Exception:
        pass
    return None

def sun_moon_rise_set(local_date: datetime, lon: float, lat: float):
    """Sunrise/sunset/moonrise/moonset for the local date (with day+1 fallback)."""
    swe.set_topo(lon, lat, 0.0)
    midnight_local = local_date.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = midnight_local.astimezone(pytz.utc)
    jd0 = swe.julday(midnight_utc.year, midnight_utc.month, midnight_utc.day, 0.0)

    sr = rise_set_one(jd0, swe.SUN,  swe.CALC_RISE, lon, lat)  or rise_set_one(jd0+1, swe.SUN,  swe.CALC_RISE, lon, lat)
    ss = rise_set_one(jd0, swe.SUN,  swe.CALC_SET,  lon, lat)  or rise_set_one(jd0+1, swe.SUN,  swe.CALC_SET,  lon, lat)
    mr = rise_set_one(jd0, swe.MOON, swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_RISE, lon, lat)
    ms = rise_set_one(jd0, swe.MOON, swe.CALC_SET,  lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_SET,  lon, lat)

    return jd_to_local_dt(sr), jd_to_local_dt(ss), jd_to_local_dt(mr), jd_to_local_dt(ms), sr

def sidereal_longitudes(jd_ut: float, lon: float, lat: float):
    """Lahiri sidereal, topocentric Sun & Moon longitudes at jd_ut (0..360)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0.0)
    FLG_TOPOCTR = getattr(swe, "FLG_TOPOCTR", 0)  # available in some builds
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | FLG_TOPOCTR
    sun_pos, _ = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon_pos, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    return sun_pos[0] % 360.0, moon_pos[0] % 360.0

# ============== PANCHANG INDICES ==============
STEP_NAK = 360.0 / 27.0

def tithi_index(sun_long: float, moon_long: float) -> int:
    return int(((moon_long - sun_long) % 360.0) // 12.0)  # 0..29

def nak_index(moon_long: float) -> int:
    return int((moon_long % 360.0) // STEP_NAK)  # 0..26

def yoga_index(sun_long: float, moon_long: float) -> int:
    return int(((sun_long + moon_long) % 360.0) // STEP_NAK)  # 0..26

def karana_name(sun_long: float, moon_long: float) -> str:
    elong = (moon_long - sun_long) % 360.0
    idx = int((elong // 6.0) % 60)
    return (KARANAS_MOVABLE * 9)[idx]  # simple movable cycle

# ============== TRANSITION FINDER (for “ends at”) ==============
def find_next_change(jd_start: float, lon: float, lat: float, kind: str, current_idx: int, max_hours: int = 48) -> float | None:
    """
    Find the next time (JD) when the given index (tithi/nak/yoga) changes.
    Coarse scan hourly, then binary search to minute precision.
    """
    def idx_at(jd):
        s, m = sidereal_longitudes(jd, lon, lat)
        if kind == "tithi":   return tithi_index(s, m)
        if kind == "nak":     return nak_index(m)
        if kind == "yoga":    return yoga_index(s, m)
        return None

    # Coarse scan
    step = 1.0 / 24.0  # 1 hour
    jd_prev = jd_start
    prev_idx = current_idx
    for _ in range(max_hours):
        jd_next = jd_prev + step
        nxt_idx = idx_at(jd_next)
        if nxt_idx is None:
            return None
        if nxt_idx != prev_idx:
            # binary search in [jd_prev, jd_next]
            lo, hi = jd_prev, jd_next
            for _ in range(24):  # ~2.5 sec granularity
                mid = (lo + hi) / 2.0
                im = idx_at(mid)
                if im == prev_idx:
                    lo = mid
                else:
                    hi = mid
            return hi
        jd_prev, prev_idx = jd_next, nxt_idx
    return None

# ============== MAIN PANCHANG ==============
def compute_panchang_for_date(local_date: datetime, lon: float, lat: float):
    # 1) Rise/Set (get sunrise JD)
    sr_local, ss_local, mr_local, ms_local, sr_jd = sun_moon_rise_set(local_date, lon, lat)

    # 2) Evaluate AT sunrise + 1 minute (avoid boundary flicker)
    eval_local = (sr_local or local_date.replace(hour=6, minute=0, second=0, microsecond=0)) + timedelta(minutes=1)
    eval_utc = eval_local.astimezone(pytz.utc)
    jd_eval = swe.julday(eval_utc.year, eval_utc.month, eval_utc.day,
                         eval_utc.hour + eval_utc.minute/60 + eval_utc.second/3600)

    # 3) Sidereal longs (Lahiri, topocentric)
    sun_long, moon_long = sidereal_longitudes(jd_eval, lon, lat)
    elong = (moon_long - sun_long) % 360.0

    # 4) Panchang pieces
    ti = tithi_index(sun_long, moon_long)            # 0..29
    ni = nak_index(moon_long)                        # 0..26
    yi = yoga_index(sun_long, moon_long)             # 0..26
    tithi_name = TITHIS[ti]
    nak_name = NAKSHATRAS[ni]
    yoga_name = YOGAS[yi]
    paksha = "Shukla" if ti < 15 else "Krishna"
    karana = karana_name(sun_long, moon_long)

    # 5) Next change times
    tithi_change_jd = find_next_change(jd_eval, lon, lat, "tithi", ti)
    nak_change_jd   = find_next_change(jd_eval, lon, lat, "nak",   ni)
    yoga_change_jd  = find_next_change(jd_eval, lon, lat, "yoga",  yi)

    return {
        "sunrise": sr_local, "sunset": ss_local, "moonrise": mr_local, "moonset": ms_local,
        "sun_long": sun_long, "moon_long": moon_long, "elong": elong,
        "tithi": tithi_name, "paksha": paksha, "nakshatra": nak_name, "yoga": yoga_name, "karana": karana,
        "tithi_ends": jd_to_local_dt(tithi_change_jd),
        "nak_ends": jd_to_local_dt(nak_change_jd),
        "yoga_ends": jd_to_local_dt(yoga_change_jd)
    }

# ============== RUN & RENDER ==============
try:
    p = compute_panchang_for_date(now_local, lon, lat)

    st.markdown('<div class="row">', unsafe_allow_html=True)

    # Rise/Set
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌅 Rise / Set")
    st.markdown(f"**Sunrise:** {fmt_time(p['sunrise'])} &nbsp;&nbsp; **Sunset:** {fmt_time(p['sunset'])}")
    st.markdown(f"**Moonrise:** {fmt_time(p['moonrise'])} &nbsp;&nbsp; **Moonset:** {fmt_time(p['moonset'])}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Panchang
    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Panchang (Sunrise-based)")
    st.markdown(f"🌸 **Tithi:** {p['tithi']}  <span class='small'>(ends {fmt_time(p['tithi_ends'])})</span>", unsafe_allow_html=True)
    st.markdown(f"🌗 **Paksha:** {p['paksha']}")
    st.markdown(f"✨ **Nakshatra:** {p['nakshatra']}  <span class='small'>(ends {fmt_time(p['nak_ends'])})</span>", unsafe_allow_html=True)
    st.markdown(f"🪶 **Yoga:** {p['yoga']}  <span class='small'>(ends {fmt_time(p['yoga_ends'])})</span>", unsafe_allow_html=True)
    st.markdown(f"🌼 **Karana:** {p['karana']}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # row end
    st.markdown("<hr>", unsafe_allow_html=True)

    # Generate Sankalpa button (placeholder – we wire the dialog next)
    st.markdown("<div style='text-align:center'><button class='kbutton'>🪔 Generate Sankalpa</button></div>", unsafe_allow_html=True)

    # Debug panel
    if show_debug:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🧪 Debug")
        st.caption(f"☀️ Sun λ = {p['sun_long']:.6f}°  |  🌙 Moon λ = {p['moon_long']:.6f}°  |  Δ = {p['elong']:.6f}°")
        st.caption(f"tithi_idx = {TITHIS.index(p['tithi'])}  |  nak_idx = {NAKSHATRAS.index(p['nakshatra'])}  |  yoga_idx = {YOGAS.index(p['yoga'])}")

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

# ============== FOOTER ==============
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — v7.0 Cosmic Accuracy Edition (Swiss Ephemeris • Lahiri • Topocentric)
</div>
""", unsafe_allow_html=True)