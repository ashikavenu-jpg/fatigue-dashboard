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
st.title("Fatigue Monitoring System")
st.caption("AI-Based Real-Time Monitoring with CDSS Support")

st.divider()

# ---------------- CONTROL ----------------
col1, col2 = st.columns(2)
start = col1.button("Start Monitoring")
stop = col2.button("Stop Monitoring")

if "run" not in st.session_state:
    st.session_state.run = False

if start:
    st.session_state.run = True
if stop:
    st.session_state.run = False

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

placeholder = st.empty()

# ---------------- MAIN LOOP ----------------
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

        # -------- VITALS --------
        st.subheader("Vitals")

        c1, c2, c3 = st.columns(3)
        c1.metric("Glucose", glucose)
        c2.metric("Hemoglobin (Hb)", hb)
        c3.metric("Hydration", hydration)

        st.divider()

        # -------- FATIGUE LEVEL --------
        st.subheader("Fatigue Level")

        if prediction == "High":
            st.error("HIGH FATIGUE")
        elif prediction == "Medium":
            st.warning("MEDIUM FATIGUE")
        else:
            st.success("LOW FATIGUE")

        st.divider()

        # -------- CDSS (7 CONDITIONS) --------
        st.subheader("Clinical Decision Support System (CDSS)")

        # 1. High fatigue critical
        if prediction == "High":
            st.error("1. Critical fatigue condition – Immediate rest required")

        # 2. Medium fatigue
        if prediction == "Medium":
            st.warning("2. Moderate fatigue – Reduce activity and hydrate")

        # 3. Low fatigue
        if prediction == "Low":
            st.success("3. Normal condition – Continue activity")

        # 4. Low hydration
        if hydration < 55:
            st.warning("4. Dehydration risk detected")

        # 5. Low Hb
        if hb < 11:
            st.warning("5. Low hemoglobin level detected")

        # 6. High glucose
        if glucose > 170:
            st.warning("6. Elevated glucose level detected")

        # 7. Combined risk
        if (hydration < 55 and hb < 11) or (prediction == "High" and glucose > 170):
            st.error("7. Combined risk – Medical attention recommended")

        st.divider()

        # -------- RECOMMENDATION --------
        st.subheader("Recommendation")

        if prediction == "High":
            st.write("• Immediate rest")
            st.write("• Hydration with electrolytes")
            st.write("• Monitor continuously")

        elif prediction == "Medium":
            st.write("• Take short rest")
            st.write("• Drink fluids")

        else:
            st.write("• Maintain routine activity")

        st.divider()

        # -------- GRAPH --------
        st.subheader("Trend Monitoring")

        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

    time.sleep(2)

# ---------------- HISTORY ----------------
st.divider()
st.subheader("History Data")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
else:
    st.info("No data available")

