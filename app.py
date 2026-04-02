import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Fatigue Monitoring", layout="wide")

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
st.markdown("<h1 style='text-align: center;'>🏃 AI Fatigue Monitoring System</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Control Panel")

start = st.sidebar.button("▶ Start")
stop = st.sidebar.button("⏹ Stop")

if "run" not in st.session_state:
    st.session_state.run = False

if start:
    st.session_state.run = True
if stop:
    st.session_state.run = False

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📡 Live Monitor", "📊 Analytics", "📁 History"])

# ---------------- LIVE MONITOR ----------------
with tab1:

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

            st.subheader("📡 Live Sensor Data")

            col1, col2, col3 = st.columns(3)
            col1.metric("Glucose", glucose)
            col2.metric("Hb", hb)
            col3.metric("Hydration", hydration)

            st.markdown("---")

            st.subheader("⚡ Fatigue Status")

            if prediction == "High":
                st.error("⚠ HIGH FATIGUE")
            elif prediction == "Medium":
                st.warning("⚠ MEDIUM FATIGUE")
            else:
                st.success("✅ LOW FATIGUE")

            st.markdown("### 🧠 Recommendation")

            if prediction == "High":
                st.write("• Immediate rest required")
                st.write("• Drink electrolyte fluids")
                st.write("• Avoid physical activity")

            elif prediction == "Medium":
                st.write("• Take short rest")
                st.write("• Drink water")
                st.write("• Reduce activity")

            else:
                st.write("• Continue normal activity")
                st.write("• Stay hydrated")

            # Alerts
            st.markdown("---")
            st.subheader("⚠ Risk Alerts")

            if hydration < 55:
                st.warning("💧 Dehydration Risk")
            if hb < 11:
                st.warning("🩸 Low Hemoglobin")
            if glucose > 170:
                st.warning("🍬 High Glucose")

        time.sleep(2)

# ---------------- ANALYTICS ----------------
with tab2:

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        st.subheader("📊 Trends")
        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

        st.subheader("📉 Fatigue Distribution")
        st.bar_chart(df['Fatigue'].value_counts())

        st.subheader("📌 Summary")
        st.write(df.describe())

    else:
        st.info("No data yet. Start monitoring.")

# ---------------- HISTORY ----------------
with tab3:

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        st.subheader("📁 Recorded Data")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Data", csv, "fatigue_data.csv", "text/csv")

    else:
        st.info("No history available.")

