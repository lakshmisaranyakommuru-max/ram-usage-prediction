import streamlit as st
import psutil
import pickle
import pandas as pd

st.set_page_config(
    page_title="RAM Usage Prediction",
    page_icon="💻",
    layout="wide"
)

# Load trained ML model
with open("model.pkl", "rb") as file:
    model = pickle.load(file)

st.title("💻 RAM Usage Prediction and Optimization")
st.write("Machine Learning based system for predicting and monitoring RAM usage.")
if st.button("🔄 Refresh System Data"):
    st.rerun()

# Get current system data
cpu = psutil.cpu_percent(interval=1)

ram = psutil.virtual_memory()
current_ram = ram.percent
available_ram = ram.available / (1024 ** 3)

process_count = len(psutil.pids())

# ML prediction
prediction = model.predict([[
    cpu,
    available_ram,
    process_count
]])

predicted_ram = prediction[0]

# Status
if predicted_ram >= 80:
    status = "🔴 HIGH"
elif predicted_ram >= 60:
    status = "🟡 MODERATE"
else:
    status = "🟢 NORMAL"

# Display information
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current RAM", f"{current_ram:.1f}%")

with col2:
    st.metric("Predicted RAM", f"{predicted_ram:.1f}%")

with col3:
    st.metric("CPU Usage", f"{cpu:.1f}%")

with col4:
    st.metric("Available RAM", f"{available_ram:.2f} GB")

st.subheader("📊 System Status")

st.write(f"**RAM Status:** {status}")
st.write(f"**Running Processes:** {process_count}")

# RAM progress
st.progress(min(int(current_ram), 100))

# RAM Usage History Graph

if "ram_history" not in st.session_state:
    st.session_state.ram_history = []

st.session_state.ram_history.append(current_ram)

# Keep only the latest 20 readings
st.session_state.ram_history = st.session_state.ram_history[-20:]

st.subheader("📈 RAM Usage History")

st.line_chart(st.session_state.ram_history)


# Top processes
st.subheader("🔍 Top RAM-Consuming Processes")

processes = []

for process in psutil.process_iter(
    ["pid", "name", "memory_percent"]
):
    try:
        info = process.info

        if info["memory_percent"] is not None:
            processes.append(info)

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

processes.sort(
    key=lambda x: x["memory_percent"],
    reverse=True
)

top_processes = processes[:10]

# Display Top 3 RAM-consuming applications

st.subheader("🏆 Top 3 RAM Consumers")

for process in processes[:3]:
    st.write(
        f"🔴 {process['name']} — "
        f"{process['memory_percent']:.2f}% RAM"
    )


df = pd.DataFrame(top_processes)

if not df.empty:
    df = df.rename(columns={
        "pid": "PID",
        "name": "Process",
        "memory_percent": "RAM Usage (%)"
    })

    st.dataframe(
        df,
        use_container_width=True
    )

# Recommendation
st.subheader("💡 Optimization Recommendation")

if current_ram >= 80:
    st.error(
        "RAM usage is high. Close unused applications "
        "that are consuming large amounts of memory."
    )
elif current_ram >= 60:
    st.warning(
        "RAM usage is moderate. Consider closing "
        "unnecessary background applications."
    )
else:
    st.success(
        "RAM usage is normal. No optimization is currently required."
    )

st.caption("RAM Usage Prediction and Optimization — Mini Project")