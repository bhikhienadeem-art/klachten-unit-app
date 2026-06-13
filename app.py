import streamlit as st
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- LOGIN & ROL-BEHEER ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
    st.session_state.rol = None

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    gebruiker = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if gebruiker == "admin" and wachtwoord == "admin123":
            st.session_state.logged_in = True
            st.session_state.rol = 'admin'
            st.rerun()

# --- DASHBOARD & ADMIN BEHEER ---
if st.session_state.logged_in:
    if st.session_state.rol == 'admin':
        tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Medewerker Beheer"])
        
        with tab1:
            st.title("Dashboard")
            st.write("Overzicht van binnengekomen klachten.")
            
        with tab2:
            st.subheader("Nieuwe Medewerker Toevoegen")
            with st.form("add_user_form"):
                naam = st.text_input("Naam medewerker")
                pw = st.text_input("Wachtwoord", type="password")
                if st.form_submit_button("Account Aanmaken"):
                    # Hier logica voor toevoegen aan Supabase
                    st.success(f"Medewerker {naam} toegevoegd!")

            st.subheader("Bestaande Medewerkers")
            # Voorbeeldlijst - hier zou je een database call doen
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write("Naam Medewerker (Rol)")
            col2.button("Maak Admin", key="btn1")
            col3.button("Verwijder", key="btn2")
    else:
        st.title("Dashboard (Medewerker)")
else:
    # --- PUBLIEK FORMULIER ---
    st.title("Klacht indienen")
    with st.form("klacht_form"):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving van de klacht")
        if st.form_submit_button("Verstuur"):
            st.write("Klacht verzonden!")
