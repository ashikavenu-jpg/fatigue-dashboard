import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Fatigue Monitoring System", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("full_fatigue_dataset.csv")

data = load_data()

X = data[['Glucose', 'Hb', 'Hydration']]
y = data['Fatigue']

model = RandomForestClassifier()
model.fit(X, y)

# ---------------- TITLE ----------------
st.title("🏃 AI-Based Live Fatigue Monitoring System with CDSS")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙ Controls")

start = st.sidebar.button("▶ Start Monitoring")
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
tab1, tab2, tab3 = st.tabs(["📡 Live", "📊 Analytics", "📁 History"])

# ---------------- LIVE MONITORING ----------------
with tab1:

    placeholder = st.empty()

    while st.session_state.run:

        # Simulated sensor values
        glucose = random.randint(120, 180)
        hb = random.randint(10, 16)
        hydration = random.randint(50, 70)

        prediction = model.predict([[glucose, hb, hydration]])[0]

        # Save history
        st.session_state.history.append({
            "Glucose": glucose,
            "Hb": hb,
            "Hydration": hydration,
            "Fatigue": prediction
        })

        df = pd.DataFrame(st.session_state.history)

        with placeholder.container():

            # KPI CARDS
            c1, c2, c3 = st.columns(3)
            c1.metric("Glucose", glucose)
            c2.metric("Hb", hb)
            c3.metric("Hydration", hydration)

            st.subheader("⚡ Fatigue Status & CDSS")

            # CDSS LOGIC
            if prediction == "High":
                st.error("⚠ HIGH FATIGUE - CRITICAL")
                st.write("### 🧠 Recommendation")
                st.write("- Immediate rest")
                st.write("- Drink electrolyte fluids")
                st.write("- Avoid physical activity")
                st.write("- Monitor condition")

            elif prediction == "Medium":
                st.warning("⚠ MEDIUM FATIGUE")
                st.write("### 🧠 Recommendation")
                st.write("- Take short rest")
                st.write("- Hydrate properly")
                st.write("- Reduce activity")

            else:
                st.success("✅ LOW FATIGUE")
                st.write("### 🧠 Recommendation")
                st.write("- Continue activity")
                st.write("- Maintain hydration")

            # EXTRA ALERTS
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

        st.subheader("📊 Live Trends")
        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

        st.subheader("📉 Fatigue Distribution")
        st.bar_chart(df['Fatigue'].value_counts())

        st.subheader("📌 Statistical Summary")
        st.write(df.describe())

    else:
        st.info("No data yet. Start monitoring.")

# ---------------- HISTORY ----------------
with tab3:

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df)

        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Data", csv, "fatigue_data.csv", "text/csv")

    else:
        st.info("No history available.")
