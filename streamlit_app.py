
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="EcoLoop Node | NGIH",
    page_icon="♻️",
    layout="wide"
)

st.image("IMG-20261028-WA0000.jpg", width=180)

st.title("♻️ EcoLoop Node")
st.subheader("Intelligent Waste Monitoring Dashboard")

st.info("Prototype Demo: Waste figures are simulated. No physical sensors are connected yet.")

# Starting data
if "bins" not in st.session_state:
    st.session_state.bins = {
        "Plastic": 0.0,
        "Paper": 0.0,
        "Metal": 0.0
    }

if "history" not in st.session_state:
    st.session_state.history = []

st.header("Waste Collection Stations")

capacity = 50

for material in st.session_state.bins:
    st.subheader(f"{material} Bin")

    current = st.session_state.bins[material]
    st.write(f"Recorded quantity: {current:.1f} kg")
    st.progress(min(current / capacity, 1.0))

    if current >= capacity:
        st.warning("Collection needed!")
    else:
        st.success("Capacity available")

st.divider()

st.header("Record New Waste")

material = st.selectbox(
    "Select material",
    ["Plastic", "Paper", "Metal"]
)

weight = st.number_input(
    "Enter quantity in kg",
    min_value=0.1,
    max_value=50.0,
    step=0.5
)

if st.button("Add Waste"):
    st.session_state.bins[material] += weight

    st.session_state.history.append({
        "Material": material,
        "Weight (kg)": weight,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    st.success("Waste record added!")

st.divider()

st.header("Collection History")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)

    st.bar_chart(
        df.groupby("Material")["Weight (kg)"].sum()
    )

    st.download_button(
        "Download Records",
        df.to_csv(index=False),
        file_name="ecoloop_records.csv",
        mime="text/csv"
    )
else:
    st.write("No waste records yet.")

st.divider()

if st.button("Reset Demo"):
    st.session_state.bins = {
        "Plastic": 0.0,
        "Paper": 0.0,
        "Metal": 0.0
    }
    st.session_state.history = []
    st.rerun()


st.divider()

# NGIH branding
st.image("IMG-20261028-WA0000.jpg", width=180)

st.markdown("""
<div style="text-align: center; padding: 15px;">
    <h2 style="color: #1687FF;">ECOLOOP NODE</h2>
    <p><strong>Powered by Next Gen Impact Hub (NGIH)</strong></p>
    <hr>
    <p><strong>Munashe Roy Mutopa</strong></p>
    <p>Project Coordinator & Developer</p>
    <p style="color: gray; font-size: 12px;">
        Building technology for sustainable communities.
    </p>
    <p style="color: gray; font-size: 11px;">
        Sensor integration is under development.
    </p>
</div>
""", unsafe_allow_html=True)

