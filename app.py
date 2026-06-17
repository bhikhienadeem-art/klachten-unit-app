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

# --- MAIL FUNCTIE MET BIJLAGE ---
def stuur_mail(ontvanger, onderwerp, html_inhoud, bestand=None):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "Klachtenunit Wanica <klachtenunitwanicacentrum@gmail.com>"
        msg['To'] = ontvanger
        msg.add_alternative(html_inhoud, subtype='html')
        
        if bestand is not None:
            bestand.seek(0)
            msg.add_attachment(
                bestand.read(),
                maintype='application',
                subtype='octet-stream',
                filename=bestand.name
            )
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail fout: {e}")
        return False

# --- SESSIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- SIDEBAR (INLOGGEN) ---
with st.sidebar:
    if not st.session_state.logged_in:
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            # Controleer via database
            check = supabase.table("medewerkers").select("*").eq("gebruikersnaam", user).eq("wachtwoord", pw).execute().data
            if check:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Ongeldige gegevens")
    else:
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- HOOFDPROGRAMMA ---
if not st.session_state.logged_in:
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Volledige naam")
        id_nr = col1.text_input("ID Nummer")
        telefoon = col1.text_input("Telefoon/WhatsApp")
        woonadres = col1.text_input("Woonadres")
        email = col2.text_input("E-mailadres")
        soort = col2.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        uploaded_file = st.file_uploader("Bijlage (optioneel)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if st.form_submit_button("Verstuur Klacht"):
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            
            # Database
            supabase.table("klachten").insert({
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr
            }).execute()
            
            # MAIL BURGER
            mail_burger = f"""<html><body style="font-family:sans-serif; color:#333;">
                <h2 style="color:#004a99;">Bevestiging van uw klacht</h2>
                <p>Beste {naam},</p>
                <p>Hartelijk dank voor het indienen van uw klacht bij het Commissariaat Wanica Centrum. Wij hebben uw melding (Referentie: <b>{ticket_nr}</b>) in goede orde ontvangen.</p>
                <p>Ons team zal uw klacht zo spoedig mogelijk in behandeling nemen. Wij houden u via de e-mail op de hoogte van de voortgang.</p>
                <p>Met vriendelijke groet,<br>Klachtenunit Wanica Centrum</p>
                </body></html>"""
            stuur_mail(email, f"Bevestiging klacht: {ticket_nr}", mail_burger)
            
            # MAIL MEDEWERKER
            mail_med = f"""<html><body style="font-family:sans-serif;">
                <h2 style="color:#d32f2f;">Nieuwe klacht binnengekomen: {ticket_nr}</h2>
                <p>Beste collega, er is een nieuwe klacht gemeld. In de bijlage vindt u eventuele bewijsstukken.</p>
                <table border="1" cellpadding="5" style="border-collapse:collapse;">
                    <tr><td><b>Naam:</b></td><td>{naam}</td></tr>
                    <tr><td><b>Soort:</b></td><td>{soort}</td></tr>
                    <tr><td><b>Omschrijving:</b></td><td>{omschrijving}</td></tr>
                </table>
                </body></html>"""
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {ticket_nr}", mail_med, bestand=uploaded_file)
            
            st.success("✅ Klacht succesvol verzonden!")
else:
    st.write("Welkom beheerder. U bent ingelogd.")
