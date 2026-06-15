import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER (Altijd zichtbaar) ---
col_l, col_r = st.columns([1, 4])
with col_l:
    st.image("orgineel logo Centrum.png", width=150)
with col_r:
    st.title("Klachtenunit Commissariaat Wanica Centrum")

# --- LOGICA ---
if st.session_state.logged_in:
    # --- DASHBOARD VOOR MEDEWERKERS ---
    st.subheader("📊 Dashboard")
    # Hier kun je weer je metrics en klachtenlijst toevoegen
    if st.button("Uitloggen"):
        st.session_state.logged_in = False
        st.rerun()
else:
    # --- FORMULIER VOOR BURGERS (ALTIJD ZICHTBAAR) ---
    st.subheader("📝 Klacht indienen of Afspraak maken")
    
    # Jouw formulier code komt hier
    with st.form("publiek_form"):
        naam = st.text_input("Volledige naam")
        if st.form_submit_button("Verstuur"):
            st.success("Verzonden!")

# --- SIDEBAR INLOG ---
with st.sidebar:
    st.header("🔑 Medewerkers")
    u = st.text_input("Gebruiker")
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if u == "admin" and p == "admin123":
            st.session_state.logged_in = True
            st.rerun()
