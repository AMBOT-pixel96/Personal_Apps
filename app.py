import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="🕉️ Shiva Vaas Calculator", page_icon="🕉️", layout="centered")

# --- Inject Custom CSS ---
st.markdown("""
<style>
body {
    background-color: #0d0d0d;
    color: #f5f3e7;
    font-family: 'Open Sans', sans-serif;
}

h1, h2, h3 {
    color: #f4d03f;
    text-align: center;
    text-shadow: 0px 0px 10px #f7dc6f, 0px 0px 20px #f1c40f;
    font-family: 'Cinzel Decorative', cursive;
}

.css-18e3th9 {
    background-color: #1a1a1a !important;
    border: 1px solid #f1c40f;
    border-radius: 15px;
    padding: 1rem;
}

.stSelectbox label {
    color: #f7dc6f !important;
    font-weight: bold;
}

div[data-testid="stMarkdownContainer"] p {
    color: #f5f3e7 !important;
}

hr {
    border: 1px solid #f4d03f;
    box-shadow: 0px 0px 5px #f4d03f;
}

.footer {
    text-align: center;
    margin-top: 40px;
    font-size: 0.9rem;
    color: #aaa;
}

.footer span {
    color: #f1c40f;
}
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""
<h1>🕉️ Shiva Vaas Calculator</h1>
<h3>Discover where Lord Shiva resides today based on Paksha & Tithi</h3>
""", unsafe_allow_html=True)

# --- User Inputs ---
paksha = st.selectbox("Select Paksha:", ["Shukla Paksha", "Krishna Paksha"])
tithi = st.selectbox("Select Tithi (1 = Prathama, 15 = Purnima/Amavasya):", list(range(1, 16)))

# --- Data ---
shukla_data = {
    1: ("शमशान", "मृत्युतुल्य"),
    2: ("गौरी सानिध्य", "सुखप्रद"),
    3: ("सभायां", "संताप"),
    4: ("क्रीडायां", "कष्ट एवं दुःख"),
    5: ("कैलाश पर", "सुखप्रद"),
    6: ("वृषारूढ", "अभीष्टसिद्धि"),
    7: ("भोजन", "पीड़ा"),
    8: ("शमशान", "मृत्युतुल्य"),
    9: ("गौरी सानिध्य", "सुखप्रद"),
    10: ("सभायां", "संताप"),
    11: ("क्रीडायां", "कष्ट एवं दुःख"),
    12: ("कैलाश पर", "सुखप्रद"),
    13: ("वृषारूढ", "अभीष्टसिद्धि"),
    14: ("भोजन", "पीड़ा"),
    15: ("शमशान", "मृत्युतुल्य")
}

krishna_data = {
    1: ("गौरी सानिध्य", "सुखप्रद"),
    2: ("सभायां", "संताप"),
    3: ("क्रीडायां", "कष्ट एवं दुःख"),
    4: ("कैलाश पर", "सुखप्रद"),
    5: ("वृषारूढ", "अभीष्टसिद्धि"),
    6: ("भोजन", "पीड़ा"),
    7: ("शमशान", "मृत्युतुल्य"),
    8: ("गौरी सानिध्य", "सुखप्रद"),
    9: ("सभायां", "संताप"),
    10: ("क्रीडायां", "कष्ट एवं दुःख"),
    11: ("कैलाश पर", "सुखप्रद"),
    12: ("वृषारूढ", "अभीष्टसिद्धि"),
    13: ("भोजन", "पीड़ा"),
    14: ("शमशान", "मृत्युतुल्य"),
    15: ("गौरी सानिध्य", "सुखप्रद")
}

# --- Shiva Vaas → Image mapping ---
image_map = {
    "शमशान": "images/smasan.jpg",
    "गौरी सानिध्य": "images/gauri.jpg",
    "सभायां": "images/sabha.jpg",  # your chosen temple / mandapam / hall image
    "क्रीडायां": "images/kreeda.jpg",
    "कैलाश पर": "images/kailash.jpg",
    "वृषारूढ": "images/vrisharudh.jpg",
    "भोजन": "images/bhojan.jpg"
}

# --- Fetch Results ---
if paksha == "Shukla Paksha":
    vaas, phal = shukla_data[tithi]
else:
    vaas, phal = krishna_data[tithi]

# --- Display Results ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"<h2>🔱 शिववास: {vaas}</h2>", unsafe_allow_html=True)
st.markdown(f"<h3>🌸 फल: {phal}</h3>", unsafe_allow_html=True)

# --- Display corresponding image ---
if vaas in image_map:
    st.image(image_map[vaas], use_container_width=True, caption=f"🔮 {vaas} — Divine Presence")

st.markdown("<hr>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
🕯️ <span>ॐ नमः शिवाय</span> — Crafted with devotion by Amlan Mishra 🕉️
</div>
""", unsafe_allow_html=True)