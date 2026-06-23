import streamlit as st

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V2")

# -------------------------
# CONTEXTE (simple V1.5)
# -------------------------

st.subheader("📊 Contexte du jour")

temps_libre = st.number_input("Temps libre estimé (heures)", 0.0, 12.0, 3.0)

fatigue = st.selectbox(
    "Niveau de fatigue",
    ["Faible", "Moyenne", "Élevée"]
)

st.write(f"⏱ Temps libre : **{temps_libre}h**")
st.write(f"🧠 Fatigue : **{fatigue}**")

st.divider()

# -------------------------
# ACTIVITÉS
# -------------------------

st.subheader("🎯 Activités proposées")

if "plan" not in st.session_state:
    st.session_state.plan = []

def add_activity(name):
    if name not in st.session_state.plan:
        st.session_state.plan.append(name)

col1, col2 = st.columns(2)

with col1:
    if st.button("🎥 Stream"):
        add_activity("Stream")

    if st.button("🧾 Script"):
        add_activity("Script")

    if st.button("🏃 Sport"):
        add_activity("Sport")

with col2:
    if st.button("✂ Montage"):
        add_activity("Montage")

    if st.button("🎬 Tournage"):
        add_activity("Tournage")

    if st.button("😴 Repos"):
        add_activity("Repos")

st.divider()

# -------------------------
# PLAN FINAL
# -------------------------

st.subheader("📋 Ton plan du jour")

if len(st.session_state.plan) == 0:
    st.info("Aucune activité sélectionnée pour le moment.")
else:
    for item in st.session_state.plan:
        st.write(f"✔ {item}")

if st.button("🗑 Reset planning"):
    st.session_state.plan = []
