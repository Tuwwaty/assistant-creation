import streamlit as st
import requests
from datetime import datetime
import re

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V3 iCal")

# =====================================================
# 📅 iCal INPUT
# =====================================================

st.subheader("📅 Synchronisation planning")

ical_url = st.text_input("Lien iCal (Strobbo)")

events = []

def parse_ical(data):
    """Extraction simple des événements iCal"""
    lines = data.splitlines()

    current_event = {}

    for line in lines:
        if "DTSTART" in line:
            current_event["start"] = line.split(":")[-1]
        elif "DTEND" in line:
            current_event["end"] = line.split(":")[-1]

        if line.strip() == "END:VEVENT":
            if "start" in current_event and "end" in current_event:
                events.append(current_event)
            current_event = {}

def convert_time(ical_time):
    """Convertit format iCal en heure simple"""
    match = re.search(r"T(\d{2})(\d{2})", ical_time)
    if match:
        return int(match.group(1)) + int(match.group(2)) / 60
    return 0

work_hours = 0

if ical_url:
    try:
        res = requests.get(ical_url)
        if res.status_code == 200:
            parse_ical(res.text)

            for e in events:
                start = convert_time(e["start"])
                end = convert_time(e["end"])
                work_hours += (end - start)

            st.success("✔ Calendrier chargé")
        else:
            st.error("Erreur de chargement iCal")

    except Exception as e:
        st.error(f"Erreur : {e}")

# =====================================================
# 📊 CONTEXTE
# =====================================================

st.subheader("📊 Analyse automatique")

fatigue = st.selectbox(
    "Niveau de fatigue",
    ["Faible", "Moyenne", "Élevée"]
)

temps_total_jour = st.number_input("Temps total dans la journée (h)", 0.0, 24.0, 24.0)

temps_libre = max(0, temps_total_jour - work_hours)

st.write(f"⏱ Travail total : **{work_hours:.2f}h**")
st.write(f"🕒 Temps libre réel : **{temps_libre:.2f}h**")

st.divider()

# =====================================================
# 🧠 ACTIVITÉS INTELLIGENTES
# =====================================================

activities = [
    {"name": "Stream Chill", "energy": "faible", "type": "stream"},
    {"name": "Stream Normal", "energy": "moyenne", "type": "stream"},
    {"name": "Gros Stream", "energy": "haute", "type": "stream"},
    {"name": "Montage", "energy": "haute", "type": "focus"},
    {"name": "Script", "energy": "moyenne", "type": "focus"},
    {"name": "Tournage", "energy": "haute", "type": "focus"},
    {"name": "Sport", "energy": "moyenne", "type": "physique"},
    {"name": "Repos", "energy": "faible", "type": "recup"},
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

    # temps dispo
    if temps_libre < 2 and activity["type"] == "stream":
        return -999

    if temps_libre >= 3:
        score += 20

    # énergie
    if activity["energy"] == user_energy:
        score += 40
    elif activity["energy"] == "faible":
        score += 10
    else:
        score -= 20

    # bonus stream régulier
    if activity["type"] == "stream":
        score += 10

    # repos si fatigue élevée
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
# 📦 INFO DEBUG
# =====================================================

st.subheader("📦 Debug planning")

st.write(f"Nombre d'événements détectés : {len(events)}")
