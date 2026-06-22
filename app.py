import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import smtplib
from email.message import EmailMessage

# --- CONFIGURATIE ---
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide", initial_sidebar_state="expanded")
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

import streamlit as st

# --- CSS ---
st.markdown("""
    <style>
    /* UI Elementen verbergen */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    header {visibility: visible;} 
    
    /* Achtergrond kleuren */
    .stApp { background-color: #90D5FF; }
    [data-testid="stSidebar"] { background-color: #90D5FF; }
    
    /* Header balk styling */
    .header-bar { 
        background-color: #003366; 
        color: white; 
        padding: 20px; 
        border: 3px solid #ffcc00; 
        border-radius: 10px; 
        text-align: center;
    }
    
    /* Tekst groter maken */
    .header-bar h1 { 
        font-size: 32px !important; 
        color: white !important; 
    }
    
    .header-bar p { 
        font-size: 18px !important; 
        color: white !important; 
    }
    
    /* Mobiele optimalisatie */
    @media (max-width: 600px) {
        .header-bar { padding: 10px; }
        .header-bar h1 { font-size: 20px !important; }
        .header-bar p { font-size: 12px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col1, col2, col3 = st.columns([1, 5, 1])

with col1:
    st.image("orgineel logo Centrum.png", use_container_width=True)

with col2:
    st.markdown("""
        <div style="background-color: #003366; color: white; padding: 15px; 
                    text-align: center; border: 3px solid #ffcc00; border-radius: 10px;">
            <h1 style="margin: 0; font-size: 22px;">Klachtenunit Commissariaat Wanica Centrum</h1>
            <p style="margin: 5px 0 0 0;">
                📍 Tawajarieweg 20 Lelydorp | 
                📞 +597-366660/+597-366929 | 
                💬 +597-8921062 | 
                ✉️ klachtenunitwanicacentrum@gmail.com
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.image("pngegg (1).png", use_container_width=True)
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
    try: st.image("orgineel logo Centrum.png", width=300)
    except: st.warning("Logo bestand niet gevonden")

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

   elif st.session_state.menu == "⚙️ Instellingen":
        st.title("⚙️ Instellingen - Gebruikersbeheer")
        
        # Nieuwe medewerker toevoegen
        with st.expander("➕ Nieuwe medewerker toevoegen"):
            with st.form("add_user_form", clear_on_submit=True):
                u = st.text_input("👤 Gebruikersnaam")
                p = st.text_input("🔑 Wachtwoord", type="password")
                r = st.selectbox("🎭 Rol", ["Admin", "Medewerker", "Viewer"])
                if st.form_submit_button("💾 Opslaan"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p, "rol": r}).execute()
                    st.success("✅ Toegevoegd!")
                    st.rerun()
        
        # Huidige medewerkers overzicht
        st.subheader("👥 Huidige medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        if medewerkers:
            st.table(pd.DataFrame(medewerkers)[['gebruikersnaam', 'rol']])
            
            # Verwijder functie
            te_verwijderen = st.selectbox("🗑️ Selecteer gebruiker om te verwijderen", options=[m['gebruikersnaam'] for m in medewerkers])
            if st.button("❌ Verwijder deze medewerker"):
                supabase.table("medewerkers").delete().eq("gebruikersnaam", te_verwijderen).execute()
                st.rerun()

        # Wachtwoord wijzigen sectie
        st.markdown("---")
        st.subheader("🔑 Wachtwoord wijzigen")
        with st.form("change_password_form"):
            user_to_change = st.selectbox("Selecteer medewerker om wachtwoord te wijzigen", options=[m['gebruikersnaam'] for m in medewerkers])
            new_pw = st.text_input("Nieuw wachtwoord", type="password")
            confirm_pw = st.text_input("Bevestig nieuw wachtwoord", type="password")
            
            if st.form_submit_button("Opslaan nieuw wachtwoord"):
                if new_pw == confirm_pw:
                    supabase.table("medewerkers").update({"wachtwoord": new_pw}).eq("gebruikersnaam", user_to_change).execute()
                    st.success(f"✅ Wachtwoord voor {user_to_change} is succesvol gewijzigd!")
                    st.rerun()
                else:
                    st.error("❌ De wachtwoorden komen niet overeen.")
else:
    with st.form("klacht_form", clear_on_submit=True):
        st.subheader("📝 Klacht Indienen")
        c1, c2 = st.columns(2)
        naam = c1.text_input("👤 Volledige Naam")
        email = c2.text_input("📧 E-mail")
        id_nr = c1.text_input("🆔 ID Nummer")
        soort = c2.selectbox("📂 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        telefoon = c1.text_input("📞 Telefoon/Whatsapp Nummer")
        adres = c2.text_input("🏠 Woonadres")
        omschrijving = st.text_area("✍️ Omschrijving/Eventueel Oplossings Voorstel")
        file = st.file_uploader("📎 Bijlage")
        
        if st.form_submit_button("🚀 Verstuur Klacht"):
            # 1. Automatische nummering
            huidig_jaar = datetime.now().year
            bestaande_klachten = supabase.table("klachten").select("ticket_id").ilike("ticket_id", f"WAN-{huidig_jaar}-%").execute().data
            if bestaande_klachten:
                nummers = [int(k['ticket_id'].split('-')[-1]) for k in bestaande_klachten]
                volgend_nummer = max(nummers) + 1
            else:
                volgend_nummer = 1
            t_id = f"WAN-{huidig_jaar}-{volgend_nummer:03d}"
            
            # 2. Opslaan
            supabase.table("klachten").insert({"volledige_naam": naam, "email": email, "id_nummer": id_nr, "telefoon_whatsapp": telefoon, "adres": adres, "omschrijving": omschrijving, "klachtensoort": soort, "status": "Nieuw", "ticket_id": t_id}).execute()
            
            # 3. Mailen
           # Vriendelijke bevestiging naar de burger
            bevestiging_mail = f"""
            <html>
                <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
                    <h2 style="color: #003366;">Bevestiging van uw melding</h2>
                    <p>Beste {naam},</p>
                    <p>Hartelijk dank voor uw bericht aan de <strong>Klachtenunit van het Commissariaat Wanica Centrum</strong>. Wij waarderen het zeer dat u de tijd heeft genomen om ons op de hoogte te stellen van deze situatie.</p>
                    <p>Wij hebben uw klacht in goede orde ontvangen en geregistreerd onder het volgende referentienummer:</p>
                    <div style="background-color: #f0f7ff; padding: 15px; border-left: 5px solid #003366; border-radius: 5px;">
                        <p style="margin: 0; font-size: 18px;"><strong>Referentienummer: {t_id}</strong></p>
                    </div>
                    <p>Ons team zal uw melding zorgvuldig beoordelen. Wij streven ernaar om u binnen een redelijke termijn te informeren over de status van uw klacht.</p>
                    <p>Met vriendelijke groet,<br><strong>Het team van Klachtenunit Wanica Centrum</strong></p>
                </body>
            </html>
            """
            stuur_mail(email, f"Bevestiging van uw klacht - {t_id}", bevestiging_mail)

            # Gedetailleerde tabel-mail naar de medewerker
            medewerker_mail = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #003366;">Nieuwe klacht binnengekomen: {t_id}</h2>
                    <p>Er is via het systeem een nieuwe klacht ingediend. Hieronder vindt u alle gegevens van de burger:</p>
                    <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
                        <tr style="background-color: #f2f2f2;"><th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Veld</th><th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Gegevens</th></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Naam</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{naam}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>E-mail</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{email}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>ID Nummer</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{id_nr}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Telefoon</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{telefoon}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Adres</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{adres}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Soort klacht</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{soort}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Omschrijving</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{omschrijving}</td></tr>
                    </table>
                    <p><i>Bijlage(n) (indien geüpload) zijn als bestand aan deze mail toegevoegd.</i></p>
                    <br>
                    <p>Met vriendelijke groet,<br>Het Klachten Systeem</p>
                </body>
            </html>
            """
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {t_id}", medewerker_mail, bestand=file)
            st.success(f"✅ Uw klacht is verzonden! Referentienummer: {t_id}")
            # --- FOOTER ---
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #003366;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 2px solid #ffcc00;
    }
    </style>
    <div class="footer">
        © 2026 Districstcommissariaat Wanica Centrum | Afdeling ICT
    </div>
""", unsafe_allow_html=True)
            
