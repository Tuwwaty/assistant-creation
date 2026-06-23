import streamlit as st
import requests
from datetime import datetime
import re
from collections import defaultdict

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V7 (Google Agenda)")

# =====================================================
# 📅 INPUT GOOGLE CALENDAR (ICAL LINK)
# =====================================================

st.subheader("📅 Synchronisation Google Agenda (iCal)")

ical_url = st.text_input("Lien iCal Google Agenda")

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

# =====================================================
# 🧠 PARSING ROBUSTE
# =====================================================

def parse_hour(t):
    try:
        match = re.search(r"T(\d{2})(\d{2})", t)
        if match:
            return int(match.group(1)) + int(match.group(2)) / 60
    except:
        return None

def get_day(date_str):
    try:
        clean = date_str.split("T")[0]
        dt = datetime.strptime(clean[:8], "%Y%m%d")
        return dt.weekday()
    except:
        return None

def compute_duration(start, end):
    # 🔥 gestion minuit
    if end < start:
        end += 24
    return max(0, end - start)

# =====================================================
# 📥 LOAD CALENDAR
# =====================================================

work_by_day = defaultdict(list)
total_work = 0

if ical_url:
    try:
        res = requests.get(ical_url)

        if res.status_code == 200:
            parse_ical(res.text)

            for e in events:
                start = parse_hour(e["start"])
                end = parse_hour(e["end"])

                if start is None or end is None:
                    continue

                duration = compute_duration(start, end)
                total_work += duration

                day = get_day(e["start"])

                if day is not None:
                    work_by_day[day].append({
                        "start": start,
                        "end": end,
                        "duration": duration
                    })

            st.success("✔ Google Agenda chargé")

        else:
            st.error("Erreur chargement calendrier")

    except Exception as e:
        st.error(e)

# =====================================================
# 📅 AFFICHAGE 7 JOURS PROPRE
# =====================================================

st.subheader("📊 Planning semaine")

days = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]

for i in range(7):

    if i in work_by_day:

        shifts = work_by_day[i]

        parts = []

        for s in shifts:
            sh = int(s["start"])
            sm = int((s["start"] % 1) * 60)

            eh = int(s["end"] % 24)
            em = int((s["end"] % 1) * 60)

            parts.append(f"{sh:02d}h{sm:02d}-{eh:02d}h{em:02d}")

        st.write(f"📅 {days[i]} : " + " | ".join(parts))

    else:
        st.write(f"📅 {days[i]} : OFF")

st.divider()

# =====================================================
# 📊 STATS
# =====================================================

st.subheader("📊 Analyse")

fatigue = st.selectbox("Fatigue", ["Faible","Moyenne","Élevée"])

temps_jour = st.number_input("Temps total journée (h)", 0.0, 24.0, 24.0)

temps_libre = max(0, temps_jour - total_work)

st.write(f"⏱ Travail total semaine : **{total_work:.2f}h**")
st.write(f"🕒 Temps libre estimé : **{temps_libre:.2f}h**")

# =====================================================
# 🎯 ACTIVITÉS SIMPLES (BASE IA FUTURE)
# =====================================================

activities = [
    {"name":"Stream Chill","energy":"faible"},
    {"name":"Stream Normal","energy":"moyenne"},
    {"name":"Gros Stream","energy":"haute"},
    {"name":"Montage","energy":"haute"},
    {"name":"Script","energy":"moyenne"},
    {"name":"Tournage","energy":"haute"},
    {"name":"Sport","energy":"moyenne"},
    {"name":"Repos","energy":"faible"}
]

def energy_level(f):
    return {"Faible":"haute","Moyenne":"moyenne","Élevée":"faible"}[f]

def score(a):
    s = 0
    user = energy_level(fatigue)

    if temps_libre < 2 and "Stream" in a["name"]:
        return -999

    if a["energy"] == user:
        s += 40
    elif a["energy"] == "faible":
        s += 10
    else:
        s -= 20

    if "Stream" in a["name"]:
        s += 15

    return s

st.subheader("🎯 Suggestions")

ranked = sorted([(a["name"], score(a)) for a in activities], key=lambda x: x[1], reverse=True)

for name, s in ranked:
    if s > 0:
        st.write(f"⭐ {name} — {s}")

st.divider()

# =====================================================
# DEBUG
# =====================================================

st.subheader("📦 Debug")

st.write(f"Événements détectés : {len(events)}")
st.write(work_by_day)
