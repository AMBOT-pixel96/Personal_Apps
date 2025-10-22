import math
from datetime import datetime, timedelta, timezone

import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe

# =================== CONFIG ===================
st.set_page_config(page_title="🕉️ Kaalachakra Live — v8.0 (Drik Emulation)", page_icon="🕉️", layout="centered")

# =================== UI STYLE ===================
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

# =================== TITLE ===================
st.markdown("<h1>🕉️ Kaalachakra Live</h1><h3>Drik-style • Sunrise-based • Lahiri Sidereal • Topocentric</h3>", unsafe_allow_html=True)

# =================== CONSTANT TABLES ===================
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

# Karanas – full 60-half sequence (0..59) per classical rule:
# 0: Kinstughna, 1..56: 7 movables repeat, 57: Shakuni, 58: Chatushpada, 59: Naga
KARANA_60 = (
    ["Kinstughna"] +
    (["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"] * 8) +  # 1..56 (56 halves)
    ["Shakuni","Chatushpada","Naga"]
)

# =================== SIDEBAR ===================
st.sidebar.header("🌍 Location & Settings")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz_name = st.sidebar.text_input("Timezone (IANA, e.g. Asia/Kolkata)", value="Asia/Kolkata")
show_debug = st.sidebar.checkbox("Show debug panel", value=False)
# Tiny ayanamsa trim (degrees) if you need to match another source by a hair
ayanamsa_trim = st.sidebar.slider("Ayanamsa fine trim (°)", -0.05, 0.05, 0.0, 0.001)

# =================== LIVE CLOCK ===================
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

# =================== ASTRO HELPERS ===================
STEP_NAK = 360.0/27.0

def jd_to_local_dt(jd_ut: float):
    if jd_ut is None or (isinstance(jd_ut, float) and math.isnan(jd_ut)): return None
    y,m,d,ut = swe.revjul(jd_ut, swe.GREG_CAL)
    dt_utc = datetime(y,m,d, tzinfo=timezone.utc) + timedelta(hours=ut)
    return dt_utc.astimezone(tz)

def fmt_time(dt): return dt.strftime("%I:%M %p") if dt else "—"

def rise_set_one(jd0_ut, body, mode, lon, lat):
    try:
        ret, jdlist = swe.rise_trans(
            jd0_ut, body, mode | swe.BIT_DISC_CENTER, (lon, lat, 0.0), 1013.25, 15.0
        )
        if ret >= 0:
            return jdlist[0] if isinstance(jdlist, (list, tuple)) else jdlist
    except Exception:
        pass
    return None

def sun_moon_rise_set(local_date, lon, lat):
    swe.set_topo(lon, lat, 0.0)
    local_midnight = local_date.replace(hour=0,minute=0,second=0,microsecond=0)
    utc_midnight = local_midnight.astimezone(pytz.utc)
    jd0 = swe.julday(utc_midnight.year, utc_midnight.month, utc_midnight.day, 0.0)
    sr = rise_set_one(jd0, swe.SUN,  swe.CALC_RISE, lon, lat)  or rise_set_one(jd0+1, swe.SUN,  swe.CALC_RISE, lon, lat)
    ss = rise_set_one(jd0, swe.SUN,  swe.CALC_SET,  lon, lat)  or rise_set_one(jd0+1, swe.SUN,  swe.CALC_SET, lon, lat)
    mr = rise_set_one(jd0, swe.MOON, swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_RISE, lon, lat)
    ms = rise_set_one(jd0, swe.MOON, swe.CALC_SET,  lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_SET,  lon, lat)
    return jd_to_local_dt(sr), jd_to_local_dt(ss), jd_to_local_dt(mr), jd_to_local_dt(ms), sr

