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

# ---------------- NAVIGATION ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Live Monitoring",
    "CDSS Recommendation",
    "Graph Analysis",
    "Recorded Data"
])

# ---------------- SESSION ----------------
if "run" not in st.session_state:
    st.session_state.run = False

if "history" not in st.session_state:
    st.session_state.history = []

if "time_sec" not in st.session_state:
    st.session_state.time_sec = 0

# ---------------- AUTO UPDATE ----------------
if st.session_state.run:
    time.sleep(2)
    st.session_state.time_sec += 2
    st.rerun()

# ---------------- GENERATE DATA ----------------
def generate_data():
    glucose = random.randint(120, 180)
    hb = random.randint(10, 16)
    hydration = random.randint(50, 70)

    prediction = model.predict([[glucose, hb, hydration]])[0]

    st.session_state.history.append({
        "Time": st.session_state.time_sec,
        "Glucose": glucose,
        "Hb": hb,
        "Hydration": hydration,
        "Fatigue": prediction
    })

# =========================================================
# 🔷 PAGE 1: LIVE MONITORING
# =========================================================
if page == "Live Monitoring":

    st.title("Fatigue Monitoring System")
    st.subheader("Live Monitoring")

    col1, col2 = st.columns(2)
    start = col1.button("Start Monitoring")
    stop = col2.button("Stop Monitoring")

    if start:
        st.session_state.run = True
    if stop:
        st.session_state.run = False

    # Generate new data when running
    if st.session_state.run:
        generate_data()

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        last = df.iloc[-1]

        c1, c2, c3 = st.columns(3)
        c1.metric("Glucose", int(last["Glucose"]))
        c2.metric("Hemoglobin", int(last["Hb"]))
        c3.metric("Hydration", int(last["Hydration"]))

        st.divider()

        st.subheader("Fatigue Level")

        if last["Fatigue"] == "High":
            st.error("HIGH FATIGUE")
        elif last["Fatigue"] == "Medium":
            st.warning("MEDIUM FATIGUE")
        else:
            st.success("LOW FATIGUE")

        st.divider()

        st.line_chart(df.set_index("Time")[['Glucose', 'Hb', 'Hydration']])

    else:
        st.info("Click Start Monitoring")

# =========================================================
# 🔷 PAGE 2: CDSS
# =========================================================
elif page == "CDSS Recommendation":

    st.title("Clinical Decision Support System")

    if len(st.session_state.history) > 0:

        last = pd.DataFrame(st.session_state.history).iloc[-1]

        glucose = last["Glucose"]
        hb = last["Hb"]
        hydration = last["Hydration"]
        prediction = last["Fatigue"]

        st.subheader("Latest Values")

        c1, c2, c3 = st.columns(3)
        c1.metric("Glucose", int(glucose))
        c2.metric("Hemoglobin", int(hb))
        c3.metric("Hydration", int(hydration))

        st.divider()

        st.subheader("CDSS Recommendation")

        if prediction == "High":
            st.error("Immediate rest + monitoring")

        elif prediction == "Medium":
            st.warning("Reduce activity + hydration")

        else:
            st.success("Normal condition")

        st.divider()

        # 7 CONDITIONS
        if hydration < 55:
            st.warning("Dehydration risk")
        if hb < 11:
            st.warning("Low Hb risk")
        if glucose > 170:
            st.warning("High glucose")
        if hb < 11 and hydration < 55:
            st.error("Combined risk")
        if glucose > 170 and hydration < 55:
            st.error("Metabolic risk")
        if prediction == "High" and hb < 11:
            st.error("Severe fatigue + Hb")
        if prediction == "High" and hydration < 55:
            st.error("Severe fatigue + hydration")

    else:
        st.info("Run monitoring first")

# =========================================================
# 🔷 PAGE 3: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":

    st.title("Graph Analysis")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.subheader("Trend vs Time (seconds)")
        st.line_chart(df.set_index("Time")[['Glucose', 'Hb', 'Hydration']])

        st.subheader("Fatigue Distribution")
        st.bar_chart(df['Fatigue'].value_counts())

        st.subheader("Summary")

        avg = df[['Glucose', 'Hb', 'Hydration']].mean()

        st.write({
            "Average Glucose": round(avg['Glucose'], 2),
            "Average Hb": round(avg['Hb'], 2),
            "Average Hydration": round(avg['Hydration'], 2)
        })

    else:
        st.info("Run monitoring first")

# =========================================================
# 🔷 PAGE 4: RECORDED DATA
# =========================================================
elif page == "Recorded Data":

    st.title("Recorded Data")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "Download Data",
            data=csv,
            file_name="fatigue_data.csv",
            mime="text/csv"
        )

    else:
        st.info("No data available")

