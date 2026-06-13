import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Jouw key hier
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- LOGIN & NAVIGATIE ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam", key="user_input")
        wachtwoord = st.text_input("Wachtwoord", type="password", key="pass_input")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Ongeldige gegevens")
    else:
        st.success("Ingelogd als Admin")
        menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if menu == "Dashboard":
        st.title("📊 Dashboard")
        data = supabase.table("klachten").select("*").execute().data
        for k in data:
            with st.expander(f"Klacht: {k.get('volledige_naam')} - Status: {k.get('status')}"):
                st.write(f"**ID:** {k.get('id_nummer')} | **Tel:** {k.get('telefoon_whatsapp')}")
                # Gebruik altijd een unieke key in loops!
                status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], key=f"status_{k['id']}")
                if st.button("Update Status", key=f"upd_{k['id']}"):
                    supabase.table("klachten").update({"status": status}).eq("id", k['id']).execute()
                    st.rerun()

    elif menu == "Rapporten":
        st.title("📈 Rapporten")
        st.write("Visualisatie van gegevens...")

    elif menu == "Instellingen":
        st.title("⚙️ Instellingen")
        st.write("Gebruikersbeheer...")

# --- FORMULIER (Blijft onderaan) ---
st.divider()
st.title("Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    naam = st.text_input("Volledige naam")
    # ... (rest van je formulier)
    if st.form_submit_button("Verstuur klacht"):
        # ... (je insert logica)
        st.success("Verzonden!")
