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

# --- PROFESSIONELE MAIL FUNCTIE ---
def stuur_mail_professioneel(ontvanger, onderwerp, html_inhoud):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "Klachtenunit Wanica <klachtenunitwanicacentrum@gmail.com>"
        msg['To'] = ontvanger
        msg.add_alternative(html_inhoud, subtype='html')
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Fout bij mailverzending: {e}")
        return False

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border-radius: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_text = st.columns([1, 4])
with col_logo:
    try: st.image("orgineel logo Centrum.png", width=150)
    except: st.write("Logo niet gevonden")
with col_text:
    st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
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

# --- HOOFDPROGRAMMA ---
if st.session_state.logged_in:
    # (Dashboard & Logica hier laten staan zoals voorheen)
    st.write(f"Welkom in het dashboard menu: {st.session_state.menu}")
    # ... (Rest van de admin logica)

else:
    st.subheader("📝 Dien hier uw klacht in")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Volledige naam")
        id_nr = col1.text_input("ID Nummer")
        telefoon = col1.text_input("Telefoon/WhatsApp")
        woonadres = col1.text_input("Woonadres")
        email = col2.text_input("E-mailadres")
        soort = col2.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        uploaded_file = st.file_uploader("Bijlage (optioneel)", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Verstuur Klacht"):
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            
            # Database
            supabase.table("klachten").insert({
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr
            }).execute()
            
            # 1. MAIL NAAR CLIENT
            mail_client = f"""<html><body style="font-family:sans-serif;">
                <h2 style="color:#004a99;">Bevestiging klacht: {ticket_nr}</h2>
                <p>Beste {naam}, hartelijk dank voor uw melding. Wij nemen deze in behandeling.</p>
                </body></html>"""
            stuur_mail_professioneel(email, f"Bevestiging: {ticket_nr}", mail_client)
            
            # 2. MAIL NAAR MEDEWERKER
            mail_medewerker = f"""<html><body style="font-family:sans-serif;">
                <h2 style="color:#d32f2f;">Nieuwe Klacht: {ticket_nr}</h2>
                <table border="1" style="border-collapse:collapse; width:100%;">
                    <tr><td>Naam</td><td>{naam}</td></tr>
                    <tr><td>Soort</td><td>{soort}</td></tr>
                    <tr><td>Omschrijving</td><td>{omschrijving}</td></tr>
                    <tr><td>Bestand</td><td>{uploaded_file.name if uploaded_file else 'Geen'}</td></tr>
                </table>
                </body></html>"""
            stuur_mail_professioneel("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {ticket_nr}", mail_medewerker)
            
            st.success("✅ Uw klacht is verzonden en de bevestigingsmail is onderweg!")
