import streamlit as st
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .header-bar { background-color: #004a99; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar"><h1>Klachtenunit Wanica Centrum</h1></div>', unsafe_allow_html=True)

# --- LOGIN & ROL-BEHEER ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
    st.session_state.rol = None

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    gebruiker = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if gebruiker == "admin" and wachtwoord == "admin123":
            st.session_state.logged_in = True
            st.session_state.rol = 'admin'
            st.rerun()

# --- DASHBOARD & ADMIN ---
if st.session_state.logged_in:
    if st.session_state.rol == 'admin':
        tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Medewerker Beheer"])
        
        with tab1:
            st.title("Dashboard")
            # Haal klachten op uit Supabase
            klachten = supabase.table("klachten").select("*").execute()
            st.write(klachten.data)
            
        with tab2:
            st.subheader("Nieuwe Medewerker Toevoegen")
            with st.form("add_user_form"):
                naam = st.text_input("Naam medewerker")
                pw = st.text_input("Wachtwoord", type="password")
                
                if st.form_submit_button("Account Aanmaken"):
                    try:
                        dummy_email = f"{naam.lower().replace(' ', '')}@wanicacentrum.sr"
                        auth_res = supabase.auth.admin.create_user({"email": dummy_email, "password": pw, "email_confirm": True})
                        supabase.table("gebruikers").insert({"id": auth_res.user.id, "email": dummy_email, "naam": naam, "rol": "medewerker"}).execute()
                        st.success(f"Medewerker {naam} is toegevoegd!")
                    except Exception as e:
                        st.error(f"Fout: {e}")
    else:
        st.title("Dashboard (Medewerker)")
        st.write("Welkom medewerker. Hier kun je klachten inzien.")

else:
    # --- PUBLIEK FORMULIER ---
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving van de klacht")
        submitted = st.form_submit_button("Verstuur")
        
        if submitted:
            data = {"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}
            supabase.table("klachten").insert(data).execute()
            st.success("Uw klacht is succesvol ingediend!")
