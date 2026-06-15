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

# 2. Initialisatie
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# 3. E-mail functie
def stuur_mail(ontvanger, onderwerp, inhoud):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "klachtenunitwanicacentrum@gmail.com"
        msg['To'] = ontvanger
        msg.set_content(inhoud)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            # Wachtwoord zonder spaties: nbngichzpmlgzglc
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        return False

# --- LOGICA ---
if st.session_state.logged_in:
    # Sidebar voor medewerkers
    with st.sidebar:
        st.title("Menu")
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

    klachten = supabase.table("klachten").select("*").execute().data

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | Ticket: {k.get('ticket_id', 'N/A')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                # Status update
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
    st.title("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Volledige naam")
        email = col2.text_input("E-mailadres")
        soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        
        if st.form_submit_button("Verstuur Klacht"):
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            data = {"volledige_naam": naam, "email": email, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr}
            supabase.table("klachten").insert(data).execute()
            
            # Mails versturen
            stuur_mail(email, "Bevestiging Klacht", f"Beste {naam}, uw klacht {ticket_nr} is ontvangen.")
            stuur_mail("klachtenunitwanicacentrum@gmail.com", "Nieuwe Klacht", f"Nieuwe klacht van {naam}: {omschrijving}")
            
            st.success("✅ Klacht verzonden!")

    # Inlog knop voor medewerkers
    if st.checkbox("Medewerkers inloggen"):
        u = st.text_input("Gebruikersnaam")
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.rerun()
