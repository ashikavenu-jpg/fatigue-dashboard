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
page = st.sidebar.radio("Go to", ["Live Monitoring", "Graph Analysis", "Recorded Data"])

# ---------------- SESSION ----------------
if "run" not in st.session_state:
    st.session_state.run = False

if "history" not in st.session_state:
    st.session_state.history = []

# =========================================================
# 🔷 PAGE 1: LIVE MONITORING
# =========================================================
if page == "Live Monitoring":

    st.title("Fatigue Monitoring System")

    col1, col2 = st.columns(2)
    start = col1.button("Start Monitoring")
    stop = col2.button("Stop Monitoring")

    if start:
        st.session_state.run = True
    if stop:
        st.session_state.run = False

    # 🔥 AUTO REFRESH EVERY 2 SEC (IMPORTANT FIX)
    if st.session_state.run:
        time.sleep(2)
        st.rerun()

    # -------- GENERATE DATA --------
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

    # -------- LAYOUT --------
    left, right = st.columns([1, 2])

    # 🔴 LEFT → CDSS
    with left:
        st.subheader("CDSS Recommendation")

        if prediction == "High":
            st.error("Immediate rest required\nHydration + monitoring")

        elif prediction == "Medium":
            st.warning("Reduce activity\nIncrease fluids")

        else:
            st.success("Normal condition\nContinue activity")

        # Additional rules
        if hydration < 55:
            st.warning("Low hydration detected")

        if hb < 11:
            st.warning("Low hemoglobin")

        if glucose > 170:
            st.warning("High glucose level")

        if (hydration < 55 and hb < 11):
            st.error("Combined risk → Medical attention needed")

    # 🟢 RIGHT → MONITOR
    with right:
        st.subheader("Live Monitoring")

        c1, c2, c3 = st.columns(3)
        c1.metric("Glucose", glucose)
        c2.metric("Hemoglobin", hb)
        c3.metric("Hydration", hydration)

        st.divider()

        st.subheader("Fatigue Level")

        if prediction == "High":
            st.error("HIGH FATIGUE")
        elif prediction == "Medium":
            st.warning("MEDIUM FATIGUE")
        else:
            st.success("LOW FATIGUE")

        st.divider()

        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

# =========================================================
# 🔷 PAGE 2: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":

    st.title("Graph Analysis")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])
        st.bar_chart(df['Fatigue'].value_counts())

        avg = df[['Glucose', 'Hb', 'Hydration']].mean()

        st.write({
            "Average Glucose": round(avg['Glucose'], 2),
            "Average Hb": round(avg['Hb'], 2),
            "Average Hydration": round(avg['Hydration'], 2)
        })

    else:
        st.info("Run Live Monitoring first")

# =========================================================
# 🔷 PAGE 3: RECORDED DATA
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

