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
    [data-testid="stAppViewContainer"] { padding-top: 0rem; }
    .header-bar { 
        background-color: #004a99; color: white; padding: 30px 20px; 
        text-align: center; margin-bottom: 30px; border-bottom: 5px solid #ffcc00;
    }
    .main-title { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
    .contact-info { font-size: 16px; line-height: 1.6; }
    [data-testid="stSidebar"] { background-color: #f0f2f6 !important; }
    [data-testid="stSidebar"] div { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <div class="main-title">Klachtenunit Commissariaat Wanica Centrum</div>
        <div class="contact-info">
            📍 Tawajariweg #20 | 📞 366660 / 366929 | 💬 8921062 <br>
            📧 klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
    st.session_state.rol = None

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.session_state.rol = 'admin'
                st.rerun()
    else:
        st.write(f"Ingelogd als: {st.session_state.rol}")
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- DASHBOARD & FORMULIER ---
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
            st.subheader("Medewerker Beheer")
            # Beheer logica...
    else:
        st.title("Dashboard (Medewerker)")
else:
    # HIER KOMT JE FORMULIER TERUG
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            id_nr = st.text_input("ID Nummer")
            email = st.text_input("E-mailadres")
        with col2:
            adres = st.text_input("Adres")
            telefoon = st.text_input("Telefoon/Whatsapp")
            soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        
        omschrijving = st.text_area("Omschrijving")
        uploaded_file = st.file_uploader("Voeg bijlage toe", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Verstuur klacht"):
            try:
                file_path = None
                if uploaded_file:
                    file_path = f"bijlagen/{uuid.uuid4()}_{uploaded_file.name}"
                    supabase.storage.from_("klachten-bijlagen").upload(file_path, uploaded_file.getvalue())
                
                data = {
                    "volledige_naam": naam, "id_nummer": id_nr, "email": email, "adres": adres, 
                    "telefoon_whatsapp": telefoon, "klachtensoort": soort, "omschrijving": omschrijving, 
                    "status": "Nieuw", "bijlagen": file_path
                }
                supabase.table("klachten").insert(data).execute()
                st.success("Verzonden!")
            except Exception as e:
                st.error(f"Fout: {e}")
