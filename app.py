import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid 

# 1. Configuratie
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    # Dashboard, Rapporten en Instellingen logica
    klachten = supabase.table("klachten").select("*").execute().data
    
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            status = k.get('status', 'Nieuw')
            status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
            
            # Voorkom ValueError door te checken of status bestaat
            huidige_idx = status_opties.index(status) if status in status_opties else 0
            
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | Status: {status}"):
                nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=huidige_idx, key=f"s_{k['id']}")
                if st.button("Opslaan", key=f"b_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()

elif st.session_state.menu == "Rapporten":
    st.title("📈 Rapporten")
    # ... (jouw rapporten code)

else:
    # --- BURGERS PAGINA ---
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        # ... (je formulier velden)
        if st.form_submit_button("Verstuur"):
            st.success("Verzonden!")
