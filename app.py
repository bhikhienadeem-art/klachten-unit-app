import streamlit as st
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER (Blijft ongewijzigd) ---
st.markdown("""
    <style>
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    .contact-info { font-size: 0.95em; margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); }
    </style>
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="contact-info">
            📍 <b>Adres:</b> Indira Gandhiweg | 📞 <b>Tel:</b> (+597) 584xxx | 💬 <b>WhatsApp:</b> (+597) 8xxx-xxx | ✉️ <b>E-mail:</b> klachten.wanica@gov.sr
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Ongeldige gegevens")
    else:
        st.success("Ingelogd als Admin")
        menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if menu == "Dashboard":
        # ... (hier je bestaande dashboard code laten staan)
        st.write("Dashboard inhoud actief...")
    
    elif menu == "Rapporten":
        st.title("📈 Rapporten")
        st.selectbox("Type rapport", ["Wekelijks", "Maandelijks"])
        st.button("Genereer & Download Rapport")

    elif menu == "Instellingen":
        st.title("⚙️ Instellingen")
        tab1, tab2 = st.tabs(["Gebruikers", "Rollen"])
        with tab1:
            st.text_input("Nieuwe medewerker")
            st.button("Toevoegen")
        with tab2:
            st.write("Beheer rollen hier.")

# --- FORMULIER (Blijft altijd onderaan) ---
st.divider()
st.title("Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    # ... (je bestaande formulier code laten staan)
    st.form_submit_button("Verstuur klacht")
