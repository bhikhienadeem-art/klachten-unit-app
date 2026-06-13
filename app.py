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
            response = supabase.table("klachten").select("*").execute()
            for k in response.data:
                with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')}"):
                    st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                    st.write(f"**Status:** {k.get('status', 'Nieuw')}")
            
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
        response = supabase.table("klachten").select("*").execute()
        for k in response.data:
            with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")

else:
    # --- PUBLIEK FORMULIER ---
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            id_nr = st.text_input("ID Nummer")
        with col2:
            adres = st.text_input("Adres")
            soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        uploaded_file = st.file_uploader("Voeg bijlage toe", type=['png', 'jpg', 'pdf'])
        if st.form_submit_button("Verstuur klacht"):
            try:
                file_path = None
                if uploaded_file:
                    file_path = f"bijlagen/{uuid.uuid4()}_{uploaded_file.name}"
                    supabase.storage.from_("klachten-bijlagen").upload(file_path, uploaded_file.getvalue())
                data = {"volledige_naam": naam, "id_nummer": id_nr, "adres": adres, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw", "bijlagen": file_path}
                supabase.table("klachten").insert(data).execute()
                st.success("Verzonden!")
            except Exception as e:
                st.error(f"Fout: {e}")
