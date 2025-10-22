import streamlit as st

st.set_page_config(page_title="Shiva Vaas Calculator 🕉️", page_icon="🕉️", layout="centered")

st.markdown("""
# 🕉️ Shiva Vaas Finder
### Discover where Lord Shiva resides today, based on Paksha & Tithi.
""")

# --- User Inputs ---
paksha = st.selectbox("Select Paksha:", ["Shukla Paksha", "Krishna Paksha"])
tithi = st.selectbox("Select Tithi (1 = Prathama, 15 = Purnima/Amavasya):", list(range(1, 16)))

# --- Data Logic ---
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
    15: ("गौरी सानिध्य", "सुखप्रद")  # Amavasya
}

# --- Fetch result ---
if paksha == "Shukla Paksha":
    vaas, phal = shukla_data[tithi]
else:
    vaas, phal = krishna_data[tithi]

# --- Display Output ---
st.divider()
st.markdown(f"## 🔱 Shiva Vaas Today: **{vaas}**")
st.markdown(f"### 🌸 Phal: *{phal}*")

# --- Bonus aesthetic ---
st.markdown("""
---
🕉️ *May Lord Shiva bless you with strength, peace, and absolute badassery.*
""")