import streamlit as st
import pandas as pd
import random
import time
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# ---------------- LEVEL FUNCTIONS ----------------
def glucose_level(g):
    if g < 100:
        return "Low"
    elif g <= 150:
        return "Normal"
    else:
        return "High"

def hb_level(hb):
    if hb < 11:
        return "Low"
    elif hb <= 14:
        return "Normal"
    else:
        return "High"

def hydration_level(h):
    if h < 55:
        return "Low"
    elif h <= 65:
        return "Normal"
    else:
        return "High"

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
    start = col1.button("Start Monitoring")
    stop = col2.button("Stop Monitoring")

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
# 🔷 PAGE 2: CDSS OUTPUT
# =========================================================
elif page == "CDSS Output":

    st.title("CDSS Output")

    # -------- CURRENT MATCH (TOP) --------
    if st.session_state.latest:

        g = st.session_state.latest["Glucose"]
        hb = st.session_state.latest["Hb"]
        h = st.session_state.latest["Hydration"]

        g_level = glucose_level(g)
        hb_level_val = hb_level(hb)
        h_level = hydration_level(h)

        st.subheader("Current Condition Match")

        col1, col2, col3 = st.columns(3)
        col1.metric("Glucose Level", g_level)
        col2.metric("Hb Level", hb_level_val)
        col3.metric("Hydration Level", h_level)

    else:
        st.info("Run monitoring first")

    st.divider()

    # -------- CDSS TABLE (BOTTOM) --------
    st.subheader("Expected CDSS Outputs")

    cdss_table = pd.DataFrame([
        ["Normal","Normal","Normal","Optimal performance condition","Continue regular training"],
        ["High","Normal","Normal","Dehydration-induced performance decline","Increase fluids + electrolytes"],
        ["High","Low","Low","Reduced oxygen delivery → Early fatigue risk","Iron-rich diet + monitor Hb"],
        ["Normal","Low","Low","High metabolic stress + fatigue + injury risk","Reduce training intensity"],
        ["Low","Normal","Low","Hypoglycemia + dehydration → Dizziness/cramps","Immediate carbohydrate + fluids"],
        ["High","Normal","Low","Oxygen deficit + dehydration → Endurance reduction","Recovery + hydration"]
    ], columns=[
        "Glucose Level","Hb Estimation","Hydration Status",
        "Interpretation","CDSS Recommendation"
    ])

    st.dataframe(cdss_table, use_container_width=True)

# =========================================================
# 🔷 PAGE 3: INTERPRETATION
# =========================================================
elif page == "Interpretation":

    st.title("Interpretation & Recommendation")

    if st.session_state.latest:

        g = st.session_state.latest["Glucose"]
        hb = st.session_state.latest["Hb"]
        h = st.session_state.latest["Hydration"]

        st.subheader("Interpretation")

        if g > 170 and h < 55:
            st.error("Dehydration + high glucose → performance decline")
        elif hb < 11:
            st.warning("Low Hb → reduced oxygen delivery")
        elif g < 90:
            st.warning("Hypoglycemia risk")
        else:
            st.success("Normal condition")

        st.subheader("Recommendation")

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

        st.write({
            "Average Glucose": round(avg['Glucose'],2),
            "Average Hb": round(avg['Hb'],2),
            "Average Hydration": round(avg['Hydration'],2)
        })

    else:
        st.info("No data available")

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