def sidereal_longitudes(jd_ut, lon, lat, trim_deg=0.0):
    # Lahiri sidereal; apply tiny user-trim if needed for parity
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    swe.set_topo(lon, lat, 0.0)
    FLG_TOPOCTR = getattr(swe, "FLG_TOPOCTR", 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | FLG_TOPOCTR
    sun, _  = swe.calc_ut(jd_ut, swe.SUN,  flags)
    moon, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    sun_lon  = (sun[0]  + trim_deg) % 360.0
    moon_lon = (moon[0] + trim_deg) % 360.0
    return sun_lon, moon_lon

def tithi_idx(sun_lon, moon_lon):  return int(((moon_lon - sun_lon) % 360.0) // 12.0)
def nak_idx(moon_lon):             return int((moon_lon % 360.0) // STEP_NAK)
def yoga_idx(sun_lon, moon_lon):   return int(((sun_lon + moon_lon) % 360.0) // STEP_NAK)
def karana_name(sun_lon, moon_lon):
    half = int(((moon_lon - sun_lon) % 360.0) // 6.0)  # 0..59
    return KARANA_60[half]

# ---- Find next transition time for a given index ----
def find_next_change(jd_start, lon, lat, kind, cur_idx, trim_deg=0.0, max_hours=48):
    def idx_at(jd):
        s, m = sidereal_longitudes(jd, lon, lat, trim_deg)
        if kind == "tithi": return tithi_idx(s, m)
        if kind == "nak":   return nak_idx(m)
        if kind == "yoga":  return yoga_idx(s, m)
        return None

    step = 0.25/24.0  # 15-minute coarse
    jd_prev = jd_start
    prev_idx = cur_idx
    for _ in range(int(max_hours/0.25)):
        jd_next = jd_prev + step
        nxt = idx_at(jd_next)
        if nxt is None: return None
        if nxt != prev_idx:
            # binary search to ~1 min
            lo, hi = jd_prev, jd_next
            for _ in range(30):
                mid = (lo + hi)/2.0
                im = idx_at(mid)
                if im == prev_idx: lo = mid
                else: hi = mid
            return hi
        jd_prev, prev_idx = jd_next, nxt
    return None

# =================== CORE ENGINE ===================
def panchang_for_date(local_date, lon, lat, trim_deg=0.0):
    sr_local, ss_local, mr_local, ms_local, sr_jd = sun_moon_rise_set(local_date, lon, lat)

    # Evaluate at "apparent" sunrise + 15 minutes to avoid boundary flutters
    eval_local = (sr_local or local_date.replace(hour=6, minute=0)) + timedelta(minutes=15)
    eval_utc = eval_local.astimezone(pytz.utc)
    jd_eval = swe.julday(eval_utc.year, eval_utc.month, eval_utc.day,
                         eval_utc.hour + eval_utc.minute/60 + eval_utc.second/3600)

    # Also evaluate BEFORE sunrise (for "roll forward if ended before sunrise" checks)
    pre_local = eval_local - timedelta(hours=2)
    pre_utc = pre_local.astimezone(pytz.utc)
    jd_pre = swe.julday(pre_utc.year, pre_utc.month, pre_utc.day,
                        pre_utc.hour + pre_utc.minute/60 + pre_utc.second/3600)

    # Sidereal longitudes
    s_eval, m_eval = sidereal_longitudes(jd_eval, lon, lat, trim_deg)
    s_pre,  m_pre  = sidereal_longitudes(jd_pre,  lon, lat, trim_deg)

    # Indices (evaluate at sunrise+15)
    ti = tithi_idx(s_eval, m_eval)
    ni = nak_idx(m_eval)
    yi = yoga_idx(s_eval, m_eval)

    # ---- Drik-like tithi rule: if tithi changed before sunrise, show current (post-sunrise) ----
    ti_pre = tithi_idx(s_pre, m_pre)
    if ti_pre != ti:
        # already rolled forward because tithi flipped before sunrise
        pass

    # Names
    tithi_name = TITHIS[ti]
    paksha = "Shukla" if ti < 15 else "Krishna"
    nak_name = NAKSHATRAS[ni]
    yoga_name = YOGAS[yi]
    karana = karana_name(s_eval, m_eval)

    # Ends-at times
    tithi_end_jd = find_next_change(jd_eval, lon, lat, "tithi", ti, trim_deg)
    nak_end_jd   = find_next_change(jd_eval, lon, lat, "nak",   ni, trim_deg)
    yoga_end_jd  = find_next_change(jd_eval, lon, lat, "yoga",  yi, trim_deg)

    return {
        "sunrise": sr_local, "sunset": ss_local, "moonrise": mr_local, "moonset": ms_local,
        "sun_long": s_eval, "moon_long": m_eval, "elong": (m_eval - s_eval) % 360.0,
        "tithi": tithi_name, "paksha": paksha, "nakshatra": nak_name, "yoga": yoga_name, "karana": karana,
        "tithi_ends": jd_to_local_dt(tithi_end_jd),
        "nak_ends": jd_to_local_dt(nak_end_jd),
        "yoga_ends": jd_to_local_dt(yoga_end_jd)
    }

# =================== RUN ===================
try:
    p = panchang_for_date(now_local, lon, lat, ayanamsa_trim)

    st.markdown('<div class="row">', unsafe_allow_html=True)

    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌅 Rise / Set")
    st.markdown(f"**Sunrise:** {fmt_time(p['sunrise'])} &nbsp;&nbsp; **Sunset:** {fmt_time(p['sunset'])}")
    st.markdown(f"**Moonrise:** {fmt_time(p['moonrise'])} &nbsp;&nbsp; **Moonset:** {fmt_time(p['moonset'])}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="col"><div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Panchang (Sunrise-based)")
    st.markdown(f"🌸 **Tithi:** {p['tithi']}  <span class='small'>(ends {fmt_time(p['tithi_ends'])})</span>", unsafe_allow_html=True)
    st.markdown(f"🌗 **Paksha:** {p['paksha']}")
    st.markdown(f"✨ **Nakshatra:** {p['nakshatra']}  <span class='small'>(ends {fmt_time(p['nak_ends'])})</span>", unsafe_allow_html=True)
    st.markdown(f"🪶 **Yoga:** {p['yoga']}  <span class='small'>(ends {fmt_time(p['yoga_ends'])})</span>", unsafe_allow_html=True)
    st.markdown(f"🌼 **Karana:** {p['karana']}")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div style='text-align:center'><button class='kbutton'>🪔 Generate Sankalpa</button></div>", unsafe_allow_html=True)

    if show_debug:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🧪 Debug")
        st.caption(f"☀️ Sun λ = {p['sun_long']:.6f}°  |  🌙 Moon λ = {p['moon_long']:.6f}°  |  Δ = {p['elong']:.6f}°")
        # raw indices
        raw_ti = TITHIS.index(p['tithi'])
        raw_ni = NAKSHATRAS.index(p['nakshatra'])
        raw_yi = YOGAS.index(p['yoga'])
        st.caption(f"indices → tithi={raw_ti}, nak={raw_ni}, yoga={raw_yi} | trim={ayanamsa_trim:+.3f}°")

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

# =================== FOOTER ===================
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — v8.0 Drik Emulation Mode (Swiss Ephemeris • Lahiri • Topocentric • Sunrise + 15m)
</div>
""", unsafe_allow_html=True)