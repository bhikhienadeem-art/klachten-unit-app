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
    /* Verberg de Streamlit menu-balk (witte balk) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Achtergrondkleur voor de gehele app en sidebar */
    .stApp, [data-testid="stSidebar"] { 
        background-color: #90D5FF; 
    }
    /* Grotere Header styling */
    .header-bar { 
        background-color: #003366; 
        color: white; 
        padding: 40px; 
        text-align: center; 
        border: 5px solid #ffcc00; 
        border-radius: 15px; 
        margin-bottom: 30px; 
    }
    .header-bar h1 {
        font-size: 3em; 
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# De header container
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-size: 1.2em;">
            📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)
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
    # Logo onderaan de sidebar (groter formaat)
    st.markdown("---")
    try: 
        st.image("orgineel logo Centrum.png", width=250)
    except: 
        st.warning("Logo bestand niet gevonden")
        # --- PAGINA LOGICA ---
if st.session_state.logged_in:
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten)

    # --- DASHBOARD VOOR MEDEWERKERS ---
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        
        # Data ophalen
        klachten = supabase.table("klachten").select("*").execute().data
        df_dash = pd.DataFrame(klachten)
        
        # --- METRIC CARDS ---
        if not df_dash.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal Klachten", len(df_dash))
            c2.metric("Nieuw", len(df_dash[df_dash['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df_dash[df_dash['status'] == 'Afgehandeld']))
            st.markdown("---")
        
        # --- KLACHTEN LIJST ---
        if klachten:
            for k in klachten:
                row_id = k.get('id') # Expliciet ID ophalen
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
                    
                    # Bijwerken
                    nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=huidige_idx, key=f"status_{row_id}")
                    notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{row_id}")
                    
                    if st.button("💾 Status & Notitie Opslaan", key=f"save_{row_id}"):
                        try:
                            # Veilige database update
                            supabase.table("klachten").update({
                                "status": nieuwe_status, 
                                "interne_notitie": notitie
                            }).eq("id", row_id).execute()
                            st.success("✅ Opgeslagen!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fout bij opslaan: {e}")
        else:
            st.info("Geen klachten gevonden in het systeem.")    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        if not df_dash.empty:
            st.download_button("📥 Download CSV", data=df_dash.to_csv(index=False), file_name='klachten.csv')
            st.plotly_chart(px.pie(df_dash, names='klachtensoort'))
            st.dataframe(df_dash)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Gebruikersbeheer")
        
        # --- Nieuwe medewerker toevoegen ---
        with st.expander("➕ Nieuwe medewerker toevoegen"):
            with st.form("add_user_form", clear_on_submit=True):
                u = st.text_input("Gebruikersnaam")
                p = st.text_input("Wachtwoord", type="password")
                r = st.selectbox("Rol", ["Admin", "Medewerker", "Viewer"])
                
                if st.form_submit_button("Opslaan"):
                    if u and p:
                        supabase.table("medewerkers").insert({
                            "gebruikersnaam": u, 
                            "wachtwoord": p, 
                            "rol": r
                        }).execute()
                        st.success(f"✅ Medewerker {u} is toegevoegd!")
                        st.rerun()
                    else:
                        st.error("⚠️ Vul zowel een gebruikersnaam als wachtwoord in.")
        
        st.markdown("---")
        
        # --- Huidige medewerkers beheer ---
        st.subheader("👥 Huidige medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        
        if medewerkers:
            df_users = pd.DataFrame(medewerkers)
            # Toon alleen relevante kolommen
            st.table(df_users[['gebruikersnaam', 'rol']])
            
            st.markdown("---")
            st.warning("⚠️ Gebruikers verwijderen")
            te_verwijderen = st.selectbox("Selecteer gebruiker om te verwijderen", options=[m['gebruikersnaam'] for m in medewerkers])
            
            if st.button("🗑️ Verwijder deze medewerker", type="primary"):
                supabase.table("medewerkers").delete().eq("gebruikersnaam", te_verwijderen).execute()
                st.rerun()
        else:
            st.info("Geen medewerkers gevonden.")


else:
   # --- INDIENEN KLACHT ---
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        # Invoervelden met icoontjes
        naam = col1.text_input("👤 Volledige Naam")
        id_nr = col1.text_input("🆔 ID Nummer")
        telefoon = col1.text_input("📞 Telefoon/Whatsapp Nummer")
        woonadres = col1.text_input("🏠 Woonadres")
        
        email = col2.text_input("📧 E-mail")
        soort = col2.selectbox("📂 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        
        omschrijving = st.text_area("📝 Omschrijving van uw klacht")
        file = st.file_uploader("📎 Bijlage (max 200MB)")
        
        if st.form_submit_button("Klacht Indienen 🚀"):
            t_id = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            
            # Database insert
            supabase.table("klachten").insert({
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "omschrijving": omschrijving,
                "status": "Nieuw", "ticket_id": t_id, "klachtensoort": soort
            }).execute()
            
            # VRIENDELIJKE MAIL VOOR CLIENT
            html_client = f"""
            <div style="font-family: Arial;">
                <h2 style="color:#004a99;">Uw melding is in goede orde ontvangen</h2>
                <p>Beste {naam},</p>
                <p>Hartelijk dank voor het indienen van uw klacht bij het Commissariaat Wanica Centrum.</p>
                <p>Uw melding (Referentie: <b>{t_id}</b>) is in behandeling genomen door ons team. Wij houden u via de e-mail op de hoogte van de voortgang.</p>
                <p>Met vriendelijke groet,<br><b>Klachtenunit Wanica Centrum</b></p>
            </div>"""
            stuur_mail(email, "Bevestiging van uw klacht", html_client)
            
            # GEDETAILLEERDE MAIL VOOR MEDEWERKER
            html_med = f"""
            <div style="font-family: Arial;">
                <h2 style="color:#d32f2f;">Nieuwe klacht gemeld: {t_id}</h2>
                <p>Er is zojuist een nieuwe klacht binnengekomen via het portaal. Hieronder staan de details:</p>
                <table border="1" cellpadding="10" style="border-collapse:collapse; width:100%;">
                    <tr><td><b>Naam:</b></td><td>{naam}</td></tr>
                    <tr><td><b>ID Nummer:</b></td><td>{id_nr}</td></tr>
                    <tr><td><b>Telefoon:</b></td><td>{telefoon}</td></tr>
                    <tr><td><b>Adres:</b></td><td>{woonadres}</td></tr>
                    <tr><td><b>Soort klacht:</b></td><td>{soort}</td></tr>
                    <tr><td><b>Omschrijving:</b></td><td>{omschrijving}</td></tr>
                </table>
                <p>Eventuele bewijsstukken vindt u in de bijlage van deze e-mail.</p>
            </div>"""
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {t_id}", html_med, bestand=file)
            
            st.success("✅ Uw klacht is verzonden. Bedankt voor uw melding!")
