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
    st.subheader("Live Monitoring with CDSS")

    col1, col2 = st.columns(2)
    start = col1.button("Start Monitoring")
    stop = col2.button("Stop Monitoring")

    if start:
        st.session_state.run = True
    if stop:
        st.session_state.run = False

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

            # -------- VITALS --------
            st.subheader("Vitals")

            c1, c2, c3 = st.columns(3)
            c1.metric("Glucose", glucose)
            c2.metric("Hemoglobin", hb)
            c3.metric("Hydration", hydration)

            st.divider()

            # -------- FATIGUE --------
            st.subheader("Fatigue Level")

            if prediction == "High":
                st.error("HIGH FATIGUE")
            elif prediction == "Medium":
                st.warning("MEDIUM FATIGUE")
            else:
                st.success("LOW FATIGUE")

            st.divider()

            # -------- CDSS --------
            st.subheader("CDSS Recommendation")

            if prediction == "High":
                st.error("Immediate rest required")
            elif prediction == "Medium":
                st.warning("Reduce activity and hydrate")
            else:
                st.success("Normal condition")

            # 7 Conditions
            if hydration < 55:
                st.warning("Dehydration risk")
            if hb < 11:
                st.warning("Low hemoglobin")
            if glucose > 170:
                st.warning("High glucose")
            if (hydration < 55 and hb < 11):
                st.error("Combined risk detected")

        time.sleep(2)

# =========================================================
# 🔷 PAGE 2: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":

    st.title("Graph Analysis")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.subheader("Trend Graph")
        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])

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
        st.info("No data available. Run monitoring first.")

# =========================================================
# 🔷 PAGE 3: RECORDED DATA
# =========================================================
elif page == "Recorded Data":

    st.title("Recorded Patient Data")

    if len(st.session_state.history) > 0:

        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df)

        # DOWNLOAD
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "Download Data",
            data=csv,
            file_name="fatigue_data.csv",
            mime="text/csv"
        )

    else:
        st.info("No recorded data available.")

