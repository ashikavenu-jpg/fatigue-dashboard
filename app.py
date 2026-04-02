import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Fatigue System", layout="wide")

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
st.title("🏃 AI-Based Live Fatigue Monitoring System")

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
tab1, tab2, tab3 = st.tabs(["📡 Live Monitoring", "📊 Analytics", "📁 History"])

# ---------------- LIVE MONITORING ----------------
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

            # KPI Cards
            c1, c2, c3 = st.columns(3)
            c1.metric("Glucose", glucose)
            c2.metric("Hb", hb)
            c3.metric("Hydration", hydration)

            st.subheader("⚡ Fatigue Status")

            if prediction == "High":
                st.error("⚠ HIGH FATIGUE 🔔")
                st.audio("https://www.soundjay.com/buttons/beep-07.mp3")
            elif prediction == "Medium":
                st.warning("⚠ MEDIUM FATIGUE")
            else:
                st.success("✅ LOW FATIGUE")

        time.sleep(2)

# ---------------- ANALYTICS ----------------
with tab2:

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        st.subheader("📊 Live Trend Graph")
        st.line_chart(df[['Glucose','Hb','Hydration']])

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

        st.dataframe(df)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Data", csv, "fatigue_data.csv", "text/csv")

    else:
        st.info("No history available.")
