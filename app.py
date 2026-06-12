import streamlit as st
import hashlib
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "sb_publishable_XnTLlOfaR0bfZ_gFXlOnuw_zxOi87kb"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- STYLING (Blauwe zijbalk behouden) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #004a99; }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-title { color: #004a99; }
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

# --- APP LOGICA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# ZIJKANT: Inloggen
with st.sidebar:
    if not st.session_state.logged_in:
        st.markdown("### 🔐 Medewerker Login")
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
        st.write(f"Ingelogd: {st.session_state.user_data['username']}")
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.rerun()

# HOOFDSCHERM: Dashboard OF Publiek Formulier
if st.session_state.logged_in:
    st.title("Medewerker Dashboard")
    # Hier kun je de functies voor klachtenbeheer aanroepen
    st.write("Je bent ingelogd. Gebruik de database om klachten af te handelen.")
else:
    # HET KLACHTEN FORMULIER (Zoals je het had)
    st.markdown("<h1 class='main-title'>Welkom bij de Klachten Unit Wanica Centrum</h1>", unsafe_allow_html=True)
    st.write("Dien hieronder je klacht in:")
    with st.form("klacht_form"):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving van je klacht")
        if st.form_submit_button("Verstuur klacht"):
            if naam and omschrijving:
                supabase.table("klachten").insert({"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
                st.success("Klacht verstuurd!")
            else: st.warning("Vul alle velden in.")
