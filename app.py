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
        
        if bestand is not None:
            msg.add_attachment(bestand.getvalue(), maintype='application', subtype='octet-stream', filename=bestand.name)
            
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail fout: {e}")
        return False

# --- CSS ---
st.markdown("""
    <style>
    .header-bar { background-color: #003366; color: white; padding: 30px; text-align: center; border-radius: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# --- AUTH & SESSIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    if not st.session_state.logged_in:
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            check = supabase.table("medewerkers").select("*").eq("gebruikersnaam", user).eq("wachtwoord", pw).execute().data
            if check: st.session_state.logged_in = True; st.rerun()
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten"])
        if st.button("Uitloggen"): st.session_state.logged_in = False; st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten)

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            row_id = k.get('id')
            with st.expander(f"👤 {k.get('volledige_naam')} | Status: {k.get('status')}"):
                st.write(f"**E-mail:** {k.get('email')} | **Tel:** {k.get('telefoon_whatsapp')}")
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], key=f"s_{row_id}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"n_{row_id}")
                bericht = st.text_area("Bericht naar burger", key=f"b_{row_id}")
                
                c1, c2 = st.columns(2)
                if c1.button("💾 Opslaan & Mailen", key=f"save_{row_id}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", row_id).execute()
                    if bericht: stuur_mail(k.get('email'), "Update uw klacht", f"<p>{bericht}</p>")
                    st.success("Opgeslagen!")
                    st.rerun()
                if c2.button("🗑️ Verwijderen", key=f"del_{row_id}"):
                    supabase.table("klachten").delete().eq("id", row_id).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        if not df_dash.empty:
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.bar(df_dash['klachtensoort'].value_counts().reset_index(), x='klachtensoort', y='count'), use_container_width=True)
            c2.plotly_chart(px.pie(df_dash, names='klachtensoort'), use_container_width=True)

else:
    with st.form("klacht_form", clear_on_submit=True):
        st.subheader("📝 Klacht Indienen")
        col1, col2 = st.columns(2)
        naam = col1.text_input("👤 Naam")
        email = col2.text_input("📧 E-mail")
        omschrijving = st.text_area("✍️ Omschrijving")
        file = st.file_uploader("📎 Bijlage")
        if st.form_submit_button("🚀 Verstuur Klacht"):
            supabase.table("klachten").insert({"volledige_naam": naam, "email": email, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
            stuur_mail(email, "Bevestiging", "Bedankt voor uw melding.")
            st.success("Verzonden!")
