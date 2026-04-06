import streamlit as st
import pandas as pd
import requests  # Add this for API calls
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG & THINGSPEAK ----------------
THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID" # Replace with your ID
THINGSPEAK_READ_API_KEY = "YOUR_READ_KEY"  # Replace with your Read API Key

# ---------------- LEVEL FUNCTIONS ----------------
def glucose_level(g):
    if g < 100: return "Low"
    elif g <= 150: return "Normal"
    else: return "High"

def hb_level(hb):
    if hb < 11: return "Low"
    elif hb <= 14: return "Normal"
    else: return "High"

def hydration_level(h):
    if h < 55: return "Low"
    elif h <= 65: return "Normal"
    else: return "High"

# ---------------- FETCH DATA FROM THINGSPEAK ----------------
def fetch_thingspeak_data():
    """Fetches the latest entry from ThingSpeak."""
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds/last.json?api_key={THINGSPEAK_READ_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        # ThingSpeak fields are strings, convert to float/int
        return {
            "Glucose": float(data['field1']),
            "Hb": float(data['field2']),
            "Hydration": float(data['field3'])
        }
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# ---------------- LOAD MODEL DATA ----------------
@st.cache_data
def load_data():
    # Ensure this file exists in your project folder
    return pd.read_csv("full_fatigue_dataset.csv")

data = load_data()
X = data[['Glucose', 'Hb', 'Hydration']]
y = data['Fatigue']
model = RandomForestClassifier()
model.fit(X, y)

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "latest" not in st.session_state:
    st.session_state.latest = {}
if "run" not in st.session_state:
    st.session_state.run = False

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Live Monitoring", "CDSS Output", "Interpretation", "Graph Analysis", "Recorded Data"])

# =========================================================
# 🔷 PAGE 1: LIVE MONITORING (UPDATED)
# =========================================================
if page == "Live Monitoring":
    st.title("Fatigue Monitoring System")

    col1, col2 = st.columns(2)
    if col1.button("Start Monitoring"):
        st.session_state.run = True
    if col2.button("Stop Monitoring"):
        st.session_state.run = False

    placeholder = st.empty()

    while st.session_state.run:
        # Fetch data from Hardware via ThingSpeak
        hw_data = fetch_thingspeak_data()
        
        if hw_data:
            glucose = hw_data["Glucose"]
            hb = hw_data["Hb"]
            hydration = hw_data["Hydration"]

            # Predict using the ML Model
            prediction = model.predict([[glucose, hb, hydration]])[0]

            st.session_state.latest = {
                "Glucose": glucose,
                "Hb": hb,
                "Hydration": hydration,
                "Fatigue": prediction
            }
            st.session_state.history.append(st.session_state.latest)

            with placeholder.container():
                st.subheader("Vitals (Live from Hardware)")
                c1, c2, c3 = st.columns(3)
                c1.metric("Glucose", f"{glucose} mg/dL")
                c2.metric("Hb", f"{hb} g/dL")
                c3.metric("Hydration", f"{hydration} %")

                st.subheader("Fatigue Level")
                if prediction == "High":
                    st.error("HIGH FATIGUE")
                elif prediction == "Medium":
                    st.warning("MEDIUM FATIGUE")
                else:
                    st.success("LOW FATIGUE")
        
        # ThingSpeak updates every 15s on free tier; 
        # Don't refresh faster than your hardware sends data.
        time.sleep(15) 
        st.rerun()

# ... (Keep your other pages (CDSS, Interpretation, etc.) exactly as they were) ...

