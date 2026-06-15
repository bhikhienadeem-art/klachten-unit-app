import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    
    /* Header met gouden rand */
    .header-bar { 
        background-color: #004a99; 
        color: white; 
        padding: 25px; 
        text-align: center; 
        border: 5px solid #ffcc00; 
        border-radius: 10px; 
        margin-bottom: 30px; 
    }
    
    /* Sidebar blauw en tekst wit */
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Formulier blauwe look */
    [data-testid="stForm"] {
        background-color: #e3f2fd;
        border: 2px solid #004a99;
        padding: 25px;
        border-radius: 10px;
    }
    
    /* Zorg dat tekst IN invoervelden leesbaar is */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        color: black !important; /* Tekstkleur in velden zwart maken voor contrast */
        background-color: white !important;
    }
    
    div.stButton > button { background-color: #004a99; color: white !important; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-style: italic;">Welkom op de officiële klachtenpagina. Uw stem wordt gehoord.</div>
        <div style="font-size: 0.9em; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
            📍 Tawajarieweg 20 | 📞 (+597) 366660 | ✉️ klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("👤 Gebruikersnaam", key="user_in")
        wachtwoord = st.text_input("🔒 Wachtwoord", type="password", key="pass_in")
        if st.button("Inloggen", key="login_btn"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        # Let op: Zorg dat je Supabase tabel 'klachten' bestaat
        try:
            klachten = supabase.table("klachten").select("*").execute().data
            for k in klachten:
                with st.expander(f"Klacht ID: {k.get('id', 'N/A')}"):
                    st.write(f"**Naam:** {k.get('volledige_naam')}")
                    st.write(f"**Omschrijving:** {k.get('omschrijving')}")
                    if st.button("Opslaan", key=f"save_{k['id']}"):
                        st.success("Opgeslagen!")
        except Exception as e:
            st.error("Kon klachten niet ophalen.")

# --- FORMULIER ---
st.divider()
st.subheader("📝 Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("👤 Volledige naam")
        id_nr = st.text_input("🆔 ID Nummer")
        tel = st.text_input("📞 Telefoon/WhatsApp")
        woonadres = st.text_input("🏠 Woonadres")
    with col2:
        email = st.text_input("📧 E-mailadres")
        soort = st.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        file = st.file_uploader("📎 Voeg bestand toe")
        
    omschrijving = st.text_area("📝 Omschrijving of voorstel")
    
    if st.form_submit_button("Verstuur klacht"):
        st.success("✅ Uw klacht is succesvol verzonden!")
