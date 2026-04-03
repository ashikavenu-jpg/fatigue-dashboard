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

    # 🔁 AUTO UPDATE
    if st.session_state.run:
        time.sleep(2)
        st.rerun()

    # Generate values
    glucose = random.randint(120, 180)
    hb = random.randint(10, 16)
    hydration = random.randint(50, 70)

    prediction = model.predict([[glucose, hb, hydration]])[0]

    # Save
    st.session_state.history.append({
        "Glucose": glucose,
        "Hb": hb,
        "Hydration": hydration,
        "Fatigue": prediction
    })

    df = pd.DataFrame(st.session_state.history)

    # UI
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
# 🔷 PAGE 2: CDSS RECOMMENDATION
# =========================================================
elif page == "CDSS Recommendation":

    st.title("Clinical Decision Support System")

    if len(st.session_state.history) > 0:

        last = st.session_state.history[-1]

        glucose = last["Glucose"]
        hb = last["Hb"]
        hydration = last["Hydration"]
        prediction = last["Fatigue"]

        st.subheader("Latest Patient Condition")

        c1, c2, c3 = st.columns(3)
        c1.metric("Glucose", glucose)
        c2.metric("Hemoglobin", hb)
        c3.metric("Hydration", hydration)

        st.divider()

        st.subheader("CDSS Recommendation")

        # Main decision
        if prediction == "High":
            st.error("Critical fatigue → Immediate rest & monitoring")

        elif prediction == "Medium":
            st.warning("Moderate fatigue → Reduce activity & hydrate")

        else:
            st.success("Normal → Continue routine")

        st.divider()

        # 7 CDSS CONDITIONS
        st.subheader("Risk Conditions")

        if hydration < 55:
            st.warning("1. Dehydration risk")

        if hb < 11:
            st.warning("2. Low hemoglobin")

        if glucose > 170:
            st.warning("3. High glucose level")

        if hb < 11 and hydration < 55:
            st.error("4. Combined oxygen + hydration risk")

        if glucose > 170 and hydration < 55:
            st.error("5. Metabolic + dehydration risk")

        if prediction == "High" and hb < 11:
            st.error("6. Severe fatigue + low Hb risk")

        if prediction == "High" and hydration < 55:
            st.error("7. Severe fatigue + dehydration risk")

    else:
        st.info("Run Live Monitoring first")

# =========================================================
# 🔷 PAGE 3: GRAPH ANALYSIS
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

