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
        
        # Logica voor bijlage toevoegen
        if bestand:
            msg.add_attachment(
                bestand.getvalue(),
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

# --- CSS & HEADER ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp, [data-testid="stSidebar"] { background-color: #90D5FF; }
    .header-bar { background-color: #003366; color: white; padding: 40px; text-align: center; border: 5px solid #ffcc00; border-radius: 15px; margin-bottom: 30px; }
    .header-bar h1 { font-size: 3em; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

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
    st.markdown("---")
    try: st.image("orgineel logo Centrum.png", width=250)
    except: st.warning("Logo bestand niet gevonden")

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
            row_id = k.get('id')
            status = k.get('status', 'Nieuw')
            
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | Status: {status}"):
                # Hier tonen we de extra gegevens
                st.subheader("📋 Gegevens van de burger")
                col_a, col_b = st.columns(2)
                col_a.write(f"**ID Nummer:** {k.get('id_nummer', '-')}")
                col_a.write(f"**Telefoon:** {k.get('telefoon_whatsapp', '-')}")
                col_b.write(f"**E-mail:** {k.get('email', '-')}")
                col_b.write(f"**Adres:** {k.get('adres', '-')}")
                st.write(f"**Soort klacht:** {k.get('klachtensoort', '-')}")
                st.markdown("---")
                
                # Hieronder volgt je bestaande status/notitie code
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                nieuwe_status = st.selectbox("Status", status_opties, index=status_opties.index(status) if status in status_opties else 0, key=f"status_{row_id}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{row_id}")
                mail_bericht = st.text_area("Bericht naar de burger", key=f"msg_{row_id}")

                if st.button("💾 Status & Notitie Opslaan", key=f"save_{row_id}"):
                    # Database update
                    supabase.table("klachten").update({
                        "status": nieuwe_status,
                        "interne_notitie": notitie
                    }).eq("id", row_id).execute()
                    
                    # Mail versturen (zorg dat de functie-definitie stuur_mail(..., bestand=None) is)
                    mail_inhoud = f"<p>Update over uw klacht ({k.get('ticket_id')}):</p><p>{mail_bericht}</p>"
                    if stuur_mail(k.get('email'), "Update klacht", mail_inhoud):
                        st.success("✅ Opgeslagen en gemaild!")
                        st.rerun()

elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        
        if not df_dash.empty:
            df_plot = df_dash['klachtensoort'].value_counts().reset_index()
            df_plot.columns = ['Soort', 'Aantal']
            
            # Kolommen voor side-by-side of onder elkaar
            col1, col2 = st.columns(2)
            
            # Staafdiagram
            fig_bar = px.bar(df_plot, x='Soort', y='Aantal', color='Soort', title="Staafdiagram: Klachten per soort")
            col1.plotly_chart(fig_bar, use_container_width=True)
            
            # Cirkeldiagram (Pie Chart)
            fig_pie = px.pie(df_plot, values='Aantal', names='Soort', title="Cirkeldiagram: Verhouding klachten")
            col2.plotly_chart(fig_pie, use_container_width=True)
            
            st.dataframe(df_dash)
        else:
            st.info("Nog geen klachten om te tonen.")
else:
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Naam")
        id_nr = col1.text_input("ID Nummer")
        telefoon = col1.text_input("Telefoon")
        woonadres = col1.text_input("Woonadres")
        email = col2.text_input("E-mail")
        soort = col2.selectbox("Soort", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        file = st.file_uploader("Bijlage")
        
        if st.form_submit_button("Verstuur Klacht"):
            t_id = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            supabase.table("klachten").insert({"volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon, "adres": woonadres, "email": email, "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": t_id, "klachtensoort": soort}).execute()
            stuur_mail(email, "Bevestiging van uw klacht", "Bedankt voor uw melding.")
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {t_id}", "Er is een nieuwe melding.", bestand=file)
            st.success("✅ Uw klacht is verzonden!")
