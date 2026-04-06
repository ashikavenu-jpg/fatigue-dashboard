import streamlit as st
import pandas as pd
import requests
import time
from sklearn.ensemble import RandomForestClassifier

# --- 1. YOUR ACTUAL THINGSPEAK CREDENTIALS ---
TS_CHANNEL_ID = "3150784" 
# Paste your READ API KEY here (from the API Keys tab in ThingSpeak)
TS_READ_KEY = "PASTE_YOUR_READ_API_KEY_HERE" 

# --- UPDATED TITLE IN CONFIG ---
st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# --- 2. ML MODEL SETUP ---
@st.cache_data
def train_model():
    try:
        df = pd.read_csv("full_fatigue_dataset.csv")
        model = RandomForestClassifier()
        model.fit(df[['Glucose', 'Hb', 'Hydration']], df['Fatigue'])
        return model
    except:
        st.error("Error: 'full_fatigue_dataset.csv' not found in GitHub.")
        return None

model = train_model()

# --- 3. SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "run" not in st.session_state: st.session_state.run = False

# --- 4. THE LIVE DASHBOARD ---
# --- UPDATED TITLE ON PAGE ---
st.title("Fatigue Monitoring System")
st.markdown(f"**Connected to ThingSpeak Channel:** `{TS_CHANNEL_ID}`")

# Control Buttons
c_start, c_stop = st.columns(2)
if c_start.button("🚀 START MONITORING", use_container_width=True):
    st.session_state.run = True
if c_stop.button("🛑 STOP", use_container_width=True):
    st.session_state.run = False

placeholder = st.empty()

if st.session_state.run:
    while True:
        url = f"https://api.thingspeak.com/channels/{TS_CHANNEL_ID}/feeds/last.json?api_key={TS_READ_KEY}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                
                if data.get('field1') is not None:
                    g = float(data['field1'])
                    hb = float(data['field2'])
                    hy = float(data['field3'])
                    
                    pred = model.predict([[g, hb, hy]])[0]
                    
                    with placeholder.container():
                        st.subheader("Live Hardware Data")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Glucose", f"{g} mg/dL")
                        m2.metric("Hemoglobin", f"{hb} g/dL")
                        m3.metric("Hydration", f"{hy}%")
                        
                        if pred == "High": st.error("🚨 HIGH FATIGUE DETECTED")
                        elif pred == "Medium": st.warning("⚠️ MEDIUM FATIGUE")
                        else: st.success("✅ LOW FATIGUE")
                    
                    st.session_state.history.append({"Glucose":g, "Hb":hb, "Hydration":hy, "Fatigue":pred})
                else:
                    placeholder.info("Waiting for data from hardware sensor...")
            elif r.status_code == 404:
                st.error("Error 404: Check Channel ID.")
                break
        except Exception as e:
            st.error(f"Sync Error: {e}")

        time.sleep(15) 
        st.rerun()

# Display Data History
if st.session_state.history:
    st.divider()
    st.subheader("Session History")
    st.dataframe(pd.DataFrame(st.session_state.history).tail(10), use_container_width=True)


