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
    [data-testid="stSidebar"] input { color: black !important; }
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
        response = supabase.table("gebruikers").select("*").eq("username", username).execute()
        if response.data:
            if response.data[0]['password_hash'] == pw_hash:
                return response.data[0]
    except Exception as e:
        st.error(f"Fout: {e}")
    return None

# --- STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- ZIJKANT (LOGIN) ---
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
            else:
                st.error("Onjuiste gegevens")
    else:
        st.write(f"Ingelogd als: {st.session_state.user_data['username']}")
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.rerun()

# --- HOOFDPROGRAMMA ---
if st.session_state.logged_in:
    st.title("Dashboard: Binnengekomen Klachten")
    try:
        # Hier halen we de klachten op
        response = supabase.table("klachten").select("*").order("id", desc=True).execute()
        klachten = response.data
        
        if klachten:
            for k in klachten:
                # We gebruiken .get() om te voorkomen dat de app crasht bij missende data
                onderwerp = k.get('onderwerp', 'Geen onderwerp')
                with st.expander(f"Klacht #{k.get('id')} - {onderwerp}"):
                    st.write(f"**Naam:** {k.get('volledige_naam')}")
                    st.write(f"**Omschrijving:** {k.get('omschrijving')}")
                    if st.button(f"Markeer als afgehandeld", key=f"btn_{k['id']}"):
                        supabase.table("klachten").update({"status": "Afgehandeld"}).eq("id", k['id']).execute()
                        st.rerun()
        else:
            st.info("Geen klachten gevonden.")
    except Exception as e:
        st.error(f"Fout bij laden van data: {e}")
else:
    # --- FORMULIER ---
    st.markdown("<h1 class='title-style'>Welkom bij de Klachten Unit Wanica</h1>", unsafe_allow_html=True)
    with st.form("klacht_form"):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            email = st.text_input("E-mailadres")
        with col2:
            telefoon = st.text_input("Telefoonnummer")
            onderwerp = st.selectbox("Onderwerp", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        
        if st.form_submit_button("Verstuur klacht"):
            supabase.table("klachten").insert({
                "volledige_naam": naam, "email": email, "telefoon": telefoon, 
                "onderwerp": onderwerp, "omschrijving": omschrijving, "status": "Nieuw"
            }).execute()
            st.success("Uw klacht is verstuurd!")
