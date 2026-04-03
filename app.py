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

# ---------------- DATA FUNCTION ----------------
def generate_data():

    glucose = random.randint(120, 180)
    hb = random.randint(10, 16)
    hydration = random.randint(50, 70)

    prediction = model.predict([[glucose, hb, hydration]])[0]

    # CDSS Recommendation logic
    if prediction == "High":
        cdss = "Immediate rest + monitoring"
    elif prediction == "Medium":
        cdss = "Reduce activity + hydration"
    else:
        cdss = "Normal condition"

    st.session_state.history.append({
        "Time": st.session_state.time_sec,
        "Glucose": glucose,
        "Hb": hb,
        "Hydration": hydration,
        "Fatigue": prediction,
        "CDSS": cdss
    })

    st.session_state.time_sec += 2


# =========================================================
# 🔷 PAGE 1: LIVE MONITORING
# =========================================================
if page == "Live Monitoring":

    st.title("Fatigue Monitoring System")

    col1, col2 = st.columns(2)
    if col1.button("Start Monitoring"):
        st.session_state.run = True

    if col2.button("Stop Monitoring"):
        st.session_state.run = False

    # Default values
    glucose = 0
    hb = 0
    hydration = 0
    fatigue = "Not Started"

    # RUN LOGIC
    if st.session_state.run:

        glucose = random.randint(120, 180)
        hb = random.randint(10, 16)
        hydration = random.randint(50, 70)

        fatigue = model.predict([[glucose, hb, hydration]])[0]

        st.session_state.history.append({
            "Time": st.session_state.time_sec,
            "Glucose": glucose,
            "Hb": hb,
            "Hydration": hydration,
            "Fatigue": fatigue
        })

        st.session_state.time_sec += 2

        # auto refresh every 2 sec
        time.sleep(2)
        st.rerun()

    # DISPLAY VALUES ALWAYS
    c1, c2, c3 = st.columns(3)
    c1.metric("Glucose", glucose)
    c2.metric("Hemoglobin", hb)
    c3.metric("Hydration", hydration)

    st.subheader("Fatigue Level")

    if fatigue == "High":
        st.error("HIGH FATIGUE")
    elif fatigue == "Medium":
        st.warning("MEDIUM FATIGUE")
    elif fatigue == "Low":
        st.success("LOW FATIGUE")
    else:
        st.info("Click Start Monitoring")

    # GRAPH
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df.set_index("Time")[['Glucose', 'Hb', 'Hydration']])

    # ALWAYS SHOW PLACEHOLDER VALUES
    glucose = 0
    hb = 0
    hydration = 0
    fatigue = "Not Started"

    if st.session_state.run:
        glucose = random.randint(120, 180)
        hb = random.randint(10, 16)
        hydration = random.randint(50, 70)

        fatigue = model.predict([[glucose, hb, hydration]])[0]

        st.session_state.history.append({
            "Time": st.session_state.time_sec,
            "Glucose": glucose,
            "Hb": hb,
            "Hydration": hydration,
            "Fatigue": fatigue
        })

        st.session_state.time_sec += 2

        time.sleep(2)
        st.rerun()

    # ALWAYS SHOW VALUES
    c1, c2, c3 = st.columns(3)
    c1.metric("Glucose", glucose)
    c2.metric("Hemoglobin", hb)
    c3.metric("Hydration", hydration)

    st.subheader("Fatigue Level")

    if fatigue == "High":
        st.error("HIGH FATIGUE")
    elif fatigue == "Medium":
        st.warning("MEDIUM FATIGUE")
    elif fatigue == "Low":
        st.success("LOW FATIGUE")
    else:
        st.info("Click Start Monitoring")

    # GRAPH
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df.set_index("Time")[['Glucose', 'Hb', 'Hydration']])

    # -------- CONTINUOUS UPDATE --------
    if st.session_state.run:
        generate_data()
        time.sleep(2)
        st.rerun()

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

    st.title("CDSS Recommendation")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)
        last = df.iloc[-1]

        st.subheader("Latest Recommendation")
        st.write(last["CDSS"])

    else:
        st.info("Run monitoring first")


# =========================================================
# 🔷 PAGE 3: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":

    st.title("Graph Analysis")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.subheader("Trend (Time vs Parameters)")
        st.line_chart(df.set_index("Time")[['Glucose', 'Hb', 'Hydration']])

        st.subheader("Fatigue Distribution")
        st.bar_chart(df['Fatigue'].value_counts())

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

