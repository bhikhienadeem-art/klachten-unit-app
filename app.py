import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid
import smtplib
from email.message import EmailMessage

# 1. MOET ALTIJD ALS EERSTE
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CONFIGURATIE ---
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
    st.markdown("""
        <div class="header-bar">
            <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
            <div style="font-size: 0.9em; margin-top: 15px;">
                📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
            </div>
        </div>
    """, unsafe_allow_html=True)

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
    df_dash = pd.DataFrame(klachten)

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        if not df_dash.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal Klachten", len(df_dash))
            c2.metric("Nieuw", len(df_dash[df_dash['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df_dash[df_dash['status'] == 'Afgehandeld']))
            st.markdown("---")
        
        for k in klachten:
            status = k.get('status', 'Nieuw')
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | 📋 {k.get('klachtensoort', '-')} | Status: {status}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🆔 ID:** {k.get('id_nummer', '-')}")
                col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}")
                col_a.write(f"**📞 Tel/WA:** {k.get('telefoon_whatsapp', '-')}")
                col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                if k.get('bijlage_url'):
                    col_b.markdown(f"**📎 Bijlage:** [Bekijk bestand]({k['bijlage_url']})")
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                st.markdown("---")
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                huidige_idx = status_opties.index(status) if status in status_opties else 0
                nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=huidige_idx, key=f"status_{k['id']}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                if st.button("💾 Status & Notitie Opslaan", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.success("Opgeslagen!")
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        if not df_dash.empty:
            st.download_button("📥 Download CSV", data=df_dash.to_csv(index=False), file_name='klachten.csv')
            st.plotly_chart(px.pie(df_dash, names='klachtensoort'))
            st.dataframe(df_dash)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Gebruikersbeheer")
        with st.expander("➕ Nieuwe medewerker toevoegen"):
            with st.form("add_user_form", clear_on_submit=True):
                u = st.text_input("Gebruikersnaam")
                p = st.text_input("Wachtwoord", type="password")
                r = st.selectbox("Rol", ["Admin", "Medewerker", "Viewer"])
                if st.form_submit_button("Opslaan"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p, "rol": r}).execute()
                    st.rerun()
        st.subheader("👥 Huidige medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        if medewerkers:
            st.table(pd.DataFrame(medewerkers)[['gebruikersnaam', 'rol']])

else:
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
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'jpeg', 'pdf'])
        
       if st.form_submit_button("Verstuur Klacht"):
            # 1. Ticketnummer en database opslag (zoals je al hebt)
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            
            # 2. De inhoud voor de medewerker (inclusief alle data)
            mail_medewerker = f"""
            <h2>Nieuwe klacht binnengekomen: {ticket_nr}</h2>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr><td><b>Naam:</b></td><td>{naam}</td></tr>
                <tr><td><b>ID Nummer:</b></td><td>{id_nr}</td></tr>
                <tr><td><b>Telefoon:</b></td><td>{telefoon}</td></tr>
                <tr><td><b>Adres:</b></td><td>{woonadres}</td></tr>
                <tr><td><b>Soort:</b></td><td>{soort}</td></tr>
                <tr><td><b>Omschrijving:</b></td><td>{omschrijving}</td></tr>
                <tr><td><b>Bijlage Link:</b></td><td>{uploaded_file.name if uploaded_file else 'Geen bijlage'}</td></tr>
            </table>
            <p>Log in op het dashboard om de klacht te beheren.</p>
            """
            
            # 3. Verstuur de mail
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {ticket_nr}", mail_medewerker)
            
            # 4. Bevestiging aan burger
            stuur_mail(email, "Bevestiging Klacht", f"Beste {naam}, uw klacht {ticket_nr} is ontvangen.")
            
            st.success("✅ Klacht verzonden!")

    st.markdown("---")
    st.subheader("🗓️ Indien nodig afspraak maken")
    with st.form("afspraak_form", clear_on_submit=True):
        naam_af = st.text_input("Uw Naam voor afspraak")
        datum = st.date_input("Datum")
        tijd = st.selectbox("Tijdstip", ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00"])
        if st.form_submit_button("Afspraak Bevestigen"):
            st.success(f"✅ Afspraak op {datum} om {tijd} bevestigd!")
