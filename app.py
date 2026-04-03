import streamlit as st
import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# ---------------- AUTO REFRESH (2 sec) ----------------
count = st_autorefresh(interval=2000, limit=None, key="refresh")

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
if "history" not in st.session_state:
    st.session_state.history = []

# =========================================================
# 🔷 DATA GENERATION (EVERY REFRESH)
# =========================================================
def generate_data():
    glucose = random.randint(120, 180)
    hb = random.randint(10, 16)
    hydration = random.randint(50, 70)

    prediction = model.predict([[glucose, hb, hydration]])[0]

    st.session_state.history.append({
        "Time": len(st.session_state.history) * 2,
        "Glucose": glucose,
        "Hb": hb,
        "Hydration": hydration,
        "Fatigue": prediction
    })

# Only generate when on Live page
if page == "Live Monitoring":
    generate_data()

# =========================================================
# 🔷 PAGE 1: LIVE MONITORING
# =========================================================
if page == "Live Monitoring":

    st.title("Fatigue Monitoring System")

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

        # -------- VALUES --------
        st.subheader("Latest Patient Values")

        c1, c2, c3 = st.columns(3)
        c1.metric("Glucose", int(glucose))
        c2.metric("Hemoglobin", int(hb))
        c3.metric("Hydration", int(hydration))

        st.divider()

        # -------- RISK INTERPRETATION --------
        st.subheader("Risk Interpretation")

        if prediction == "High":
            st.error("Severe fatigue condition → High risk of performance decline and health complications")

        elif prediction == "Medium":
            st.warning("Moderate fatigue → Reduced efficiency and potential dehydration risk")

        else:
            st.success("Normal physiological condition → Stable performance")

        # Additional interpretation
        if hb < 11:
            st.warning("Low hemoglobin → Reduced oxygen carrying capacity")

        if hydration < 55:
            st.warning("Low hydration → Risk of dehydration and fatigue")

        if glucose > 170:
            st.warning("High glucose → Possible metabolic imbalance")

        if hb < 11 and hydration < 55:
            st.error("Combined oxygen + hydration deficiency → High fatigue risk")

        st.divider()

        # -------- CDSS RECOMMENDATION --------
        st.subheader("CDSS Recommendation")

        if prediction == "High":
            st.error("Immediate rest required\nProvide fluids and continuous monitoring")

        elif prediction == "Medium":
            st.warning("Reduce activity level\nIncrease hydration")

        else:
            st.success("Continue normal activity")

        # -------- 7 CONDITIONS --------
        st.subheader("Critical Conditions")

        if hydration < 55:
            st.warning("1. Dehydration risk")

        if hb < 11:
            st.warning("2. Low hemoglobin risk")

        if glucose > 170:
            st.warning("3. High glucose level")

        if hb < 11 and hydration < 55:
            st.error("4. Combined oxygen + hydration risk")

        if glucose > 170 and hydration < 55:
            st.error("5. Metabolic + dehydration risk")

        if prediction == "High" and hb < 11:
            st.error("6. Severe fatigue with low Hb")

        if prediction == "High" and hydration < 55:
            st.error("7. Severe fatigue with dehydration")

    else:
        st.info("Run Live Monitoring first")

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

# =========================================================
# 🔷 PAGE 3: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":

    st.title("Graph Analysis")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.subheader("Trend vs Time (seconds)")
        st.line_chart(df.set_index("Time")[['Glucose', 'Hb', 'Hydration']])

        st.bar_chart(df['Fatigue'].value_counts())

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

