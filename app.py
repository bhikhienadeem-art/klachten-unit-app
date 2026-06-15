import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid # Nodig voor ticket_id

# 1. MOET ALTIJD ALS EERSTE
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_html=True)

# --- HEADER ---
col_logo, col_text = st.columns([1, 4]) 
with col_logo:
    st.image("orgineel logo Centrum.png", width=150)
with col_text:
    st.markdown("""
        <div class="header-bar">
            <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
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

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    # Hier komt je dashboard code (zoals je al had)
    st.title(f"📊 {st.session_state.menu}")
    # ... (rest van je dashboard logica)
else:
    # --- BURGERS PAGINA ---
    st.subheader("📝 Klacht indienen")
    
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("👤 Volledige naam")
        id_nr = col1.text_input("🆔 ID Nummer")
        telefoon = col1.text_input("📞 Telefoon/WhatsApp nummer")
        woonadres = col1.text_input("🏠 Woonadres")
        email = col2.text_input("📧 E-mailadres")
        soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("📝 Omschrijving")
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if st.form_submit_button("Verstuur Klacht"):
            # Ticket ID genereren
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            
            try:
                data = {
                    "volledige_naam": naam,
                    "id_nummer": id_nr,
                    "telefoon_whatsapp": telefoon,
                    "adres": woonadres,
                    "email": email,
                    "klachtensoort": soort,
                    "omschrijving": omschrijving,
                    "status": "Nieuw",
                    "ticket_id": ticket_nr # Ticket toegevoegd
                }
                supabase.table("klachten").insert(data).execute()
                st.success(f"✅ Klacht verzonden! Uw ticketnummer is: {ticket_nr}")
            except Exception as e:
                st.error(f"Fout bij verzenden: {e}")

    st.markdown("---") 

    st.subheader("🗓️ Indien nodig afspraak maken")
    with st.form("afspraak_form", clear_on_submit=True):
        naam_af = st.text_input("Uw Naam voor afspraak")
        datum = st.date_input("Datum")
        tijd = st.selectbox("Tijdstip", ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00"])
        
        if st.form_submit_button("Afspraak Bevestigen"):
            st.success(f"✅ Afspraak op {datum} om {tijd} bevestigd!")
