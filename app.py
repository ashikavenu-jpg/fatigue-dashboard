import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("full_fatigue_dataset.csv")

data = load_data()

X = data[['Glucose', 'Hb', 'Hydration']]
y = data['Fatigue']

model = RandomForestClassifier()
model.fit(X, y)

# ---------------- HEADER ----------------
st.markdown("""
    <h1 style='text-align: center;'>🏃 AI Fatigue Monitoring Dashboard</h1>
    <p style='text-align: center;'>Real-time Athlete Health Monitoring System</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Control Panel")

start = st.sidebar.button("▶ Start Monitoring")
stop = st.sidebar.button("⏹ Stop Monitoring")

if "run" not in st.session_state:
    st.session_state.run = False

if start:
    st.session_state.run = True
if stop:
    st.session_state.run = False

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- MAIN LAYOUT ----------------
col_main, col_side = st.columns([3, 1])

# ---------------- LIVE DATA ----------------
with col_main:

    st.subheader("📡 Live Monitoring")

    placeholder = st.empty()

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

            # Metric Cards
            m1, m2, m3 = st.columns(3)
            m1.metric("Glucose", glucose)
            m2.metric("Hb", hb)
            m3.metric("Hydration", hydration)

            st.markdown("---")

            # Fatigue Status
            st.subheader("⚡ Fatigue Status")

            if prediction == "High":
                st.error("⚠ HIGH FATIGUE")
            elif prediction == "Medium":
                st.warning("⚠ MEDIUM FATIGUE")
            else:
                st.success("✅ LOW FATIGUE")

            # Recommendation
            st.subheader("🧠 Recommendation")

            if prediction == "High":
                st.write("• Immediate rest required")
                st.write("• Drink electrolyte fluids")
                st.write("• Avoid physical activity")

            elif prediction == "Medium":
                st.write("• Take short rest")
                st.write("• Drink water")

            else:
                st.write("• Continue normal activity")

        time.sleep(2)

# ---------------- SIDE PANEL ----------------
with col_side:

    st.subheader("⚠ Risk Alerts")

    if len(st.session_state.history) > 0:
        last = st.session_state.history[-1]

        if last["Hydration"] < 55:
            st.warning("💧 Dehydration Risk")

        if last["Hb"] < 11:
            st.warning("🩸 Low Hemoglobin")

        if last["Glucose"] > 170:
            st.warning("🍬 High Glucose")

    st.markdown("---")

    st.subheader("📊 Quick Stats")

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        avg = df[['Glucose', 'Hb', 'Hydration']].mean()

        st.write({
            "Glucose Avg": round(avg['Glucose'], 2),
            "Hb Avg": round(avg['Hb'], 2),
            "Hydration Avg": round(avg['Hydration'], 2)
        })

# ---------------- ANALYTICS ----------------
st.markdown("---")
st.subheader("📊 Analytics")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)

    c1, c2 = st.columns(2)

    with c1:
        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

    with c2:
        st.bar_chart(df['Fatigue'].value_counts())

# ---------------- HISTORY ----------------
st.markdown("---")
st.subheader("📁 History Data")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Download Data", csv, "fatigue_data.csv", "text/csv")
else:
    st.info("No data available")

