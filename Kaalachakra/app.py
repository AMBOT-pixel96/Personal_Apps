import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import swisseph as swe

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🕉️ Kaalchakra Live (Manual Mode)", page_icon="🕉️", layout="centered")

# -------------- CUSTOM STYLE ------------------
st.markdown("""
<style>
body { background-color:#0d0d0d; color:#f5f3e7; font-family:'Open Sans',sans-serif; }
h1,h2,h3 { color:#f4d03f; text-align:center; text-shadow:0 0 10px #f7dc6f,0 0 20px #f1c40f;
            font-family:'Cinzel Decorative',cursive; }
.css-18e3th9 { background-color:#1a1a1a!important; border:1px solid #f1c40f; border-radius:15px; padding:1rem; }
hr { border:1px solid #f4d03f; box-shadow:0 0 5px #f4d03f; }
.footer { text-align:center; margin-top:40px; font-size:0.9rem; color:#aaa; }
.footer span { color:#f1c40f; }
</style>
""", unsafe_allow_html=True)

# ------------------- TITLE -------------------
st.markdown("""
<h1>🕉️ Kaalchakra Live</h1>
<h3>Manual Panchang — No API | Pure Celestial Calculation</h3>
""", unsafe_allow_html=True)

# ------------------- INPUTS -------------------
st.sidebar.header("🌍 Location & Timezone")
lat = st.sidebar.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.2090, format="%.6f")
tz = st.sidebar.text_input("Timezone (e.g. Asia/Kolkata)", value="Asia/Kolkata")

# ------------------- LIVE CLOCK -------------------
clock_html = f"""
<div style="text-align:center; margin-top:10px;">
  <h2 id="clock" style="color:#f4d03f;text-shadow:0px 0px 8px #f1c40f;
      font-family:'Courier New', monospace;font-size:1.5rem;">
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

# ------------------- AUTO REFRESH -------------------
st_autorefresh(interval=60000, key="kaalachakra_refresh")

# ------------------- TIME -------------------
now = datetime.now(pytz.timezone(tz))
st.markdown(f"### 🕒 {now.strftime('%A, %d %B %Y | %I:%M %p')}")

# ------------------- PANCHANG CALCULATION -------------------
try:
    # Step 1: Julian Day
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)

    # Step 2: Get Sun and Moon longitude (extract only first element)
    sun_long = swe.calc_ut(jd, swe.SUN)[0]
    moon_long = swe.calc_ut(jd, swe.MOON)[0]

    # Step 3: Tithi
    tithi_num = int(((moon_long - sun_long) % 360) / 12) + 1
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"

    # Step 4: Nakshatra
    nakshatra_index = int((moon_long % 360) / (360 / 27))
    nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
                  "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
                  "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
                  "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    nakshatra = nakshatras[nakshatra_index]

    # Step 5: Yoga
    yoga_index = int(((sun_long + moon_long) % 360) / (360 / 27))
    yogas = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
             "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
             "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    yoga = yogas[yoga_index]

    # Step 6: Karana
    karana_index = int((((moon_long - sun_long) % 360) / 6) % 60)
    karanas = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"] * 9
    karana = karanas[karana_index]

    # Step 7: Vaar (weekday)
    vaar = now.strftime("%A")

    # ------------------- DISPLAY -------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("## 🔮 **Panchang Details (Calculated)**")
    st.markdown(f"🌗 **Paksha:** {paksha}")
    st.markdown(f"🌸 **Tithi:** {tithi_num} / 30")
    st.markdown(f"✨ **Nakshatra:** {nakshatra}")
    st.markdown(f"🪶 **Yoga:** {yoga}")
    st.markdown(f"🌼 **Karana:** {karana}")
    st.markdown(f"📿 **Vaar (Day):** {vaar}")
    st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚫 Calculation Error: {e}")

# ------------------- FOOTER -------------------
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)