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

# --- CSS & HEADER ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp, [data-testid="stSidebar"] { background-color: #90D5FF; }
    .header-bar { background-color: #003366; color: white; padding: 40px; text-align: center; border: 5px solid #ffcc00; border-radius: 15px; margin-bottom: 30px; }
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
    
    try: st.image("orgineel logo Centrum.png", width=250)
    except: st.warning("Logo niet gevonden")

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten) if klachten else pd.DataFrame()

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        if klachten:
            for k in klachten:
                with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')}"):
                    st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                    notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k.get('id')}")
                    if st.button("💾 Opslaan", key=f"save_{k.get('id')}"):
                        supabase.table("klachten").update({"interne_notitie": notitie}).eq("id", k.get('id')).execute()
                        st.rerun()
        else: st.info("Geen klachten gevonden.")

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        if not df_dash.empty: st.dataframe(df_dash)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        with st.form("add_user_form_unique", clear_on_submit=True):
            u = st.text_input("Gebruikersnaam")
            p = st.text_input("Wachtwoord", type="password")
            if st.form_submit_button("Toevoegen"):
                supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p}).execute()
                st.rerun()
else:
    else:
    # --- VOLLEDIG KLACHT FORMULIER ---
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form_unique", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        naam = col1.text_input("👤 Volledige Naam")
        id_nr = col1.text_input("🆔 ID Nummer")
        telefoon = col1.text_input("📞 Telefoon/Whatsapp Nummer")
        woonadres = col1.text_input("🏠 Woonadres")
        
        email = col2.text_input("📧 E-mail")
        soort = col2.selectbox("📂 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        
        omschrijving = st.text_area("📝 Omschrijving van uw klacht")
        file = st.file_uploader("📎 Bijlage (Foto of Document uploaden)")
        
        if st.form_submit_button("Klacht Indienen 🚀"):
            if naam and omschrijving:
                # Ticket ID aanmaken
                t_id = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
                
                # Opslaan in database
                supabase.table("klachten").insert({
                    "volledige_naam": naam, 
                    "id_nummer": id_nr, 
                    "telefoon_whatsapp": telefoon,
                    "adres": woonadres, 
                    "email": email, 
                    "omschrijving": omschrijving,
                    "status": "Nieuw", 
                    "ticket_id": t_id, 
                    "klachtensoort": soort
                }).execute()
                
                st.success("✅ Uw klacht is succesvol ingediend! Ticket ID: " + t_id)
            else:
                st.warning("⚠️ Vul minimaal uw naam en de omschrijving in.")
