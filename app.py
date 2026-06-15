import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid 

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
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_text = st.columns([1, 4]) 
with col_logo:
    st.image("orgineel logo Centrum.png", width=150)
with col_text:
    st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

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
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        
        # Data ophalen
        klachten = supabase.table("klachten").select("*").execute().data
        
        if klachten:
            # --- KLACHTEN LIJST MET PRIORITEIT ---
            for k in klachten:
                status = k.get('status', 'Nieuw')
                soort = k.get('klachtensoort', 'Anders')
                
                # Prioriteit bepalen
                if soort == "Wateroverlast": prio_label = "🔴 HOOG"
                elif soort == "Wegen": prio_label = "🟠 MEDIUM"
                else: prio_label = "🟢 LAAG"
                    
                with st.expander(f"{prio_label} | 👤 {k.get('volledige_naam', 'Anoniem')} | 📋 {soort} | Status: {status}"):
                    col_a, col_b = st.columns(2)
                    col_a.write(f"**🆔 Ticket:** {k.get('ticket_id', '-')}")
                    col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}")
                    col_a.write(f"**📞 Tel/WA:** {k.get('telefoon_whatsapp', '-')}")
                    col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                    
                    st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                    
                    st.markdown("---")
                    status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                    huidige_idx = status_opties.index(status) if status in status_opties else 0
                    nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=huidige_idx, key=f"status_{k['id']}")
                    
                    if st.button("💾 Opslaan", key=f"save_{k['id']}"):
                        supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                        st.rerun()
        else:
            st.info("Geen klachten gevonden.")

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
        
        if st.form_submit_button("Verstuur Klacht"):
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            data = {
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr
            }
            supabase.table("klachten").insert(data).execute()
            st.success(f"✅ Klacht verzonden! Uw ticketnummer: {ticket_nr}")

    st.markdown("---")
    st.subheader("🗓️ Afspraak maken")
    with st.form("afspraak_form", clear_on_submit=True):
        naam_af = st.text_input("Uw Naam")
        datum = st.date_input("Datum")
        if st.form_submit_button("Afspraak Bevestigen"):
            st.success("✅ Afspraak bevestigd!")
