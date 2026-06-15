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
        return False

# --- CSS & HEADER ---
st.markdown("<style>.stApp { background-color: #e3f2fd; } .header-bar { background-color: #004a99; color: white; padding: 20px; border-radius: 10px; text-align: center; }</style>", unsafe_allow_html=True)
col_logo, col_text = st.columns([1, 4])
with col_logo: st.image("orgineel logo Centrum.png", width=150)
with col_text: st.markdown("<div class='header-bar'><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>", unsafe_allow_html=True)

# --- SIDEBAR & AUTH ---
with st.sidebar:
    st.header("🔑 Medewerkers")
    if not st.session_state.logged_in:
        u = st.text_input("Gebruiker")
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if u == "admin" and p == "admin123":
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
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], index=["Nieuw", "In behandeling", "Afgehandeld"].index(k.get('status', 'Nieuw')), key=f"s_{k['id']}")
                if st.button("Opslaan", key=f"b_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()
    
    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        if klachten: st.dataframe(pd.DataFrame(klachten))
            
    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        st.info("Beheer hier medewerkers en systeeminstellingen.")

else:
    # --- BURGERS PAGINA ---
    with st.form("klacht_form", clear_on_submit=True):
        st.subheader("📝 Klacht indienen")
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
            mail_burger = f"<h2>Bevestiging {ticket_nr}</h2><p>Beste {naam}, uw klacht is ontvangen.</p>"
            mail_medewerker = f"<h2>Nieuwe klacht</h2><p>Ticket: {ticket_nr}<br>Naam: {naam}<br>Omschrijving: {omschrijving}</p>"
            stuur_mail(email, "Klacht Ontvangen", mail_burger)
            stuur_mail("klachtenunitwanicacentrum@gmail.com", "Nieuwe Klacht", mail_medewerker)
            st.success("✅ Klacht verzonden!")
