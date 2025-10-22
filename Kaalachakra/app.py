import math
from datetime import datetime, timedelta, timezone
import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe

st.set_page_config(page_title="🕉️ Kaalachakra Live — v8.2 (Anti-Lag)", page_icon="🕉️", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
body { background:#0d0d0d; color:#f5f3e7; font-family:system-ui,-apple-system,Segoe UI,Roboto,'Open Sans',sans-serif; }
h1,h2,h3 { color:#f4d03f; text-align:center; text-shadow:0 0 10px #f7dc6f, 0 0 20px #f1c40f; font-family:'Cinzel Decorative',cursive; }
hr { border:1px solid #f4d03f; box-shadow:0 0 5px #f4d03f; }
.card { background:#141414; border:1px solid #f1c40f33; border-radius:14px; padding:14px; margin:10px 0; }
.small { opacity:0.9; font-size:0.95rem; }
.btn { background:#f4d03f; color:#000; font-weight:700; padding:10px 18px; border:none; border-radius:10px; box-shadow:0 0 10px #f4d03f66; }
.footer { text-align:center; margin-top:28px; font-size:0.9rem; color:#aaa; }
.footer span { color:#f1c40f; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🕉️ Kaalachakra Live</h1><h3>Drik-style • Sunrise-based • Lahiri Sidereal • Topocentric</h3>", unsafe_allow_html=True)

# ---------- TABLES ----------
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
# Full 60 half-karana sequence
KARANA_60 = (["Kinstughna"] + ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]*8 + ["Shakuni","Chatushpada","Naga"])

STEP_NAK = 360.0/27.0
EPS = 1e-9  # clamp for floating edge cases

# ---------- SIDEBAR ----------
st.sidebar.header("🌍 Location & Settings")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz_name = st.sidebar.text_input("Timezone (IANA)", value="Asia/Kolkata")
ayan_trim = st.sidebar.slider("Ayanamsa fine trim (°)", -0.05, 0.05, 0.000, 0.001)
show_debug = st.sidebar.checkbox("Show debug panel", value=False)

tz = pytz.timezone(tz_name)
now_local = datetime.now(tz)

# ---------- CLOCK ----------
components.html(f"""
<div style="text-align:center; margin-top:10px;">
  <h2 id="clock" style="color:#f4d03f;text-shadow:0 0 8px #f1c40f;font-family:'Courier New',monospace;font-size:1.5rem;"></h2>
</div>
<script>
function updateClock(){{
  const tz="{tz_name}";
  const now=new Date().toLocaleString("en-US",{{timeZone:tz}});
  const d=new Date(now);
  const opts={{weekday:'long',year:'numeric',month:'long',day:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'}};
  document.getElementById('clock').innerHTML=d.toLocaleString('en-IN',opts);
}}
setInterval(updateClock,1000); updateClock();
</script>
""", height=65)
st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')} — {tz_name}")

# ---------- HELPERS ----------
def jd_to_local_dt(jd_ut):
    if jd_ut is None or (isinstance(jd_ut,float) and math.isnan(jd_ut)): return None
    y,m,d,ut = swe.revjul(jd_ut, swe.GREG_CAL)
    return (datetime(y,m,d,tzinfo=timezone.utc)+timedelta(hours=ut)).astimezone(tz)

def fmt(dt): return dt.strftime("%I:%M %p") if dt else "—"

def rise_set_one(jd0_ut, body, mode, lon, lat):
    try:
        ret, jdlist = swe.rise_trans(jd0_ut, body, mode|swe.BIT_DISC_CENTER, (lon,lat,0.0), 1013.25, 15.0)
        if ret >= 0:
            return jdlist[0] if isinstance(jdlist,(list,tuple)) else jdlist
    except Exception:
        pass
    return None

def sun_moon_rise_set(local_date, lon, lat):
    swe.set_topo(lon, lat, 0.0)
    local_mid = local_date.replace(hour=0,minute=0,second=0,microsecond=0)
    utc_mid = local_mid.astimezone(pytz.utc)
    jd0 = swe.julday(utc_mid.year, utc_mid.month, utc_mid.day, 0.0)
    sr = rise_set_one(jd0, swe.SUN, swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.SUN, swe.CALC_RISE, lon, lat)
    ss = rise_set_one(jd0, swe.SUN, swe.CALC_SET, lon, lat) or rise_set_one(jd0+1, swe.SUN, swe.CALC_SET, lon, lat)
    mr = rise_set_one(jd0, swe.MOON, swe.CALC_RISE, lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_RISE, lon, lat)
    ms = rise_set_one(jd0, swe.MOON, swe.CALC_SET, lon, lat) or rise_set_one(jd0+1, swe.MOON, swe.CALC_SET, lon, lat)

    sr_local = jd_to_local_dt(sr)
    # 🔧 Anti-lag: if this sunrise is from yesterday, bump to next day
    if sr_local and sr_local.date() < now_local.date():
        sr += 1.0
        sr_local = sr_local + timedelta(days=1)

    return sr_local, jd_to_local_dt(ss), jd_to_local_dt(mr), jd_to_local_dt(ms), sr

def sidereal_longs(jd_ut, lon, lat, trim=0.0):
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    swe.set_topo(lon, lat, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | getattr(swe,"FLG_TOPOCTR",0)
    s,_ = swe.calc_ut(jd_ut, swe.SUN,  flags)
    m,_ = swe.calc_ut(jd_ut, swe.MOON, flags)
    return (s[0]+trim)%360.0, (m[0]+trim)%360.0

def clamp_idx(val, max_exclusive):
    # safe floor with epsilon and clamp in [0, max_exclusive-1]
    i = int(math.floor(min(max(val - EPS, 0.0), max_exclusive - EPS)))
    return max(0, min(i, max_exclusive-1))

def tithi_index(s,m):
    return clamp_idx(((m - s) % 360.0) / 12.0, 30)  # 0..29
def nak_index(m):
    return clamp_idx((m % 360.0) / STEP_NAK, 27)     # 0..26
def yoga_index(s,m):
    return clamp_idx(((s + m) % 360.0) / STEP_NAK, 27)  # 0..26
def karana_name(s,m):
    k = clamp_idx(((m - s) % 360.0) / 6.0, 60)       # 0..59
    return KARANA_60[k]

def next_change(jd_start, lon, lat, kind, cur_idx, trim=0.0, max_hours=48):
    def idx_at(jd):
        s,m = sidereal_longs(jd, lon, lat, trim)
        if kind=="tithi": return tithi_index(s,m)
        if kind=="nak":   return nak_index(m)
        if kind=="yoga":  return yoga_index(s,m)
        return None

    step = 0.25/24.0  # 15-min coarse
    lo = jd_start
    cur = cur_idx
    for _ in range(int(max_hours/0.25)):
        hi = lo + step
        nxt = idx_at(hi)
        if nxt != cur:
            # binary search to ~1 min
            for __ in range(30):
                mid = (lo + hi) / 2.0
                if idx_at(mid) == cur: lo = mid
                else: hi = mid
            return hi
        lo, cur = hi, nxt
    return None

def compute_panchang(local_date, lon, lat, trim=0.0):
    sr_local, ss_local, mr_local, ms_local, sr_jd = sun_moon_rise_set(local_date, lon, lat)

    if not sr_jd:
        # fallback: 6:00 local
        fb = local_date.replace(hour=6, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        sr_jd = swe.julday(fb.year, fb.month, fb.day, fb.hour + fb.minute/60.0)

    jd_eval = sr_jd + 15/1440.0     # sunrise + 15 min
    jd_pre  = sr_jd - 2/24.0        # 2h before sunrise (for roll-forward idea if needed)

    s_now, m_now = sidereal_longs(jd_eval, lon, lat, trim)
    s_pre, m_pre = sidereal_longs(jd_pre,  lon, lat, trim)

    ti = tithi_index(s_now, m_now)
    ni = nak_index(m_now)
    yi = yoga_index(s_now, m_now)

    # (If tithi before sunrise differs, we already show post-sunrise value)

    tithi = TITHIS[ti]
    paksha = "Shukla" if ti < 15 else "Krishna"
    nak = NAKSHATRAS[ni]
    yoga = YOGAS[yi]
    karana = karana_name(s_now, m_now)

    te = next_change(jd_eval, lon, lat, "tithi", ti, trim)
    ne = next_change(jd_eval, lon, lat, "nak",   ni, trim)
    ye = next_change(jd_eval, lon, lat, "yoga",  yi, trim)

    return {
        "sunrise": sr_local, "sunset": ss_local, "moonrise": mr_local, "moonset": ms_local,
        "sun_long": s_now, "moon_long": m_now, "elong": (m_now - s_now) % 360.0,
        "tithi": tithi, "paksha": paksha, "nakshatra": nak, "yoga": yoga, "karana": karana,
        "tithi_ends": jd_to_local_dt(te), "nak_ends": jd_to_local_dt(ne), "yoga_ends": jd_to_local_dt(ye)
    }

# ---------- RUN ----------
try:
    P = compute_panchang(now_local, lon, lat, ayan_trim)

    st.markdown("<div class='card'><h3>🌅 Rise / Set</h3>" +
                f"<b>Sunrise:</b> {fmt(P['sunrise'])} &nbsp;&nbsp; <b>Sunset:</b> {fmt(P['sunset'])}<br/>" +
                f"<b>Moonrise:</b> {fmt(P['moonrise'])} &nbsp;&nbsp; <b>Moonset:</b> {fmt(P['moonset'])}</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><h3>🔮 Panchang (Sunrise-based)</h3>" +
                f"🌸 <b>Tithi:</b> {P['tithi']} <span class='small'>(ends {fmt(P['tithi_ends'])})</span><br/>" +
                f"🌗 <b>Paksha:</b> {P['paksha']}<br/>" +
                f"✨ <b>Nakshatra:</b> {P['nakshatra']} <span class='small'>(ends {fmt(P['nak_ends'])})</span><br/>" +
                f"🪶 <b>Yoga:</b> {P['yoga']} <span class='small'>(ends {fmt(P['yoga_ends'])})</span><br/>" +
                f"🌼 <b>Karana:</b> {P['karana']}</div>", unsafe_allow_html=True)

    if show_debug:
        st.markdown("<hr><h3>🧪 Debug</h3>", unsafe_allow_html=True)
        st.caption(f"☀️ Sun λ = {P['sun_long']:.6f}°  |  🌙 Moon λ = {P['moon_long']:.6f}°  |  Δ = {P['elong']:.6f}°  |  trim = {ayan_trim:+.3f}°")

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

st.markdown("<div class='footer'>🕯️ <span>ॐ नमः शिवाय</span> — v8.2 Anti-Lag (Swiss • Lahiri • Topocentric)</div>", unsafe_allow_html=True)