import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid
import smtplib
from email.message import EmailMessage

# --- CONFIGURATIE ---
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# --- E-MAIL FUNCTIE ---
def stuur_mail(ontvanger, onderwerp, html_inhoud):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "klachtenunitwanicacentrum@gmail.com"
        msg['To'] = ontvanger
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(html_inhoud)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Fout bij mail: {e}")
        return False

# --- LOGICA ---
if st.session_state.logged_in:
    # Sidebar voor medewerkers
    with st.sidebar:
        st.title("Menu")
        st.session_state.menu = st.radio("Ga naar:", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

    klachten = supabase.table("klachten").select("*").execute().data

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | Ticket: {k.get('ticket_id')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], 
                                           index=["Nieuw", "In behandeling", "Afgehandeld"].index(k.get('status', 'Nieuw')), 
                                           key=f"s_{k['id']}")
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
    st.title("Klachtenunit Wanica")
    with st.form("klacht_form", clear_on_submit=True):
        naam = st.text_input("Volledige naam")
        email = st.text_input("E-mailadres")
        soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        
        if st.form_submit_button("Verstuur Klacht"):
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            data = {"volledige_naam": naam, "email": email, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr}
            supabase.table("klachten").insert(data).execute()
            
            # Professionele e-mails
            mail_burger = f"<h2>Bevestiging van uw klacht</h2><p>Beste {naam}, uw klacht {ticket_nr} is ontvangen.</p>"
            mail_medewerker = f"<h2>Nieuwe klacht</h2><p>Ticket: {ticket_nr}<br>Naam: {naam}<br>Omschrijving: {omschrijving}</p>"
            
            stuur_mail(email, "Bevestiging Klacht", mail_burger)
            stuur_mail("klachtenunitwanicacentrum@gmail.com", "Nieuwe Klacht", mail_medewerker)
            
            st.success("✅ Klacht verzonden! Controleer eventueel uw spamfolder.")

    # Inlog knop voor medewerkers onderaan
    with st.expander("🔑 Medewerkers inlog"):
        u = st.text_input("Gebruikersnaam")
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.rerun()
