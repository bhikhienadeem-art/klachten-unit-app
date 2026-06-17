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
        msg['Bcc'] = "klachtenunitwanicacentrum@gmail.com" 
        msg.add_alternative(html_inhoud, subtype='html')
        if bestand is not None:
            msg.add_attachment(bestand.getvalue(), maintype='application', subtype='octet-stream', filename=bestand.name)
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
    .header-bar { background-color: #003366; color: white; padding: 30px; text-align: center; border: 5px solid #ffcc00; border-radius: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-size: 1.1em;">
            📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SESSIE & AUTH ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.markdown("## 🔐 Medewerkers Login")
    if not st.session_state.logged_in:
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            check = supabase.table("medewerkers").select("*").eq("gebruikersnaam", user).eq("wachtwoord", pw).execute().data
            if check:
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")
    try: st.image("orgineel logo Centrum.png", width=250)
    except: st.warning("Logo bestand niet gevonden")

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten)

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            row_id = k.get('id')
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | Status: {k.get('status', 'Nieuw')}"):
                st.write(f"**E-mail:** {k.get('email')} | **Tel:** {k.get('telefoon_whatsapp')}")
                st.write(f"**Omschrijving:** {k.get('omschrijving')}")
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], key=f"status_{row_id}")
                notitie = st.text_area("Notitie", value=k.get('interne_notitie', ''), key=f"note_{row_id}")
                c1, c2 = st.columns(2)
                if c1.button("💾 Opslaan", key=f"save_{row_id}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", row_id).execute()
                    st.rerun()
                if c2.button("🗑️ Verwijderen", key=f"del_{row_id}"):
                    supabase.table("klachten").delete().eq("id", row_id).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        if not df_dash.empty:
            df_plot = df_dash['klachtensoort'].value_counts().reset_index()
            df_plot.columns = ['Soort', 'Aantal']
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.bar(df_plot, x='Soort', y='Aantal', color='Soort'), use_container_width=True)
            c2.plotly_chart(px.pie(df_plot, values='Aantal', names='Soort'), use_container_width=True)

else:
    with st.form("klacht_form", clear_on_submit=True):
        st.subheader("📝 Klacht Indienen")
        col1, col2 = st.columns(2)
        naam = col1.text_input("👤 Naam")
        id_nr = col1.text_input("🆔 ID Nummer")
        telefoon = col1.text_input("📞 Telefoon")
        woonadres = col1.text_input("🏠 Woonadres")
        email = col2.text_input("📧 E-mail")
        soort = col2.selectbox("📂 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("✍️ Omschrijving")
        file = st.file_uploader("📎 Bijlage")
        if st.form_submit_button("🚀 Verstuur Klacht"):
            t_id = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            supabase.table("klachten").
