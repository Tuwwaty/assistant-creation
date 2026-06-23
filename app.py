import streamlit as st
import requests
from datetime import datetime
import re
from collections import defaultdict

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V4 (planning visuel)")

# =====================================================
# 📅 iCal INPUT
# =====================================================

st.subheader("📅 Synchronisation Strobbo (iCal)")

ical_url = st.text_input("Lien iCal")

events = []

def parse_ical(data):
    lines = data.splitlines()
    current = {}

    for line in lines:
        if "DTSTART" in line:
            current["start"] = line.split(":")[-1]
        elif "DTEND" in line:
            current["end"] = line.split(":")[-1]

        if line.strip() == "END:VEVENT":
            if "start" in current and "end" in current:
                events.append(current)
            current = {}

def parse_hour(ical_time):
    match = re.search(r"T(\d{2})(\d{2})", ical_time)
    if match:
        return int(match.group(1)) + int(match.group(2)) / 60
    return 0

work_hours_total = 0
weekly_data = defaultdict(float)

if ical_url:
    try:
        res = requests.get(ical_url)

        if res.status_code == 200:
            parse_ical(res.text)

            for e in events:
                start = parse_hour(e["start"])
                end = parse_hour(e["end"])
                duration = max(0, end - start)

                work_hours_total += duration

                # approximation simple : jour = hash dans iCal
                day_key = e["start"][0:8]  # YYYYMMDD
                weekly_data[day_key] += duration

            st.success("✔ Planning chargé")

        else:
            st.error("Erreur chargement iCal")

    except Exception as e:
        st.error(e)

# =====================================================
# 📊 VISUALISATION SEMAINE
# =====================================================

st.subheader("📊 Temps de travail sur la semaine")

if weekly_data:

    chart_data = []

    for day, hours in sorted(weekly_data.items()):
        formatted_day = f"{day[6:8]}/{day[4:6]}"
        chart_data.append({
            "Jour": formatted_day,
            "Heures": round(hours, 2)
        })

    st.bar_chart(
        {item["Jour"]: item["Heures"] for item in chart_data}
    )

st.write(f"🧾 Total semaine : **{work_hours_total:.2f}h de travail**")

st.divider()

# =====================================================
# 📊 CONTEXTE
# =====================================================

st.subheader("📊 Contexte")

fatigue = st.selectbox(
    "Fatigue",
    ["Faible", "Moyenne", "Élevée"]
)

temps_jour = st.number_input("Temps total journée (h)", 0.0, 24.0, 24.0)

temps_libre = max(0, temps_jour - work_hours_total)

st.write(f"⏱ Temps libre estimé : **{temps_libre:.2f}h**")

st.divider()

# =====================================================
# 🧠 ACTIVITÉS
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
    return {"Faible": "haute", "Moyenne": "moyenne", "Élevée": "faible"}[fatigue]


def score(a):
    s = 0
    user_energy = energy_level(fatigue)

    if temps_libre < 2 and a["type"] == "stream":
        return -999

    if a["energy"] == user_energy:
        s += 40
    elif a["energy"] == "faible":
        s += 10
    else:
        s -= 20

    if a["type"] == "stream":
        s += 15

    if a["type"] == "recup" and fatigue == "Élevée":
        s += 30

    return s


st.subheader("🎯 Suggestions")

ranked = [(a["name"], score(a)) for a in activities]
ranked.sort(key=lambda x: x[1], reverse=True)

for name, s in ranked:
    if s > 0:
        st.write(f"⭐ {name} — score {s}")

st.divider()

# =====================================================
# 📦 DEBUG
# =====================================================

st.subheader("📦 Debug")

st.write(f"Événements détectés : {len(events)}")
