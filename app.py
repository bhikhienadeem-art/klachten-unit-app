import streamlit as st
import hashlib
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "sb_publishable_XnTLlOfaR0bfZ_gFXlOnuw_zxOi87kb"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #004a99; }
    [data-testid="stSidebar"] * { color: white !important; }
    header[data-testid="stHeader"] { background-color: #004a99; }
    .title-style { color: #004a99; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIES ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    pw_hash = hash_password(password)
    try:
        response = supabase.table("gebruikers").select("*").eq("username", username).eq("password_hash", pw_hash).execute()
        if response.data: return response.data[0]
    except: return None
    return None

# --- STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- ZIJKANT (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🔐 Medewerker Login")
    if not st.session_state.logged_in:
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            data = check_login(user, pw)
            if data:
                st.session_state.logged_in = True
                st.session_state.user_data = data
                st.rerun()
            else: st.error("Onjuiste gegevens")
    else:
        st.write(f"Ingelogd als: {st.session_state.user_data['username']}")
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📞 Contactgegevens")
    st.write("📍 **Adres:** Wanica Centrum")
    st.write("📱 **WhatsApp:** +597 8123456")
    st.write("☎️ **Telefoon:** 597 123456")
    st.write("📧 **E-mail:** info@wanica.sr")

# --- HOOFDPROGRAMMA ---
if st.session_state.logged_in:
    st.title("Dashboard")
    st.write("Welkom in het beheersysteem.")
else:
    st.markdown("<h1 class='title-style'>Welkom bij de Klachten Unit Wanica Centrum</h1>", unsafe_allow_html=True)
    st.write("Dien hieronder je klacht in:")
    
    with st.form("klacht_form"):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            email = st.text_input("E-mailadres")
        with col2:
            telefoon = st.text_input("Telefoonnummer")
            onderwerp = st.selectbox("Onderwerp", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        
        omschrijving = st.text_area("Omschrijving van je klacht")
        submit = st.form_submit_button("Verstuur klacht")
        
        if submit:
            if naam and omschrijving:
                supabase.table("klachten").insert({
                    "volledige_naam": naam, "email": email, "telefoon": telefoon, 
                    "onderwerp": onderwerp, "omschrijving": omschrijving, "status": "Nieuw"
                }).execute()
                st.success("Klacht succesvol verstuurd!")
            else: st.error("Vul alstublieft alle velden in.")
