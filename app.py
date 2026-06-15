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

# 2. E-mail functie met professionele opmaak
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

# --- UI LOGICA ---
# [Blijf hier je bestaande dashboard/rapporten/instellingen logica behouden]

# --- BURGERS PAGINA (Formulier) ---
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    naam = col1.text_input("👤 Volledige naam")
    email = col2.text_input("📧 E-mailadres")
    id_nr = col1.text_input("🆔 ID Nummer")
    telefoon = col1.text_input("📞 Telefoon/WhatsApp")
    woonadres = col1.text_input("🏠 Woonadres")
    soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
    omschrijving = st.text_area("📝 Omschrijving")
    
    if st.form_submit_button("Verstuur Klacht"):
        ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        
        # Sla op in database
        data = {
            "volledige_naam": naam, "email": email, "id_nummer": id_nr,
            "telefoon_whatsapp": telefoon, "adres": woonadres, 
            "klachtensoort": soort, "omschrijving": omschrijving, 
            "status": "Nieuw", "ticket_id": ticket_nr
        }
        supabase.table("klachten").insert(data).execute()

        # 1. Bericht voor de Burger
        mail_burger = f"""
        <h2>Bevestiging Klachtmelding</h2>
        <p>Beste {naam},</p>
        <p>Wij hebben uw klacht goed ontvangen bij het Commissariaat Wanica Centrum.</p>
        <p><b>Ticketnummer:</b> {ticket_nr}<br>
        <b>Soort klacht:</b> {soort}</p>
        <p>Wij zullen uw melding zo spoedig mogelijk in behandeling nemen.</p>
        """
        stuur_mail(email, f"Uw Klacht: {ticket_nr}", mail_burger)

        # 2. Bericht voor de Medewerker (Compleet dossier)
        mail_medewerker = f"""
        <h2>Nieuwe klacht binnengekomen: {ticket_nr}</h2>
        <table border="1">
            <tr><td><b>Naam:</b></td><td>{naam}</td></tr>
            <tr><td><b>ID Nummer:</b></td><td>{id_nr}</td></tr>
            <tr><td><b>Telefoon:</b></td><td>{telefoon}</td></tr>
            <tr><td><b>Adres:</b></td><td>{woonadres}</td></tr>
            <tr><td><b>Soort:</b></td><td>{soort}</td></tr>
            <tr><td><b>Omschrijving:</b></td><td>{omschrijving}</td></tr>
        </table>
        <p>Log in op het dashboard om de status te beheren.</p>
        """
        stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {ticket_nr}", mail_medewerker)
        
        st.success(f"✅ Klacht verzonden! Uw ticketnummer is {ticket_nr}")
