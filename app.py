import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

# ---------------- 1. CONFIGURATION ----------------
# Go to ThingSpeak -> Channels -> Channel Settings to get the ID
# Go to ThingSpeak -> API Keys to get the READ API Key
TS_CHANNEL_ID = "YOUR_CHANNEL_ID" 
TS_READ_KEY = "YOUR_READ_API_KEY"

st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# ---------------- 2. ML MODEL SETUP ----------------
@st.cache_data
def load_and_train():
    try:
        # This file must be in your GitHub repository
        data = pd.read_csv("full_fatigue_dataset.csv")
        X = data[['Glucose', 'Hb', 'Hydration']]
        y = data['Fatigue']
        model = RandomForestClassifier()
        model.fit(X, y)
        return model
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

model = load_and_train()

# ---------------- 3. DATA FETCH FUNCTION ----------------
def fetch_from_hardware():
    url = f"https://api.thingspeak.com/channels/{TS_CHANNEL_ID}/feeds/last.json?api_key={TS_READ_KEY}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Verify that ThingSpeak actually has data in the fields
            if 'field1' in data and data['field1'] is not None:
                return {
                    "Glucose": float(data['field1']),
                    "Hb": float(data['field2']),
                    "Hydration": float(data['field3'])
                }
            else:
                return "No Hardware Data Found"
        else:
            return f"ThingSpeak Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {e}"

# ---------------- 4. SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

# ---------------- 5. NAVIGATION / SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Live Monitoring", "Graph Analysis", "Recorded Data"])

# =========================================================
# PAGE 1: LIVE MONITORING
# =========================================================
if page == "Live Monitoring":
    st.title("Fatigue Monitoring System")
    st.subheader("Hardware Status: Live Feed from ESP01")

    col1, col2 = st.columns(2)
    if col1.button("Start Monitoring"):
        st.session_state.monitoring = True
    if col2.button("Stop Monitoring"):
        st.session_state.monitoring = False

    placeholder = st.empty()

    if st.session_state.monitoring:
        while True:
            result = fetch_from_hardware()
            
            with placeholder.container():
                if isinstance(result, dict):
                    # Machine Learning Prediction
                    prediction = model.predict([[result["Glucose"], result["Hb"], result["Hydration"]]])[0]
                    
                    # Store data
                    result["Fatigue"] = prediction
                    st.session_state.history.append(result)

                    # Display Metrics
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Glucose", f"{result['Glucose']} mg/dL")
                    c2.metric("Hb", f"{result['Hb']} g/dL")
                    c3.metric("Hydration", f"{result['Hydration']}%")

                    # Display Alert
                    if prediction == "High":
                        st.error("🚨 HIGH FATIGUE DETECTED")
                    elif prediction == "Medium":
                        st.warning("⚠️ MEDIUM FATIGUE")
                    else:
                        st.success("✅ LOW FATIGUE")
                    
                    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

                else:
                    st.info(f"System Message: {result}")

            # ThingSpeak Free Tier updates every 15 seconds
            time.sleep(15)
            st.rerun()

# =========================================================
# PAGE 2: GRAPH ANALYSIS
# =========================================================
elif page == "Graph Analysis":
    st.title("Trend Analysis")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df[['Glucose', 'Hb', 'Hydration']])
        st.bar_chart(df['Fatigue'].value_counts())
    else:
        st.info("No data recorded yet. Start monitoring to see graphs.")

# =========================================================
# PAGE 3: RECORDED DATA
# =========================================================
elif page == "Recorded Data":
    st.title("History Log")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data as CSV", csv, "fatigue_history.csv", "text/csv")
    else:
        st.info("No history available.")


