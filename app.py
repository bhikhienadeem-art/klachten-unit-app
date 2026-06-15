import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# 1. Configuratie & Setup (Moet als eerste)
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialisatie
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# Header
col_logo, col_text = st.columns([1, 4]) 
with col_logo:
    st.image("orgineel logo Centrum.png", width=150)
with col_text:
    st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# 2. Sidebar (Inloggen)
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

# 3. Pagina Logica
if st.session_state.logged_in:
    # --- MEDEWERKERS PAGINA'S ---
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        klachten = supabase.table("klachten").select("*").execute().data
        if klachten:
            df = pd.DataFrame(klachten)
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal", len(df))
            c2.metric("Nieuw", len(df[df['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df[df['status'] == 'Afgehandeld']))
            for k in klachten:
                with st.expander(f"{k.get('volledige_naam')} | Status: {k.get('status')}"):
                    st.write(f"Omschrijving: {k.get('omschrijving')}")
    
    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        st.write("Beheer hier je team.")
        
    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten")
        st.write("Hier komt je data-analyse.")

else:
   else:
    # --- BURGERS PAGINA ---
    st.subheader("Welkom - Wat wilt u doen?")
    tab1, tab2 = st.tabs(["📝 Klacht indienen", "🗓️ Afspraak maken"])
    
    with tab1:
        # HET VOLLEDIGE FORMULIER
        with st.form("klacht_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            naam = col1.text_input("👤 Volledige naam")
            id_nr = col1.text_input("🆔 ID Nummer")
            telefoon = col1.text_input("📞 Telefoon/WhatsApp nummer")
            woonadres = col1.text_input("🏠 Woonadres")
            email = col2.text_input("📧 E-mailadres")
            soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
            omschrijving = st.text_area("📝 Omschrijving")
            
            # De file uploader is hier weer toegevoegd
            uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'jpeg', 'pdf'])
            
            if st.form_submit_button("Verstuur Klacht"):
                file_url = None
                if uploaded_file is not None:
                    try:
                        file_path = f"bijlagen/{uploaded_file.name}"
                        supabase.storage.from_("bijlagen").upload(file_path, uploaded_file.getvalue())
                        file_url = supabase.storage.from_("bijlagen").get_public_url(file_path)
                    except Exception as e:
                        st.error(f"Fout bij uploaden bestand: {e}")
                
                # Opslaan in database
                supabase.table("klachten").insert({
                    "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                    "adres": woonadres, "email": email, "klachtensoort": soort,
                    "omschrijving": omschrijving, "status": "Nieuw", "bijlage_url": file_url
                }).execute()
                st.success("✅ Klacht inclusief bijlage verzonden!")
                
    with tab2:
        # Afspraken formulier
        with st.form("afspraak_form", clear_on_submit=True):
            naam_af = st.text_input("Uw Naam")
            datum = st.date_input("Datum")
            slots = [t.strftime("%H:%M") for t in pd.date_range("08:00", "14:00", freq="15min")]
            tijd = st.selectbox("Tijdstip", slots)
            if st.form_submit_button("Afspraak Bevestigen"):
                supabase.table("afspraken").insert({"naam": naam_af, "datum": str(datum), "tijdstip": tijd}).execute()
                st.success(f"✅ Afspraak op {datum} om {tijd}!")
