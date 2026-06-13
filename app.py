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
    .header-bar { 
        background-color: #004a99; color: white; padding: 20px; text-align: center; 
        border: 5px solid #ffcc00; margin-bottom: 20px; 
    }
    .contact-info { font-size: 14px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
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
    gebruiker = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if gebruiker == "admin" and wachtwoord == "admin123":
            st.session_state.logged_in = True
            st.session_state.rol = 'admin'
            st.rerun()

# --- DASHBOARD & FORMULIER ---
if st.session_state.logged_in:
    if st.session_state.rol == 'admin':
        tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Medewerker Beheer"])
        with tab1:
            st.title("Dashboard")
        with tab2:
            st.subheader("Medewerker Beheer")
    else:
        st.title("Dashboard (Medewerker)")
else:
    # --- PUBLIEK FORMULIER MET UPLOAD ---
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            email = st.text_input("E-mailadres")
        with col2:
            telefoon = st.text_input("Telefoon/Whatsapp")
            soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        
        omschrijving = st.text_area("Omschrijving")
        uploaded_file = st.file_uploader("Voeg bijlage toe", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Verstuur klacht"):
            try:
                # Bestand upload logica
                file_path = None
                if uploaded_file:
                    file_path = f"bijlagen/{uuid.uuid4()}_{uploaded_file.name}"
                    supabase.storage.from_("klachten-bijlagen").upload(file_path, uploaded_file.getvalue())
                
                data = {
                    "volledige_naam": naam, "email": email, "telefoon_whatsapp": telefoon, 
                    "klachtensoort": soort, "omschrijving": omschrijving, "bijlagen": file_path
                }
                supabase.table("klachten").insert(data).execute()
                st.success("Verzonden!")
            except Exception as e:
                st.error(f"Fout: {e}")
