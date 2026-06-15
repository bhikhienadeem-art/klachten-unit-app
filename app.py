import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Stel de pagina-configuratie in
st.set_page_config(
    page_title="Klachten Unit Wanica",
    page_icon="https://wanica.gov.sr/images/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS STYLING (Professioneel Blauw Thema) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    .header-bar {
        background-color: #004a99;
        color: white;
        padding: 30px;
        text-align: center;
        border-bottom: 6px solid #003366;
        border-radius: 0px 0px 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-bar h1 { margin: 0; color: white !important; font-size: 2.5em; }
    .header-text { margin-top: 15px; font-size: 1.2em; font-style: italic; color: #e1eaf3; }
    .contact-info { font-size: 1.0em; margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3); color: white; }
    [data-testid="stSidebar"] { background-color: #e8eff6; }
    div[data-testid="stExpander"], [data-testid="stForm"] {
        background-color: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    div.stButton > button { background-color: #004a99; color: white !important; border-radius: 8px; border: none; font-weight: bold; }
    div.stButton > button:hover { background-color: #003366; }
    h1, h2, h3, h4 { color: #004a99 !important; }
    a.mailto-link { text-decoration: none; color: white !important; background-color: #004a99; padding: 10px 15px; border-radius: 8px; font-weight: bold; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>🏢 Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="header-text">Samen bouwen we aan een beter Wanica.<br>Uw stem telt. Via deze pagina kunt u uw klacht of suggestie indienen.</div>
        <div class="contact-info">📍 <b>Adres:</b> Tawajarieweg 20 | 📞 <b>Tel:</b> (+597) 366660 | ✉️ <b>E-mail:</b> klachtenunitwanicacentrum@gmail.com</div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("👤 Gebruikersnaam")
        wachtwoord = st.text_input("🔒 Wachtwoord", type="password")
        if st.button("🔓 Inloggen", use_container_width=True):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Ongeldige gegevens.")
    else:
        st.success("✅ Ingelogd als Admin")
        st.session_state.menu = st.radio("🏠 Navigatie", ["📊 Dashboard", "📈 Rapporten", "⚙️ Instellingen"])
        if st.button("🔒 Uitloggen", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA (Admin gedeelte) ---
if st.session_state.logged_in:
    if st.session_state.menu == "📊 Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"👤 Klacht: {k.get('volledige_naam', 'Anoniem')} | Status: {k.get('status', 'Nieuw')}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🆔 ID:** {k.get('id_nummer', '-')}")
                col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}")
                col_a.write(f"**📞 Tel/WA:** {k.get('telefoon', '-')}")
                col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                col_b.write(f"**📋 Soort:** {k.get('klachtensoort', '-')}")
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                if k.get('bijlage_url'): st.info(f"📎 Bijlage: {k['bijlage_url']}")
                st.divider()
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=status_opties.index(k.get('status', 'Nieuw')), key=f"status_{k['id']}")
                notitie = st.text_area("✍️ Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                if st.button("💾 Opslaan", key=f"save_{k['id']}", use_container_width=True):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.rerun()
    # (Overige menu items: Rapporten & Instellingen hier weggelaten voor kortheid, maar die staan in je vorige code)

# --- FORMULIER (Voor de burger) ---
st.divider()
st.subheader("📋 Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("👤 Volledige naam")
        id_nr = st.text_input("🆔 ID Nummer")
        telefoon = st.text_input("📞 Telefoon/WhatsApp nummer")
        woonadres = st.text_input("🏠 Woonadres")
    with col2:
        email = st.text_input("📧 E-mailadres")
        soort = st.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'pdf'])
    omschrijving = st.text_area("📝 Omschrijving of suggestie voor oplossing")
    if st.form_submit_button("Verstuur klacht"):
        supabase.table("klachten").insert({
            "volledige_naam": naam, "id_nummer": id_nr, "telefoon": telefoon, "adres": woonadres, 
            "email": email, "klachtensoort": soort, "omschrijving": omschrijving, 
            "status": "Nieuw", "bijlage_url": uploaded_file.name if uploaded_file else None
        }).execute()
        st.success("✅ Uw klacht is succesvol verzonden!")
