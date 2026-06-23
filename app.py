import streamlit as st
import requests
from datetime import datetime
import re
from collections import defaultdict

st.set_page_config(page_title="Assistant de création", layout="centered")

st.title("🧠 Assistant de création - V5 (planning semaine lisible)")

# =====================================================
# 📅 iCal INPUT
# =====================================================

st.subheader("📅 iCal Strobbo")

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

def parse_hour(t):
    match = re.search(r"T(\d{2})(\d{2})", t)
    if match:
        return int(match.group(1)) + int(match.group(2)) / 60
    return None

def get_weekday(date_str):
    # YYYYMMDD → weekday
    try:
        dt = datetime.strptime(date_str[:8], "%Y%m%d")
        return dt.weekday()  # 0 = lundi
    except:
        return None

work_by_day = defaultdict(list)
total_hours = 0

if ical_url:
    try:
        res = requests.get(ical_url)

        if res.status_code == 200:
            parse_ical(res.text)

            for e in events:
                start = parse_hour(e["start"])
                end = parse_hour(e["end"])

                if start is not None and end is not None:
                    duration = max(0, end - start)
                    total_hours += duration

                    day = get_weekday(e["start"])
                    if day is not None:
                        work_by_day[day].append((start, end))

            st.success("✔ Planning chargé")

    except Exception as e:
        st.error(e)

# =====================================================
# 📅 AFFICHAGE 7 JOURS
# =====================================================

st.subheader("📊 Planning semaine")

days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

for i in range(7):

    if i in work_by_day:
        shifts = work_by_day[i]

        # fusion simple (on prend min start / max end)
        start = min(s[0] for s in shifts)
        end = max(s[1] for s in shifts)

        st.write(f"📅 {days[i]} : {start:.0f}h - {end:.0f}h")

    else:
        st.write(f"📅 {days[i]} : OFF")

st.divider()

# =====================================================
# 📊 CONTEXTE
# =====================================================

fatigue = st.selectbox("Fatigue", ["Faible", "Moyenne", "Élevée"])

temps_jour = st.number_input("Temps total journée (h)", 0.0, 24.0, 24.0)

temps_libre = max(0, temps_jour - total_hours)

st.write(f"⏱ Travail total semaine : **{total_hours:.2f}h**")
st.write(f"🕒 Temps libre estimé : **{temps_libre:.2f}h**")
