import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Patient Monitor", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("full_fatigue_dataset.csv")

data = load_data()

X = data[['Glucose', 'Hb', 'Hydration']]
y = data['Fatigue']

model = RandomForestClassifier()
model.fit(X, y)

# ---------------- DARK STYLE ----------------
st.markdown("""
    <style>
    body {background-color: #0e1117;}
    .big-font {font-size:40px !important; font-weight:bold;}
    .medium-font {font-size:20px !important;}
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;color:#00FFAA;'>🏥 PATIENT MONITOR SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- CONTROL ----------------
col_btn1, col_btn2 = st.columns(2)
start = col_btn1.button("▶ START")
stop = col_btn2.button("⏹ STOP")

if "run" not in st.session_state:
    st.session_state.run = False

if start:
    st.session_state.run = True
if stop:
    st.session_state.run = False

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- PLACEHOLDER ----------------
placeholder = st.empty()

# ---------------- LIVE LOOP ----------------
while st.session_state.run:

    glucose = random.randint(120, 180)
    hb = random.randint(10, 16)
    hydration = random.randint(50, 70)

    prediction = model.predict([[glucose, hb, hydration]])[0]

    st.session_state.history.append({
        "Glucose": glucose,
        "Hb": hb,
        "Hydration": hydration,
        "Fatigue": prediction
    })

    df = pd.DataFrame(st.session_state.history)

    with placeholder.container():

        # ---------------- VITAL SIGNS ----------------
        st.markdown("### 🩺 VITAL SIGNS")

        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<p class='big-font' style='color:#00FF00;'>Glucose<br>{glucose}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p class='big-font' style='color:#00FF00;'>Hb<br>{hb}</p>", unsafe_allow_html=True)
        c3.markdown(f"<p class='big-font' style='color:#00FF00;'>Hydration<br>{hydration}</p>", unsafe_allow_html=True)

        st.markdown("---")

        # ---------------- FATIGUE STATUS ----------------
        st.markdown("### ⚠ PATIENT STATUS")

        if prediction == "High":
            st.markdown("<h2 style='color:red;'>CRITICAL CONDITION</h2>", unsafe_allow_html=True)
        elif prediction == "Medium":
            st.markdown("<h2 style='color:orange;'>MODERATE CONDITION</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color:green;'>STABLE CONDITION</h2>", unsafe_allow_html=True)

        # ---------------- CDSS ----------------
        st.markdown("### 🧠 CLINICAL DECISION SUPPORT")

        if prediction == "High":
            st.error("Immediate medical attention required!")
        elif prediction == "Medium":
            st.warning("Patient needs rest and hydration")
        else:
            st.success("Patient condition normal")

        # ---------------- LIVE GRAPH ----------------
        st.markdown("### 📊 LIVE MONITOR")

        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

    time.sleep(2)

