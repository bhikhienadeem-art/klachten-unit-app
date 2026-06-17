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

# --- MAIL FUNCTIE ---
def stuur_mail(ontvanger, onderwerp, html_inhoud, bestand=None):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "Klachtenunit Wanica <klachtenunitwanicacentrum@gmail.com>"
        msg['To'] = ontvanger
        msg.add_alternative(html_inhoud, subtype='html')
        if bestand:
            bestand.seek(0)
            msg.add_attachment(bestand.read(), maintype='application', subtype='octet-stream', filename=bestand.name)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail fout: {e}")
        return False

# --- CSS & HEADER ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp, [data-testid="stSidebar"] { background-color: #90D5FF; }
    .header-bar { background-color: #003366; color: white; padding: 40px; text-align: center; border: 5px solid #ffcc00; border-radius: 15px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# --- SESSIE & AUTH ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.markdown("## Medewerkers Login")
    if not st.session_state.logged_in:
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            check = supabase.table("medewerkers").select("*").eq("gebruikersnaam", user).eq("wachtwoord", pw).execute().data
            if check:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Ongeldige gegevens")
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten) if klachten else pd.DataFrame()

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        if not df_dash.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal", len(df_dash))
            c2.metric("Nieuw", len(df_dash[df_dash['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df_dash[df_dash['status'] == 'Afgehandeld']))
        
        for k in klachten:
            row_id = k.get('id')
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | 📋 {k.get('klachtensoort', '-')} | Status: {k.get('status', 'Nieuw')}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}"); col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], index=["Nieuw", "In behandeling", "Afgehandeld"].index(k.get('status', 'Nieuw')), key=f"s_{row_id}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"n_{row_id}")
                
                if st.button("💾 Opslaan & Mail", key=f"b_{row_id}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", row_id).execute()
                    stuur_mail(k.get('email'), "Statusupdate", f"Update: {nieuwe_status}")
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        if not df_dash.empty: st.dataframe(df_dash)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        with st.form("add_user_unique", clear_on_submit=True): # Unieke key
            u = st.text_input("Gebruikersnaam"); p = st.text_input("Wachtwoord", type="password"); r = st.selectbox("Rol", ["Admin", "Medewerker"])
            if st.form_submit_button("Toevoegen"):
                supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p, "rol": r}).execute()
                st.rerun()

else:
    # --- PUBLIEK FORMULIER ---
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        # ... (jouw bestaande formulier code blijft hier staan)
        if st.form_submit_button("Indienen"):
            # ... (jouw database insert code blijft hier staan)
            st.success("Verzonden!")
