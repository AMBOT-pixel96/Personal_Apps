import math
from datetime import datetime, timedelta, timezone
import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe

st.set_page_config(page_title="🕉️ Kaalachakra Live — v8.2 (Anti-Lag Build)", page_icon="🕉️", layout="centered")

# ---------- BASIC STYLE ----------
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

st.markdown("<h1>🕉️ Kaalachakra Live</h1><h3>Drik-Style • Anti-Lag • Lahiri Sidereal</h3>", unsafe_allow_html=True)

# ---------- CONSTANTS ----------
STEP_NAK = 360.0/27.0
TITHIS = [...]
NAKSHATRAS = [...]
YOGAS = [...]
KARANA_60 = (["Kinstughna"] + ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]*8 + ["Shakuni","Chatushpada","Naga"])

# ---------- SIDEBAR ----------
st.sidebar.header("🌍 Location & Settings")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz_name = st.sidebar.text_input("Timezone", value="Asia/Kolkata")
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
st.markdown(f"### 🕒 {now_local.strftime('%A, %d %B %Y | %I:%M %p')} — {tz_name}", unsafe_allow_html=True)

# ---------- HELPER FUNCS ----------
def jd_to_local_dt(jd_ut):
    if not jd_ut: return None
    y,m,d,ut = swe.revjul(jd_ut, swe.GREG_CAL)
    return (datetime(y,m,d,tzinfo=timezone.utc)+timedelta(hours=ut)).astimezone(tz)
def fmt(dt): return dt.strftime("%I:%M %p") if dt else "—"

def rise_set(jd0, body, mode, lon, lat):
    try:
        ret,jdlist = swe.rise_trans(jd0, body, mode|swe.BIT_DISC_CENTER,(lon,lat,0.0),1013.25,15.0)
        if ret>=0: return jdlist[0] if isinstance(jdlist,(list,tuple)) else jdlist
    except: return None

def sun_moon_rise_set(local_date, lon, lat):
    swe.set_topo(lon, lat, 0.0)
    utc_mid = local_date.replace(hour=0,minute=0,second=0).astimezone(pytz.utc)
    jd0 = swe.julday(utc_mid.year,utc_mid.month,utc_mid.day,0.0)
    sr = rise_set(jd0,swe.SUN,swe.CALC_RISE,lon,lat)
    if not sr: sr = rise_set(jd0+1,swe.SUN,swe.CALC_RISE,lon,lat)
    # Anti-lag patch ↓↓↓
    sr_local = jd_to_local_dt(sr)
    if sr_local and sr_local.date() < now_local.date():
        sr += 1.0
        sr_local += timedelta(days=1)
    ss = rise_set(jd0,swe.SUN,swe.CALC_SET,lon,lat)
    mr = rise_set(jd0,swe.MOON,swe.CALC_RISE,lon,lat)
    ms = rise_set(jd0,swe.MOON,swe.CALC_SET,lon,lat)
    return sr_local,jd_to_local_dt(ss),jd_to_local_dt(mr),jd_to_local_dt(ms),sr

def sidereal_longs(jd,lon,lat,trim):
    swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
    swe.set_topo(lon,lat,0.0)
    flags=swe.FLG_SWIEPH|swe.FLG_SIDEREAL|getattr(swe,"FLG_TOPOCTR",0)
    s,_=swe.calc_ut(jd,swe.SUN,flags); m,_=swe.calc_ut(jd,swe.MOON,flags)
    return (s[0]+trim)%360.0,(m[0]+trim)%360.0

def tithi_idx(s,m):return int(((m-s)%360)//12)
def nak_idx(m):return int((m%360)//STEP_NAK)
def yoga_idx(s,m):return int(((s+m)%360)//STEP_NAK)
def karana_name(s,m):return KARANA_60[int(((m-s)%360)//6)]

def next_change(jd,lon,lat,kind,idx,trim):
    def cur(j): s,m=sidereal_longs(j,lon,lat,trim)
    step=0.25/24; lo=jd
    for _ in range(200):
        hi=lo+step
        s,m=sidereal_longs(hi,lon,lat,trim)
        ni=tithi_idx(s,m) if kind=="tithi" else nak_idx(m) if kind=="nak" else yoga_idx(s,m)
        if ni!=idx:
            for __ in range(30):
                mid=(lo+hi)/2; s,m=sidereal_longs(mid,lon,lat,trim)
                ni=tithi_idx(s,m) if kind=="tithi" else nak_idx(m) if kind=="nak" else yoga_idx(s,m)
                (lo,hi)=(mid,hi) if ni==idx else (lo,mid)
            return hi
        lo=hi
    return None

# ---------- MAIN ----------
try:
    sr,ss,mr,ms,sr_jd = sun_moon_rise_set(now_local,lon,lat)
    jd_eval = sr_jd + 15/1440
    s,m = sidereal_longs(jd_eval,lon,lat,ayan_trim)
    ti,ni,yi = tithi_idx(s,m),nak_idx(m),yoga_idx(s,m)
    paksha="Shukla" if ti<15 else "Krishna"
    t,n,y = TITHIS[ti],NAKSHATRAS[ni],YOGAS[yi]
    k = karana_name(s,m)
    te,ne,ye = next_change(jd_eval,lon,lat,"tithi",ti,ayan_trim),next_change(jd_eval,lon,lat,"nak",ni,ayan_trim),next_change(jd_eval,lon,lat,"yoga",yi,ayan_trim)

    st.markdown(f"<div class='card'><h3>🔮 Panchang (Sunrise-based)</h3>"
                f"🌸 <b>Tithi:</b> {t} <span class='small'>(ends {fmt(jd_to_local_dt(te))})</span><br/>"
                f"🌗 <b>Paksha:</b> {paksha}<br/>"
                f"✨ <b>Nakshatra:</b> {n} <span class='small'>(ends {fmt(jd_to_local_dt(ne))})</span><br/>"
                f"🪶 <b>Yoga:</b> {y} <span class='small'>(ends {fmt(jd_to_local_dt(ye))})</span><br/>"
                f"🌼 <b>Karana:</b> {k}</div>", unsafe_allow_html=True)

    if show_debug:
        st.caption(f"☀️Sunλ={s:.6f}° 🌙Moonλ={m:.6f}° Δ={(m-s)%360:.6f}° | trim={ayan_trim:+.3f}°")

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

st.markdown("<div class='footer'>🕯️ <span>ॐ नमः शिवाय</span> — v8.2 Anti-Lag Drik Emulation</div>", unsafe_allow_html=True)