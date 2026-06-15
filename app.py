import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    .stTextInput input { color: black !important; }
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
            <div style="font-size: 0.9em; margin-top: 15px;">
                📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam", key="user_in")
        wachtwoord = st.text_input("Wachtwoord", type="password", key="pass_in")
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
    # [Dashboard, Rapporten, Instellingen secties blijven ongewijzigd...]
    # (Zorg dat je deze code hier behoudt zoals in je vorige bestand)
    pass 
else:
    # --- BURGERS PAGINA ---
    st.subheader("Welkom bij de Klachtenunit")
    menu_keuze = st.radio("Maak een keuze:", ["📝 Klacht indienen", "🗓️ Afspraak maken"], horizontal=True)

    if menu_keuze == "📝 Klacht indienen":
        with st.form("klacht_form", clear_on_submit=True):
            # [Jouw bestaande formulier code]
            col1, col2 = st.columns(2)
            naam = col1.text_input("👤 Volledige naam")
            soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
            omschrijving = st.text_area("📝 Omschrijving")
            if st.form_submit_button("Verstuur Klacht"):
                st.success("✅ Klacht verzonden!")

    elif menu_keuze == "🗓️ Afspraak maken":
        st.subheader("🗓️ Afspraak maken (Ma-Vr: 08:00 - 14:00)")
        with st.form("afspraak_form", clear_on_submit=True):
            naam_afspraak = st.text_input("Uw Naam")
            datum = st.date_input("Kies datum")
            
            # Genereer tijdslots (08:00 tot 14:00, per 15 min)
            tijdstippen = [t.strftime("%H:%M") for t in pd.date_range("08:00", "14:00", freq="15min")]
            tijd = st.selectbox("Selecteer tijdstip (15 min per afspraak)", tijdstippen)
            reden = st.text_area("Reden van bezoek")
            
            if st.form_submit_button("Afspraak Bevestigen"):
                try:
                    supabase.table("afspraken").insert({
                        "naam": naam_afspraak,
                        "datum": str(datum),
                        "tijdstip": tijd,
                        "reden": reden
                    }).execute()
                    st.success(f"✅ Afspraak bevestigd op {datum} om {tijd}!")
                except Exception as e:
                    st.error(f"Fout bij opslaan: {e}")
