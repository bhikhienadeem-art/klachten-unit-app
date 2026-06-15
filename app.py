import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- PAGINA CONFIGURATIE ---
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stForm"] { background-color: #e3f2fd; border: 2px solid #004a99; padding: 25px; border-radius: 10px; }
    .stTextInput input, .stTextArea textarea { color: black !important; }
    div.stButton > button { background-color: #004a99; color: white !important; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER MET GEGEVENS ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-style: italic;">Welkom op de officiële klachtenpagina.</div>
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
        gebruiker = st.text_input("Gebruikersnaam", key="user_in")
        wachtwoord = st.text_input("Wachtwoord", type="password", key="pass_in")
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
    klachten = supabase.table("klachten").select("*").execute().data
    for k in klachten:
        with st.expander(f"👤 {k.get('volledige_naam')} | Status: {k.get('status', 'Nieuw')}"):
            # ... (jouw bestaande kolommen en info)
            if st.button("🗑️ Klacht verwijderen", key=f"del_{k['id']}"):
                supabase.table("klachten").delete().eq("id", k['id']).execute()
                st.rerun()

    elif st.session_state.menu == "Instellingen":
    st.title("⚙️ Instellingen - Beheer")
    
    # 1. Medewerker toevoegen
    with st.expander("➕ Medewerker toevoegen"):
        with st.form("add_user"):
            u = st.text_input("Gebruikersnaam")
            p = st.text_input("Wachtwoord", type="password")
            if st.form_submit_button("Toevoegen"):
                supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p}).execute()
                st.success("Toegevoegd!")
    
    # 2. Medewerkers verwijderen
    st.subheader("👥 Medewerkers beheren")
    medewerkers = supabase.table("medewerkers").select("*").execute().data
    for m in medewerkers:
        col1, col2 = st.columns([3, 1])
        col1.write(f"Gebruiker: {m['gebruikersnaam']}")
        if col2.button("❌", key=f"del_user_{m['id']}"):
            supabase.table("medewerkers").delete().eq("id", m['id']).execute()
            st.rerun()

# --- FORMULIER ---
st.divider()
st.subheader("📝 Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    naam = c1.text_input("👤 Volledige naam")
    id_nr = c1.text_input("🆔 ID Nummer")
    telefoon = c1.text_input("📞 Telefoon/WhatsApp")
    woonadres = c1.text_input("🏠 Woonadres")
    email = c2.text_input("📧 E-mailadres")
    soort = c2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
    omschrijving = st.text_area("📝 Omschrijving")
    
    st.divider()
    wil_afspraak = st.checkbox("📅 Ik wil indien nodig een afspraak maken")
    if wil_afspraak:
        ca1, ca2 = st.columns(2)
        afspraak_datum = ca1.date_input("Kies datum")
        tijden = [f"{h:02d}:{m:02d}" for h in range(8, 14) for m in [0, 15, 30, 45]] + ["14:00"]
        afspraak_tijd = ca2.selectbox("Kies tijdstip", tijden)
    else:
        afspraak_datum, afspraak_tijd = None, None
        
    if st.form_submit_button("Verstuur klacht"):
        supabase.table("klachten").insert({
            "volledige_naam": naam, "id_nummer": id_nr, "telefoon": telefoon, "adres": woonadres, 
            "email": email, "klachtensoort": soort, "omschrijving": omschrijving, 
            "status": "Nieuw", "afspraak_datum": str(afspraak_datum) if wil_afspraak else None,
            "afspraak_tijd": str(afspraak_tijd) if wil_afspraak else None
        }).execute()
        st.success("✅ Uw klacht is succesvol verzonden!")
