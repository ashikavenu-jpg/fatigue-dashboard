import streamlit as st
import pandas as pd
import requests
import time
from sklearn.ensemble import RandomForestClassifier

# --- 1. SETTINGS ---
TS_CHANNEL_ID = "3150784" 
# PASTE YOUR READ API KEY BELOW
TS_READ_KEY = "YOUR_READ_API_KEY_HERE" 

st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# --- 2. ML MODEL ---
@st.cache_data
def train_model():
    try:
        df = pd.read_csv("full_fatigue_dataset.csv")
        model = RandomForestClassifier()
        model.fit(df[['Glucose', 'Hb', 'Hydration']], df['Fatigue'])
        return model
    except:
        st.error("Missing full_fatigue_dataset.csv")
        return None

model = train_model()

# --- 3. UI ---
st.title("Fatigue Monitoring System")
st.markdown(f"**Channel:** {TS_CHANNEL_ID}")

if "run" not in st.session_state: st.session_state.run = False

c1, c2 = st.columns(2)
if c1.button("🚀 START MONITORING"): st.session_state.run = True
if c2.button("🛑 STOP"): st.session_state.run = False

placeholder = st.empty()

if st.session_state.run:
    while True:
        url = f"https://api.thingspeak.com/channels/{TS_CHANNEL_ID}/feeds/last.json?api_key={TS_READ_KEY}"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            
            # Check if hardware has sent data (field1 is not Null)
            if r.status_code == 200 and data.get('field1') is not None:
                g = float(data['field1'])
                hb = float(data['field2'])
                hy = float(data['field3'])
                pred = model.predict([[g, hb, hy]])[0]
                
                with placeholder.container():
                    st.subheader("Live Hardware Feed")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Glucose", f"{g} mg/dL")
                    m2.metric("Hb", f"{hb} g/dL")
                    m3.metric("Hydration", f"{hy}%")
                    
                    if pred == "High": st.error("🚨 HIGH FATIGUE")
                    elif pred == "Medium": st.warning("⚠️ MEDIUM FATIGUE")
                    else: st.success("✅ LOW FATIGUE")
            else:
                placeholder.info("Searching for hardware data... Ensure your finger is on the sensor.")
        except:
            placeholder.error("Connection lost. Checking ThingSpeak...")

        time.sleep(15) # ThingSpeak Free Tier limit
        st.rerun()


