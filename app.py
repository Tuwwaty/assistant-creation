import streamlit as st

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V2")

# -------------------------
# CONTEXTE
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
# ACTIVITÉS (SUGGESTIONS)
# -------------------------

st.subheader("🎯 Suggestions")

activities = [
    "Stream",
    "Montage",
    "Script",
    "Tournage",
    "Sport",
    "Repos"
]

def is_recommended(activity, fatigue, time_available):
    # logique simple mais efficace
    if time_available < 1 and activity not in ["Repos", "Sport"]:
        return False

    if fatigue == "Élevée":
        if activity in ["Montage", "Tournage"]:
            return False

    if fatigue == "Moyenne":
        if activity == "Montage" and time_available < 3:
            return False

    return True

recommended = []

for act in activities:
    if is_recommended(act, fatigue, temps_libre):
        recommended.append(act)
        st.write(f"✔ {act}")

if len(recommended) == 0:
    st.info("Aucune activité idéale aujourd'hui → privilégie le repos ou des tâches légères.")

st.divider()

# -------------------------
# PLANNING MANUEL
# -------------------------

st.subheader("📋 Ton planning")

if "plan" not in st.session_state:
    st.session_state.plan = []

def add_to_plan(activity):
    if activity not in st.session_state.plan:
        st.session_state.plan.append(activity)

for act in activities:
    if st.button(f"➕ Ajouter {act}"):
        add_to_plan(act)

st.write("### Plan actuel :")

if len(st.session_state.plan) == 0:
    st.info("Aucune activité ajoutée.")
else:
    for item in st.session_state.plan:
        st.write(f"• {item}")

if st.button("🗑 Reset planning"):
    st.session_state.plan = []
