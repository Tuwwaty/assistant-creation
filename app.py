import streamlit as st

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V1 globale")

# =====================================================
# 📊 CONTEXTE JOURNÉE
# =====================================================

st.subheader("📊 Contexte du jour")

temps_libre = st.number_input("Temps libre estimé (heures)", 0.0, 12.0, 4.0)

fatigue = st.selectbox(
    "Niveau de fatigue",
    ["Faible", "Moyenne", "Élevée"]
)

shift = st.selectbox(
    "Type de journée",
    ["Jour normal", "Travail soir"]
)

shift_start = None
shift_end = None

if shift == "Travail soir":
    shift_start = st.number_input("Heure début shift (ex: 18)", 0, 23, 18)
    shift_end = st.number_input("Heure fin shift (ex: 22)", 0, 23, 22)

# =====================================================
# ⛔ CONTRAINTES RÉELLES
# =====================================================

blocked_time = 0

if shift == "Travail soir":
    blocked_time += 0.67  # trajet 40 min
    shift_duration = shift_end - shift_start

    # repas contextuel
    if shift_duration <= 3:
        meal_before = False
        meal_after = True
    else:
        meal_before = True
        blocked_time += 1  # repas avant départ

temps_libre_reel = max(0, temps_libre - blocked_time)

st.write(f"⏱ Temps libre réel : **{temps_libre_reel:.2f}h**")

st.divider()

# =====================================================
# 🎯 ACTIVITÉS & SCORING
# =====================================================

activities = [
    {"name": "Stream Chill", "type": "stream", "energy": "faible"},
    {"name": "Stream Normal", "type": "stream", "energy": "moyenne"},
    {"name": "Gros Stream", "type": "stream", "energy": "haute"},
    {"name": "Montage", "type": "focus"},
    {"name": "Script", "type": "focus"},
    {"name": "Tournage", "type": "focus"},
    {"name": "Sport", "type": "physique"},
    {"name": "Repos", "type": "recup"}
]

def energy_level(fatigue):
    if fatigue == "Faible":
        return "haute"
    elif fatigue == "Moyenne":
        return "moyenne"
    else:
        return "faible"


def score(activity):

    score = 0
    user_energy = energy_level(fatigue)

    # temps
    if temps_libre_reel < 1:
        score -= 50
    elif temps_libre_reel >= 3:
        score += 30

    # énergie match
    if activity.get("energy") == user_energy:
        score += 40
    elif activity.get("energy") == "faible" and user_energy == "moyenne":
        score += 20
    else:
        score -= 20

    # règles stream
    if activity["type"] == "stream":
        if temps_libre_reel < 2:
            return -999  # interdit
        elif temps_libre_reel < 3:
            score -= 10
        else:
            score += 20

    # repos logique
    if activity["type"] == "recup" and fatigue == "Élevée":
        score += 30

    return score


st.subheader("🎯 Suggestions intelligentes")

ranked = []

for act in activities:
    s = score(act)
    ranked.append((act["name"], s))

ranked.sort(key=lambda x: x[1], reverse=True)

for name, s in ranked:
    if s > 0:
        st.write(f"⭐ {name} — score {s}")

st.divider()

# =====================================================
# 📦 PROJETS (CONTINUITÉ)
# =====================================================

st.subheader("📦 Projet en cours")

if "project" not in st.session_state:
    st.session_state.project = {
        "nom": "Vidéo principale",
        "étapes": ["Script", "Tournage", "Montage"],
        "étape": 0,
        "script_done": False
    }

project = st.session_state.project

st.write(f"🎬 {project['nom']}")
st.write(f"Étape actuelle : **{project['étapes'][project['étape']]}**")

if st.button("✔ Étape terminée"):
    project["étape"] += 1

    if project["étape"] >= len(project["étapes"]):
        st.success("🎉 Projet terminé !")
        project["étape"] = 0
    else:
        st.info(f"Prochaine étape : {project['étapes'][project['étape']]}")

st.divider()

# =====================================================
# 🔁 OBJECTIF RÉCURRENT
# =====================================================

st.subheader("🔁 Objectif hebdo")

if "stream_count" not in st.session_state:
    st.session_state.stream_count = 0

target_stream = 2

col1, col2 = st.columns(2)

with col1:
    if st.button("➕ Stream réalisé"):
        st.session_state.stream_count += 1

with col2:
    st.write(f"Streams cette semaine : **{st.session_state.stream_count} / {target_stream}**")

if st.session_state.stream_count < target_stream:
    st.warning("⚠ Objectif stream pas encore atteint")
else:
    st.success("✔ Objectif stream atteint")

st.divider()

# =====================================================
# 📋 PLANNING MANUEL
# =====================================================

st.subheader("📋 Planning manuel")

if "plan" not in st.session_state:
    st.session_state.plan = []

def add(name):
    if name not in st.session_state.plan:
        st.session_state.plan.append(name)

for act in activities:
    if st.button(f"➕ {act['name']}"):
        add(act["name"])

st.write("### Ton plan")

if len(st.session_state.plan) == 0:
    st.info("Rien pour le moment")
else:
    for item in st.session_state.plan:
        st.write(f"• {item}")

if st.button("🗑 Reset"):
    st.session_state.plan = []
