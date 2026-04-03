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

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "latest" not in st.session_state:
    st.session_state.latest = {}

if "run" not in st.session_state:
    st.session_state.run = False

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Live Monitoring",
    "CDSS Output",
    "Interpretation",
    "Graph Analysis",
    "Recorded Data"
])

# =========================================================
# 🔷 PAGE 1: LIVE MONITORING
# =========================================================
if page == "Live Monitoring":

    st.title("Fatigue Monitoring System")

    col1, col2 = st.columns(2)
    start = col1.button("Start")
    stop = col2.button("Stop")

    if start:
        st.session_state.run = True
    if stop:
        st.session_state.run = False

    placeholder = st.empty()

    while st.session_state.run:

        glucose = random.randint(80, 200)
        hb = random.randint(9, 16)
        hydration = random.randint(45, 75)

        prediction = model.predict([[glucose, hb, hydration]])[0]

        st.session_state.latest = {
            "Glucose": glucose,
            "Hb": hb,
            "Hydration": hydration,
            "Fatigue": prediction
        }

        st.session_state.history.append(st.session_state.latest)

        with placeholder.container():

            st.subheader("Vitals")

            c1, c2, c3 = st.columns(3)
            c1.metric("Glucose", glucose)
            c2.metric("Hb", hb)
            c3.metric("Hydration", hydration)

            st.subheader("Fatigue Level")

            if prediction == "High":
                st.error("HIGH FATIGUE")
            elif prediction == "Medium":
                st.warning("MEDIUM FATIGUE")
            else:
                st.success("LOW FATIGUE")

        time.sleep(2)

# =========================================================
# 🔷 PAGE 2: CDSS OUTPUT TABLE
# =========================================================
elif page == "CDSS Output":

    st.title("Expected CDSS Outputs")

    cdss_table = pd.DataFrame([
        ["Normal","Normal","Normal","Optimal performance condition","Continue regular training"],
        ["High","Normal","Normal","Dehydration-induced performance decline","Increase fluids + electrolyte replacement"],
        ["High","Low","Low","Reduced oxygen delivery → Early fatigue risk","Iron-rich diet, monitor Hb"],
        ["Normal","Low","Low","High metabolic stress + fatigue + injury risk","Reduce training intensity"],
        ["Low","Normal","Low","Hypoglycemia + dehydration → Dizziness/cramps","Immediate carbohydrate + fluids"],
        ["High","Normal","Low","Oxygen deficit + dehydration → Endurance reduction","Recovery + hydration + Hb monitoring"]
    ], columns=[
        "Glucose Level","Hb Estimation","Hydration Status",
        "Interpretation","CDSS Recommendation"
    ])

    st.dataframe(cdss_table, use_container_width=True)

    # Highlight current condition
    if st.session_state.latest:
        st.subheader("Current Condition Match")

        g = st.session_state.latest["Glucose"]
        hb = st.session_state.latest["Hb"]
        h = st.session_state.latest["Hydration"]

        st.write(f"Glucose: {g}, Hb: {hb}, Hydration: {h}")

# =========================================================
# 🔷 PAGE 3: INTERPRETATION & RECOMMENDATION
# =========================================================
elif page == "Interpretation":

    st.title("Interpretation & CDSS Recommendation")

    if st.session_state.latest:

        g = st.session_state.latest["Glucose"]
        hb = st.session_state.latest["Hb"]
        h = st.session_state.latest["Hydration"]

        # Interpretation
        st.subheader("Interpretation")

        if g > 170 and h < 55:
            st.error("Dehydration + high glucose → performance decline")
        elif hb < 11:
            st.warning("Low Hb → reduced oxygen supply")
        elif g < 90:
            st.warning("Low glucose → hypoglycemia risk")
        else:
            st.success("Normal physiological condition")

        # Recommendation
        st.subheader("CDSS Recommendation")

        if g > 170:
            st.write("• Increase fluid intake")
        if hb < 11:
            st.write("• Iron-rich diet")
        if h < 55:
            st.write("• Hydration required")
        if g < 90:
            st.write("• Immediate carbohydrate intake")

    else:
        st.info("Run monitoring first")

# =========================================================
# 🔷 PAGE 4: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":

    st.title("Graph Analysis")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)

        st.line_chart(df[['Glucose','Hb','Hydration']])
        st.bar_chart(df['Fatigue'].value_counts())

        st.subheader("Summary")

        avg = df[['Glucose','Hb','Hydration']].mean()

        st.write(avg)

    else:
        st.info("No data")

# =========================================================
# 🔷 PAGE 5: RECORDED DATA
# =========================================================
elif page == "Recorded Data":

    st.title("Recorded Data")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df)

        csv = df.to_csv(index=False).encode()

        st.download_button(
            "Download CSV",
            csv,
            "fatigue_data.csv",
            "text/csv"
        )

    else:
        st.info("No data available")

