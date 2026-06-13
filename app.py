import streamlit as st
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
# Gebruik je service_role key voor admin-acties (beveilig deze goed!)
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

# Eenvoudige login (vervangen door Supabase Auth in productie)
with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    gebruiker = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        # Hier hoort echte auth logica. Voor nu houden we je admin-login:
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
            # ... (jouw bestaande dashboard code)
            
        with tab2:
            st.subheader("Nieuwe Medewerker Toevoegen")
            with st.form("add_user_form"):
                naam = st.text_input("Naam medewerker")
                pw = st.text_input("Wachtwoord", type="password")
                
                if st.form_submit_button("Account Aanmaken"):
                    try:
                        # 1. Dummy email genereren voor Supabase Auth
                        dummy_email = f"{naam.lower().replace(' ', '')}@wanicacentrum.sr"
                        
                        # 2. Gebruiker aanmaken in Supabase Auth
                        auth_res = supabase.auth.admin.create_user({
                            "email": dummy_email,
                            "password": pw,
                            "email_confirm": True
                        })
                        
                        # 3. Opslaan in 'gebruikers' tabel
                        supabase.table("gebruikers").insert({
                            "id": auth_res.user.id,
                            "email": dummy_email,
                            "naam": naam,
                            "rol": "medewerker"
                        }).execute()
                        
                        st.success(f"Medewerker {naam} is toegevoegd!")
                    except Exception as e:
                        st.error(f"Fout: {e}")
    else:
        st.title("Dashboard (Medewerker)")
        # ... (jouw dashboard code)

else:
    # Publiek formulier voor klachten
    # ... (jouw bestaande formulier code)
