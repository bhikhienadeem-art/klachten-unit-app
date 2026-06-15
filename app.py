import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER ---
col_l, col_r = st.columns([1, 4])
with col_l:
    st.image("orgineel logo Centrum.png", width=150)
with col_r:
    st.title("Klachtenunit Commissariaat Wanica Centrum")

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    # --- DASHBOARD VOOR MEDEWERKERS ---
    st.subheader("📊 Medewerkers Dashboard")
    if st.button("Uitloggen"):
        st.session_state.logged_in = False
        st.rerun()
else:
    # --- FORMULIER VOOR BURGERS ---
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
        
        if st.form_submit_button("Verstuur"):
            st.success("✅ Klacht verzonden!")

# --- SIDEBAR INLOG ---
with st.sidebar:
    st.header("🔑 Medewerkers")
    u = st.text_input("Gebruikersnaam")
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if u == "admin" and p == "admin123":
            st.session_state.logged_in = True
            st.rerun()
