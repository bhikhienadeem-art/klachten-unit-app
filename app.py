import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    /* Blauwe achtergrond voor de hele app */
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-style: italic;">Welkom op de officiële klachtenpagina.</div>
        <div style="font-size: 0.9em; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
            📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam", key="user_in")
        wachtwoord = st.text_input("Wachtwoord", type="password", key="pass_in")
        if st.button("Inloggen", key="login_btn"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | Status: {k.get('status', 'Nieuw')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                if st.button("🗑️ Klacht verwijderen", key=f"del_{k['id']}"):
                    supabase.table("klachten").delete().eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        data = supabase.table("klachten").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(df, names='klachtensoort', title="Verdeling klachtensoort")
            st.plotly_chart(fig)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Beheer")
        st.write("Beheer hier medewerkers en systeeminstellingen.")

else:
    # --- FORMULIER & AFSPRAAK (Alleen zichtbaar als NIET ingelogd) ---
    st.subheader("📝 Klacht indienen")
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
        
        omschrijving = st.text_area("📝 Geef hier een korte omschrijving van uw klacht.")
        
        st.divider()
        st.subheader("📅 Afspraak maken (optioneel)")
        wil_afspraak = st.checkbox("Ik wil een afspraak maken voor deze klacht")
        
        afspraak_datum, afspraak_tijd = None, None
        if wil_afspraak:
            c1, c2 = st.columns(2)
            afspraak_datum = c1.date_input("Kies datum")
            afspraak_tijd = c2.time_input("Kies tijdstip")
            
        if st.form_submit_button("Verstuur klacht & Afspraak"):
            data = {
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw",
                "afspraak_datum": str(afspraak_datum) if wil_afspraak else None,
                "afspraak_tijd": str(afspraak_tijd) if wil_afspraak else None,
                "bijlage_url": uploaded_file.name if uploaded_file else None
            }
            supabase.table("klachten").insert(data).execute()
            st.success("✅ Uw klacht is verzonden!")
