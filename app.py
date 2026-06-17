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

# --- FUNCTIES ---
def stuur_mail(ontvanger, onderwerp, html_inhoud, bestand=None):
    try:
        msg = EmailMessage()
        msg['Subject'] = onderwerp
        msg['From'] = "Klachtenunit Wanica <klachtenunitwanicacentrum@gmail.com>"
        msg['To'] = ontvanger
        msg['Bcc'] = "klachtenunitwanicacentrum@gmail.com" 
        msg.add_alternative(html_inhoud, subtype='html')
        if bestand:
            msg.add_attachment(bestand.getvalue(), maintype='application', subtype='octet-stream', filename=bestand.name)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("klachtenunitwanicacentrum@gmail.com", "nbngichzpmlgzglc")
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail fout: {e}")
        return False

# --- CSS & ACHTERGROND ---
st.markdown("""
    <style>
    /* Verberg de standaard Streamlit menu/header balk */
    #MainMenu {visibility: hidden;} 
    header {visibility: hidden;} 
    footer {visibility: hidden;}

    /* Achtergrond van de hele pagina */
    .stApp { background-color: #90D5FF; }
    
    /* Achtergrond van de sidebar */
    [data-testid="stSidebar"] { background-color: #90D5FF; }
    
    /* Header styling */
    .header-bar { 
        background-color: #003366; 
        color: white; 
        padding: 30px; 
        text-align: center; 
        border: 5px solid #ffcc00; 
        border-radius: 15px; 
        margin-bottom: 20px; 
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1>📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com</div>""", unsafe_allow_html=True)

# --- SIDEBAR & AUTH ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
with st.sidebar:
    st.markdown("## 🔐 Medewerkers Login")
    if not st.session_state.logged_in:
        user = st.text_input("👤 Gebruikersnaam")
        pw = st.text_input("🔑 Wachtwoord", type="password")
        if st.button("🚀 Inloggen"):
            if supabase.table("medewerkers").select("*").eq("gebruikersnaam", user).eq("wachtwoord", pw).execute().data:
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.session_state.menu = st.radio("🧭 Navigatie", ["📊 Dashboard", "📈 Rapporten", "⚙️ Instellingen"])
        if st.button("🚪 Uitloggen"): st.session_state.logged_in = False; st.rerun()
    st.markdown("---")
    try: 
        # Groter logo hier:
        st.image("orgineel logo Centrum.png", width=300)
    except: 
        st.warning("Logo bestand niet gevonden")

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten)

    if st.session_state.menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        for k in klachten:
            row_id = k.get('id')
            with st.expander(f"👤 {k.get('volledige_naam')} | 🚦 Status: {k.get('status')}"):
                c1, c2 = st.columns(2)
                c1.write(f"**🆔 ID:** {k.get('id_nummer')}\n**📞 Tel:** {k.get('telefoon_whatsapp')}\n**🏠 Adres:** {k.get('adres')}")
                c2.write(f"**📧 E-mail:** {k.get('email')}\n**📂 Soort:** {k.get('klachtensoort')}")
                st.write(f"**✍️ Omschrijving:** {k.get('omschrijving')}")
                nieuwe_status = st.selectbox("🚦 Status bijwerken", ["Nieuw", "In behandeling", "Afgehandeld"], key=f"s_{row_id}")
                notitie = st.text_area("📝 Interne notitie", value=k.get('interne_notitie', ''), key=f"n_{row_id}")
                bericht = st.text_area("✉️ Bericht naar de burger", key=f"b_{row_id}")
                col1, col2 = st.columns(2)
                if col1.button("💾 Opslaan & Mailen", key=f"save_{row_id}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", row_id).execute()
                    if bericht: stuur_mail(k.get('email'), "Update over uw klacht", f"<p>{bericht}</p>")
                    st.success("Opgeslagen!")
                    st.rerun()
                if col2.button("🗑️ Verwijderen", key=f"del_{row_id}"):
                    supabase.table("klachten").delete().eq("id", row_id).execute()
                    st.rerun()

    elif st.session_state.menu == "📈 Rapporten":
        st.title("📈 Rapporten & Detailoverzicht")
        if not df_dash.empty:
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.bar(df_dash['klachtensoort'].value_counts().reset_index(), x='klachtensoort', y='count'), use_container_width=True)
            c2.plotly_chart(px.pie(df_dash, names='klachtensoort'), use_container_width=True)
            st.dataframe(df_dash, use_container_width=True)
            csv = df_dash.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "klachten.csv", "text/csv")

    elif st.session_state.menu == "⚙️ Instellingen":
        st.title("⚙️ Instellingen - Gebruikersbeheer")
        with st.expander("➕ Nieuwe medewerker toevoegen"):
            with st.form("add_user_form", clear_on_submit=True):
                u = st.text_input("👤 Gebruikersnaam")
                p = st.text_input("🔑 Wachtwoord", type="password")
                r = st.selectbox("🎭 Rol", ["Admin", "Medewerker", "Viewer"])
                if st.form_submit_button("💾 Opslaan"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p, "rol": r}).execute()
                    st.success("✅ Toegevoegd!"); st.rerun()
        st.subheader("👥 Huidige medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        if medewerkers:
            st.table(pd.DataFrame(medewerkers)[['gebruikersnaam', 'rol']])
            te_verwijderen = st.selectbox("🗑️ Selecteer gebruiker om te verwijderen", options=[m['gebruikersnaam'] for m in medewerkers])
            if st.button("❌ Verwijder deze medewerker"):
                supabase.table("medewerkers").delete().eq("gebruikersnaam", te_verwijderen).execute(); st.rerun()

else:
    with st.form("klacht_form", clear_on_submit=True):
        st.subheader("📝 Klacht Indienen")
        c1, c2 = st.columns(2)
        naam = c1.text_input("👤 Naam")
        email = c2.text_input("📧 E-mail")
        id_nr = c1.text_input("🆔 ID Nummer")
        soort = c2.selectbox("📂 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        telefoon = c1.text_input("📞 Telefoon")
        adres = c2.text_input("🏠 Woonadres")
        omschrijving = st.text_area("✍️ Omschrijving")
        file = st.file_uploader("📎 Bijlage")
        if st.form_submit_button("🚀 Verstuur Klacht"):
            t_id = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            supabase.table("klachten").insert({"volledige_naam": naam, "email": email, "id_nummer": id_nr, "telefoon_whatsapp": telefoon, "adres": adres, "omschrijving": omschrijving, "klachtensoort": soort, "status": "Nieuw", "ticket_id": t_id}).execute()
            stuur_mail(email, "Bevestiging", "Bedankt voor uw melding.")
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {t_id}", "Er is een nieuwe melding.", bestand=file)
            st.success("✅ Uw klacht is verzonden!")
