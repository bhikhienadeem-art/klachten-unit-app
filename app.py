import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid

# 1. Configuratie (MOET BOVENAAN)
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Sessie en CSS
if "logged_in" not in st.session_state: st.session_state.logged_in = False
st.markdown("<style>.stApp { background-color: #e3f2fd; }</style>", unsafe_allow_html=True)

# 3. Header en Sidebar
st.header("Klachtenunit Commissariaat Wanica Centrum")

with st.sidebar:
    st.header("🔑 Medewerkers")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# 4. Pagina Logica
if st.session_state.logged_in:
    st.title("📊 Dashboard")
    # Hier je dashboard code...
    klachten = supabase.table("klachten").select("*").execute().data
    st.write(pd.DataFrame(klachten))
else:
    # Burgers formulier
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Volledige naam")
        email = col2.text_input("E-mailadres")
        id_nr = col1.text_input("ID Nummer")
        soort = col2.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        telefoon = col1.text_input("Telefoon/WhatsApp")
        woonadres = col1.text_input("Woonadres")
        omschrijving = st.text_area("Omschrijving")
        
        submitted = st.form_submit_button("Verstuur")
        
        if submitted:
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            data = {
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr
            }
            supabase.table("klachten").insert(data).execute()
            st.success(f"✅ Klacht verzonden! Ticket: {ticket_nr}")

    st.subheader("🗓️ Afspraak maken")
    with st.form("afspraak_form", clear_on_submit=True):
        naam_af = st.text_input("Uw Naam")
        datum = st.date_input("Datum")
        if st.form_submit_button("Afspraak Bevestigen"):
            st.success("✅ Afspraak bevestigd!")
