import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# 1. Configuratie & Setup (Moet als eerste)
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialisatie
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# Header
col_logo, col_text = st.columns([1, 4]) 
with col_logo:
    st.image("orgineel logo Centrum.png", width=150)
with col_text:
    st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# 2. Sidebar (Inloggen)
with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# 3. Pagina Logica
if st.session_state.logged_in:
    # --- MEDEWERKERS PAGINA'S ---
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        klachten = supabase.table("klachten").select("*").execute().data
        if klachten:
            df = pd.DataFrame(klachten)
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal", len(df))
            c2.metric("Nieuw", len(df[df['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df[df['status'] == 'Afgehandeld']))
            for k in klachten:
                with st.expander(f"{k.get('volledige_naam')} | Status: {k.get('status')}"):
                    st.write(f"Omschrijving: {k.get('omschrijving')}")
    
    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        st.write("Beheer hier je team.")
        
    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        st.write("Hier komt je data-analyse.")

else:
    # --- BURGERS PAGINA (Formulier + Afspraken) ---
    st.subheader("Welkom - Wat wilt u doen?")
    tab1, tab2 = st.tabs(["📝 Klacht indienen", "🗓️ Afspraak maken"])
    
    with tab1:
        with st.form("klacht_form"):
            naam = st.text_input("Naam")
            omschrijving = st.text_area("Omschrijving")
            if st.form_submit_button("Verstuur Klacht"):
                supabase.table("klachten").insert({"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
                st.success("✅ Klacht verzonden!")
                
    with tab2:
        with st.form("afspraak_form"):
            naam_af = st.text_input("Uw Naam")
            datum = st.date_input("Datum")
            slots = [t.strftime("%H:%M") for t in pd.date_range("08:00", "14:00", freq="15min")]
            tijd = st.selectbox("Tijdstip", slots)
            if st.form_submit_button("Afspraak Bevestigen"):
                supabase.table("afspraken").insert({"naam": naam_af, "datum": str(datum), "tijdstip": tijd}).execute()
                st.success(f"✅ Afspraak op {datum} om {tijd}!")
