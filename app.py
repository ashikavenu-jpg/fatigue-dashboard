import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from sklearn.ensemble import RandomForestClassifier

@st.cache_data
def load_data():
    return pd.read_csv("full_fatigue_dataset.csv")

data = load_data()

X = data[['Glucose', 'Hb', 'Hydration']]
y = data['Fatigue']

model = RandomForestClassifier()
model.fit(X, y)

st.title("🏃 Smart Fatigue Monitoring System")

st.sidebar.header("Live Sensor Input")

glucose = st.sidebar.slider("Glucose", 80, 200, 140)
hb = st.sidebar.slider("Hb", 8, 18, 13)
hydration = st.sidebar.slider("Hydration", 40, 100, 60)

prediction = model.predict([[glucose, hb, hydration]])[0]

if prediction == "High":
    st.error("⚠ HIGH FATIGUE")
elif prediction == "Medium":
    st.warning("⚠ MEDIUM FATIGUE")
else:
    st.success("✅ LOW FATIGUE")

st.subheader("Fatigue Distribution")
st.bar_chart(data['Fatigue'].value_counts())
