import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

# --- SETTINGS (Change these to your Channel details) ---
TS_CHANNEL_ID = "YOUR_CHANNEL_ID" 
TS_READ_KEY = "YOUR_READ_API_KEY"

st.set_page_config(page_title="Fatigue Monitoring System", layout="wide")

# --- DATA FETCHING ---
def fetch_data():
    url = f"https://api.thingspeak.com/channels/{TS_CHANNEL_ID}/feeds/last.json?api_key={TS_READ_KEY}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if isinstance(data, dict) and 'field1' in data:
            return {
                "Glucose": float(data['field1']),
                "Hb": float(data['field2']),
                "Hydration": float(data['field3'])
            }
    except:
        return None
    return None

# --- ML MODEL SETUP ---
@st.cache_data
def train_model():
    df = pd.read_csv("full_fatigue_dataset.csv")
    model = RandomForestClassifier()
    model.fit(df[['Glucose', 'Hb', 'Hydration']], df['Fatigue'])
    return model

model = train_model()

# --- APP LOGIC ---
if "history" not in st.session_state: st.session_state.history = []
if "run" not in st.session_state: st.session_state.run = False

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Live Monitoring", "Graph Analysis", "Recorded Data"])

if page == "Live Monitoring":
    st.title("Fatigue Monitoring System")
    
    col1, col2 = st.columns(2)
    if col1.button("Start"): st.session_state.run = True
    if col2.button("Stop"): st.session_state.run = False

    placeholder = st.empty()

    while st.session_state.run:
        hw_data = fetch_data()
        if hw_data:
            pred = model.predict([[hw_data["Glucose"], hw_data["Hb"], hw_data["Hydration"]]])[0]
            hw_data["Fatigue"] = pred
            st.session_state.history.append(hw_data)

            with placeholder.container():
                st.subheader("Live Vitals")
                c1, c2, c3 = st.columns(3)
                c1.metric("Glucose", hw_data["Glucose"])
                c2.metric("Hb", hw_data["Hb"])
                c3.metric("Hydration", hw_data["Hydration"])
                
                if pred == "High": st.error("HIGH FATIGUE")
                elif pred == "Medium": st.warning("MEDIUM FATIGUE")
                else: st.success("LOW FATIGUE")
        
        time.sleep(15) # Wait for ThingSpeak update
        st.rerun()

elif page == "Graph Analysis":
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.line_chart(df_hist[['Glucose', 'Hb', 'Hydration']])
    else:
        st.info("No data yet.")

elif page == "Recorded Data":
    if st.session_state.history:
        st.write(pd.DataFrame(st.session_state.history))

