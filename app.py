import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Patient Monitoring System", layout="wide")

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
st.title("Patient Monitoring System")
st.caption("Real-time Fatigue Monitoring with Decision Support")

st.divider()

# ---------------- CONTROL ----------------
col1, col2, col3 = st.columns([1,1,6])

start = col1.button("Start")
stop = col2.button("Stop")

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

# ---------------- MAIN ----------------
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

        # -------- SECTION 1: VITALS --------
        st.subheader("Vitals")

        v1, v2, v3 = st.columns(3)
        v1.metric("Glucose", glucose)
        v2.metric("Hemoglobin", hb)
        v3.metric("Hydration", hydration)

        st.divider()

        # -------- SECTION 2: STATUS --------
        st.subheader("Patient Status")

        if prediction == "High":
            st.error("High Fatigue")
        elif prediction == "Medium":
            st.warning("Medium Fatigue")
        else:
            st.success("Low Fatigue")

        st.divider()

        # -------- SECTION 3: RECOMMENDATION --------
        st.subheader("Clinical Recommendation")

        if prediction == "High":
            st.write("Patient requires immediate rest and monitoring.")
        elif prediction == "Medium":
            st.write("Advise hydration and short rest.")
        else:
            st.write("Patient condition stable.")

        st.divider()

        # -------- SECTION 4: ALERTS --------
        st.subheader("Alerts")

        if hydration < 55:
            st.warning("Low hydration level")
        if hb < 11:
            st.warning("Low hemoglobin level")
        if glucose > 170:
            st.warning("High glucose level")

        st.divider()

        # -------- SECTION 5: GRAPH --------
        st.subheader("Trend")

        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

    time.sleep(2)

# ---------------- HISTORY TABLE ----------------
st.divider()
st.subheader("Patient Data History")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
else:
    st.info("No data available")

