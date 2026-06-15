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

# 2. Sessie beheer
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# E-mail functie met foutafhandeling
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
    except Exception as e:
        st.error(f"E-mail fout bij {ontvanger}: {e}")
        return False

# 3. Layout & Header
st.markdown("<style>.stApp { background-color: #e3f2fd; }</style>", unsafe_allow_html=True)
st.header("Klachtenunit Commissariaat Wanica Centrum")

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
    klachten = supabase.table("klachten").select("*").execute().data
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            with st.expander(f"👤 {k.get('volledige_naam')} | Status: {k.get('status')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving')}")
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], key=f"s_{k['id']}")
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
                data = {"volledige_naam": naam, "email": email, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr}
                supabase.table("klachten").insert(data).execute()
                
                # Versturen en feedback in app
                m1 = stuur_mail(email, f"Bevestiging {ticket_nr}", "Uw klacht is ontvangen.")
                m2 = stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {ticket_nr}", f"Naam: {naam}\nSoort: {soort}")
                
                if m1 and m2:
                    st.success(f"✅ Klacht verzonden! Bevestiging is naar {email} gestuurd.")
                else:
                    st.warning("⚠️ Klacht is opgeslagen, maar e-mail kon niet worden verzonden.")

    with tab2:
        with st.form("afspraak_form", clear_on_submit=True):
            st.text_input("Uw Naam")
            if st.form_submit_button("Bevestig"):
                st.success("✅ Afspraak bevestigd!")
