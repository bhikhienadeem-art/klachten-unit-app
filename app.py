import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid
import smtplib
from email.message import EmailMessage

# 1. Configuratie
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- E-MAIL FUNCTIE ---
def stuur_mail(ontvanger, onderwerp, inhoud):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "klachtenunitwanicacentrum@gmail.com"
        msg['To'] = ontvanger
        msg.set_content(inhoud)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except: return False

# --- SESSIE & UI ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# CSS & Header
st.markdown("<style>.stApp { background-color: #e3f2fd; } .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border-radius: 10px; }</style>", unsafe_allow_html=True)
col_logo, col_text = st.columns([1, 4])
with col_logo: st.image("orgineel logo Centrum.png", width=150)
with col_text: st.markdown("<div class='header-bar'><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>", unsafe_allow_html=True)

# --- SIDEBAR (Medewerkers) ---
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
    klachten = supabase.table("klachten").select("*").execute().data
    
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            status = k.get('status', 'Nieuw')
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | {k.get('klachtensoort', '-')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                # Veilige status update
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                huidige_idx = status_opties.index(status) if status in status_opties else 0
                nieuwe_status = st.selectbox("Status", status_opties, index=huidige_idx, key=f"s_{k['id']}")
                if st.button("Opslaan", key=f"b_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        if klachten: st.dataframe(pd.DataFrame(klachten))

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")

else:
    # --- BURGERS PAGINA ---
    tab1, tab2 = st.tabs(["📝 Klacht indienen", "🗓️ Afspraak maken"])
    
    with tab1:
        with st.form("klacht_form", clear_on_submit=True):
            naam = st.text_input("Volledige naam")
            email = st.text_input("E-mailadres")
            soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
            omschrijving = st.text_area("Omschrijving")
            if st.form_submit_button("Verstuur Klacht"):
                ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
                supabase.table("klachten").insert({
                    "volledige_naam": naam, "email": email, "klachtensoort": soort, 
                    "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr
                }).execute()
                stuur_mail(email, "Bevestiging", f"Uw klacht {ticket_nr} is ontvangen.")
                st.success("✅ Klacht verzonden!")

    with tab2:
        with st.form("afspraak_form", clear_on_submit=True):
            naam_af = st.text_input("Uw Naam")
            datum = st.date_input("Datum")
            if st.form_submit_button("Afspraak Bevestigen"):
                st.success("✅ Afspraak bevestigd!")
