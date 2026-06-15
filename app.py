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
    /* Achtergrond pagina */
    .stApp { background-color: #f0f4f8; }
    
    /* Sidebar blauw */
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Formulier styling */
    [data-testid="stForm"] {
        background-color: #e3f2fd;
        border: 2px solid #004a99;
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Blauwe invulvelden (invoervelden krijgen een blauwe rand) */
    div[data-testid="stTextInput"] > div > div > input { border: 2px solid #004a99; }
    
    /* Header bar */
    .header-bar { background-color: #004a99; color: white; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

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
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            # Unieke key per expander/knop voorkomt de DuplicateElementKey fout
            with st.expander(f"Klacht van: {k.get('volledige_naam')}"):
                st.write(f"Omschrijving: {k.get('omschrijving')}")
                if st.button("Opslaan status", key=f"save_{k['id']}"):
                    st.success("Opgeslagen!")

# --- FORMULIER ---
st.divider()
st.subheader("📋 Klacht indienen")
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
        
    omschrijving = st.text_area("📝 Omschrijving")
    
    if st.form_submit_button("Verstuur klacht"):
        # Hier je supabase insert logica
        st.success("✅ Klacht succesvol verzonden!")
