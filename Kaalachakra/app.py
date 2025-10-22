import math
from datetime import datetime, timedelta, timezone
import pytz
import streamlit as st
import streamlit.components.v1 as components
import swisseph as swe

st.set_page_config(page_title="🕉️ Kaalachakra Live — v9.0 (Sankalpa)", page_icon="🕉️", layout="centered")

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
.kbox { background:#171717; border:1px solid #f1c40f22; border-radius:12px; padding:12px; }
.out { white-space:pre-wrap; background:#0b0b0b; border:1px dashed #f1c40f55; padding:14px; border-radius:12px; }
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
KARANA_60 = (["Kinstughna"] + ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]*8 + ["Shakuni","Chatushpada","Naga"])

# Devanagari names for Sankalpa
VARS_SANSKRIT = ["रविवासरे","सोमवासरे","मङ्गलवासरे","बुधवासरे","गुरुवासरे","शुक्रवासरे","शनिवासरे"]
TITHIS_SAN = [
    "शुक्ल प्रतिपदा","शुक्ल द्वितीया","शुक्ल तृतीया","शुक्ल चतुर्थी","शुक्ल पञ्चमी",
    "शुक्ल षष्ठी","शुक्ल सप्तमी","शुक्ल अष्टमी","शुक्ल नवमी","शुक्ल दशमी",
    "शुक्ल एकादशी","शुक्ल द्वादशी","शुक्ल त्रयोदशी","शुक्ल चतुर्दशी","पूर्णिमा",
    "कृष्ण प्रतिपदा","कृष्ण द्वितीया","कृष्ण तृतीया","कृष्ण चतुर्थी","कृष्ण पञ्चमी",
    "कृष्ण षष्ठी","कृष्ण सप्तमी","कृष्ण अष्टमी","कृष्ण नवमी","कृष्ण दशमी",
    "कृष्ण एकादशी","कृष्ण द्वादशी","कृष्ण त्रयोदशी","कृष्ण चतुर्दशी","अमावस्या"
]
NAK_SAN = [
    "अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशीर्षा","आर्द्रा","पुनर्वसु","पुष्य",
    "आश्लेषा","मघा","पूर्वफल्गुनी","उत्तरफल्गुनी","हस्त","चित्रा","स्वाती",
    "विशाखा","अनूराधा","ज्येष्ठा","मूला","पूर्वाषाढा","उत्तराषाढा",
    "श्रवण","धनिष्ठा","शतभिषा","पूर्वभाद्रपदा","उत्तरभाद्रपदा","रेवती"
]
YOGA_SAN = [
    "विश्कम्भ","प्रीति","आयुष्मान्","सौभाग्य","शोभन","अतिगण्ड","सुकर्मा","धृति",
    "शूल","गण्ड","वृद्धि","ध्रुव","व्याघात","हर्षण","वज्र","सिद्धि","व्यतीपात",
    "वरीयान्","परिघ","शिव","सिद्ध","साध्य","शुभ","शुक्ल","ब्रह्म","इन्द्र","वैधृति"
]
KAR_SAN = {
    "Kinstughna":"किंस्तुघ्न","Bava":"बव","Balava":"बालव","Kaulava":"कौलव","Taitila":"तैतिल",
    "Garaja":"गर","Vanija":"वणिज","Vishti":"भद्रा","Shakuni":"शकुनि","Chatushpada":"चतुष्पद","Naga":"नाग"
}

STEP_NAK = 360.0/27.0
EPS = 1e-9

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
    # Anti-lag: if the returned sunrise is yesterday, jump to today's sunrise
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
    i = int(math.floor(min(max(val - EPS, 0.0), max_exclusive - EPS)))
    return max(0, min(i, max_exclusive-1))

def tithi_index(s,m): return clamp_idx(((m - s) % 360.0) / 12.0, 30)
def nak_index(m):     return clamp_idx((m % 360.0) / STEP_NAK, 27)
def yoga_index(s,m):  return clamp_idx(((s + m) % 360.0) / STEP_NAK, 27)
def karana_name(s,m): return ["Kinstughna"] + ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]*8 + ["Shakuni","Chatushpada","Naga"][int(((m - s) % 360.0) // 6.0) : int(((m - s) % 360.0) // 6.0)+1] if False else KARANA_60[int(((m - s) % 360.0) // 6.0)]

def next_change(jd_start, lon, lat, kind, cur_idx, trim=0.0, max_hours=48):
    def idx_at(jd):
        s,m = sidereal_longs(jd, lon, lat, trim)
        if kind=="tithi": return tithi_index(s,m)
        if kind=="nak":   return nak_index(m)
        if kind=="yoga":  return yoga_index(s,m)
        return None
    step = 0.25/24.0
    lo = jd_start
    cur = cur_idx
    for _ in range(int(max_hours/0.25)):
        hi = lo + step
        nxt = idx_at(hi)
        if nxt != cur:
            for __ in range(30):
                mid = (lo + hi)/2.0
                if idx_at(mid) == cur: lo = mid
                else: hi = mid
            return hi
        lo, cur = hi, nxt
    return None

def compute_panchang(local_date, lon, lat, trim=0.0):
    sr_local, ss_local, mr_local, ms_local, sr_jd = sun_moon_rise_set(local_date, lon, lat)
    if not sr_jd:
        fb = local_date.replace(hour=6, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        sr_jd = swe.julday(fb.year, fb.month, fb.day, fb.hour + fb.minute/60.0)
    jd_eval = sr_jd + 15/1440.0
    jd_pre  = sr_jd - 2/24.0
    s_now, m_now = sidereal_longs(jd_eval, lon, lat, trim)
    s_pre, m_pre = sidereal_longs(jd_pre,  lon, lat, trim)
    ti = tithi_index(s_now, m_now)
    ni = nak_index(m_now)
    yi = yoga_index(s_now, m_now)
    tithi = TITHIS[ti]; paksha = "Shukla" if ti < 15 else "Krishna"
    nak = NAKSHATRAS[ni]; yoga = YOGAS[yi]
    karana = KARANA_60[int(((m_now - s_now) % 360.0) // 6.0)]
    te = next_change(jd_eval, lon, lat, "tithi", ti, trim)
    ne = next_change(jd_eval, lon, lat, "nak",   ni, trim)
    ye = next_change(jd_eval, lon, lat, "yoga",  yi, trim)
    return {
        "sunrise": sr_local, "sunset": ss_local, "moonrise": mr_local, "moonset": ms_local,
        "sun_long": s_now, "moon_long": m_now, "elong": (m_now - s_now) % 360.0,
        "tithi": tithi, "paksha": paksha, "nakshatra": nak, "yoga": yoga, "karana": karana,
        "tithi_ends": jd_to_local_dt(te), "nak_ends": jd_to_local_dt(ne), "yoga_ends": jd_to_local_dt(ye),
        "ti_idx":ti, "nak_idx":ni, "yoga_idx":yi
    }

# ---------- RUN CORE ----------
P = None
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

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

# ====================== SANKALPA MODULE ======================
def devanagari_digits(s):
    dmap = str.maketrans("0123456789", "०१२३४५६७८९")
    return str(s).translate(dmap)

def weekday_sanskrit(dt):
    return VARS_SANSKRIT[dt.weekday()]  # Mon=0

def english_to_sanskrit_names(p):
    t_san = TITHIS_SAN[P["ti_idx"]]
    n_san = NAK_SAN[P["nak_idx"]]
    y_san = YOGA_SAN[P["yoga_idx"]]
    k_san = KAR_SAN.get(P["karana"], P["karana"])
    paksha_san = "शुक्ल" if P["paksha"]=="Shukla" else "कृष्ण"
    return t_san, paksha_san, n_san, y_san, k_san

def build_sankalpa(p, name, gotra, place, purpose, offering, when_dt):
    t_san, paksha_san, n_san, y_san, k_san = english_to_sanskrit_names(p)
    vara = weekday_sanskrit(when_dt)
    date_str = devanagari_digits(when_dt.strftime("%d-%m-%Y"))
    time_str = devanagari_digits(when_dt.strftime("%I:%M %p"))
    lines = [
        "ॐ विष्णुर्विष्णुर्विष्णुः ॥",
        "श्रीभगवतो महापुरुषस्य विष्णोराज्ञया प्रवर्तमाने कर्मणि।",
        f"अद्य {date_str} तिथौ, {vara},",
        f"{paksha_san}पक्षे {t_san} तथा {n_san} नक्षत्रे, {y_san} योगे, {k_san} करणेषु,",
        f"{place} नाम्नि स्थाने, {time_str} समये।",
        f"अहं {gotra}–गोत्रोत्पन्नः/उत्पन्ना {name} नाम।",
        f"{purpose} हेतोः, {offering} इति समर्पयामि।",
        "इति संकल्पः ॥"
    ]
    return "\n".join(lines)

def sankalpa_html(sank_text, p, name):
    style = """
    <style>
    body{font-family:'Noto Sans Devanagari','Hind','Mukta','Noto Sans',system-ui; padding:24px; background:#111; color:#f5f3e7;}
    h1{color:#f4d03f; text-align:center;}
    .box{border:1px solid #f1c40f55; border-radius:12px; padding:18px; background:#151515;}
    pre{white-space:pre-wrap; font-size:18px; line-height:1.7;}
    .meta{margin-top:10px; font-size:14px; opacity:0.85;}
    </style>
    """
    meta = f"तिथि: {p['tithi']} | नक्षत्र: {p['nakshatra']} | योग: {p['yoga']} | करण: {p['karana']}"
    body = f"<h1>🪔 संकल्पपत्रम्</h1><div class='box'><pre>{sank_text}</pre><div class='meta'>{meta}</div></div>"
    return ("<html><head><meta charset='UTF-8'>" + style + "</head><body>" + body + "</body></html>").encode("utf-8")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center'>🪔 Generate Sankalpa</h3>", unsafe_allow_html=True)

with st.expander("Open Sankalpa Form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name (e.g., Amlan Mishra)", value="")
        gotra = st.text_input("Gotra (e.g., भारद्वाज)", value="")
        place = st.text_input("Place/City (Devanagari or English)", value="नॊएडा / Noida")
    with col2:
        purpose = st.text_area("Why are you taking the Sankalpa? (Devanagari or English)",
                               height=80, value="समस्त दुःख–कष्ट–विघ्न–नाशनार्थे")
        offering = st.text_area("What will you offer / do? (Devanagari or English)",
                                height=80, value="११ पाठाः, नैवेद्यम् च समर्पयामि")

    # ✅ Streamlit Cloud compatible (no st.datetime_input)
    date_sel = st.date_input("Sankalpa Date", value=now_local.date())
    time_sel = st.time_input("Sankalpa Time", value=now_local.time().replace(microsecond=0))
    when_dt = tz.localize(datetime.combine(date_sel, time_sel))

    gen = st.button("✨ Generate", use_container_width=True)

if gen and P:
    text = build_sankalpa(P, name.strip() or "—", gotra.strip() or "—",
                          place.strip() or "—", purpose.strip() or "—",
                          offering.strip() or "—", when_dt)
    st.success("✅ Sankalpa generated below. Review and download.")
    st.markdown(f"<div class='out'>{text}</div>", unsafe_allow_html=True)

    html_bytes = sankalpa_html(text, P, name or "sankalpa")
    st.download_button("⬇️ Download Sankalpa (HTML → Print to PDF)",
                       data=html_bytes, file_name="sankalpa.html", mime="text/html")

# ---------- DEBUG ----------
if show_debug and P:
    st.markdown("<hr><h3>🧪 Debug</h3>", unsafe_allow_html=True)
    st.caption(f"☀️ Sun λ = {P['sun_long']:.6f}°  |  🌙 Moon λ = {P['moon_long']:.6f}°  |  Δ = {P['elong']:.6f}°  |  trim = {ayan_trim:+.3f}°")
# ====================== GRAND SANKALPA MODULE (v10.1) ======================
from utils.sankalpa_engine import generate_sankalpa

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>📜 Grand Traditional Sankalpa</h3>", unsafe_allow_html=True)

with st.expander("Open Grand Sankalpa Form (Full Sanskrit Style)"):
    c1, c2 = st.columns(2)
    with c1:
        name_full = st.text_input("Full Name (IAST or English)", "Amlan Mishra")
        gotra_full = st.text_input("Gotra (IAST or Sanskrit)", "Bhāradvāja")
        gender = st.selectbox("Gender", ["Male", "Female"])
    with c2:
        country = st.text_input("Country", "Bhāratavarṣe")
        state = st.text_input("State/Region", "Odisha")
        city = st.text_input("City/Place", "Bhubaneswar")

    purpose2 = st.text_area("Purpose — Why are you taking the Sankalpa?",
                            "to remove all obstacles and ensure divine protection")
    offering2 = st.text_area("Offering — What will you do or offer?",
                             "21 recitations of Kālabhairavāṣṭakam and 11 Siddha Kunjikā Stotram")

    date_sel2 = st.date_input("Sankalpa Date (Traditional)", value=now_local.date())
    time_sel2 = st.time_input("Sankalpa Time", value=now_local.time().replace(microsecond=0))
    when_dt2 = tz.localize(datetime.combine(date_sel2, time_sel2))

    gen2 = st.button("🔥 Generate Grand Sankalpa", use_container_width=True)

if gen2 and P:
    try:
        # Fetch graha data
        jd_eval = swe.julday(when_dt2.year, when_dt2.month, when_dt2.day,
                             when_dt2.hour + when_dt2.minute / 60.0)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        sun, _ = swe.calc_ut(jd_eval, swe.SUN, flags)
        moon, _ = swe.calc_ut(jd_eval, swe.MOON, flags)
        jup, _ = swe.calc_ut(jd_eval, swe.JUPITER, flags)

        text2 = generate_sankalpa(
            country=country, state=state, city=city,
            paksha_iast=P["paksha"], tithi_iast=P["tithi"],
            weekday_dt=when_dt2, nakshatra_iast=P["nakshatra"],
            yoga_iast=P["yoga"], karana_iast=P["karana"],
            lunar_month_iast="Kartika",  # TODO: compute dynamically
            sun_lon_sidereal=sun[0], moon_lon_sidereal=moon[0], jupiter_lon_sidereal=jup[0],
            name_iast=name_full, gotra_iast=gotra_full,
            purpose_free=purpose2, offering_free=offering2,
            gender=gender, when_dt=when_dt2
        )

        st.success("✅ Grand Sankalpa generated below.")
        st.markdown(f"<div class='out'>{text2}</div>", unsafe_allow_html=True)

        html_bytes2 = text2.encode("utf-8")
        st.download_button("⬇️ Download Grand Sankalpa (UTF-8 Text)",
                           data=html_bytes2, file_name="grand_sankalpa.txt", mime="text/plain")

    except Exception as e:
        st.error(f"🚫 Error generating Grand Sankalpa: {e}")
# ---------- FOOTER ----------
st.markdown("<div class='footer'>🕯️ <span>ॐ नमः शिवाय</span> — v9.0 Sankalpa • Swiss Ephemeris • Drik-style</div>", unsafe_allow_html=True)