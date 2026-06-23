import streamlit as st

st.title("Assistant de création - V1")

start = st.time_input("Début travail")
end = st.time_input("Fin travail")

trajet = st.number_input("Temps de trajet total (heures)", 0.0, 5.0, 1.0)
sommeil = st.number_input("Sommeil estimé (heures)", 0, 12, 8)

work_hours = (end.hour + end.minute/60) - (start.hour + start.minute/60)

temps_libre = 24 - work_hours - trajet - sommeil

st.subheader("Résultats")
st.write(f"Temps libre brut : {temps_libre:.2f}h")

if temps_libre > 5:
    st.success("Beaucoup de temps → stream / création")
elif temps_libre > 2:
    st.info("Temps moyen → tâches courtes")
else:
    st.warning("Peu de temps → repos conseillé")
