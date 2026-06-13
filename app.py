import streamlit as st
import hashlib
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
# Let op: Zorg dat de URL en de KEY tussen aanhalingstekens staan
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "PLAK_HIER_JE_ANON_API_SLEUTEL" 
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

# --- LOGIN FUNCTIE ---
def check_login(username, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        response = supabase.table("gebruikers").select("*").eq("username", username).execute()
        if response.data and response.data[0]['password_hash'] == pw_hash:
            return response.data[0]
    except: return None
    return None

# --- STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- ZIJKANT ---
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
        st.write(f"Ingelogd: {st.session_state.user_data.get('username')}")
        if st.button("Log uit"): st.session_state.logged_in = False; st.rerun()

# --- HOOFDPROGRAMMA ---
if st.session_state.logged_in:
    st.title("Dashboard: Binnengekomen Klachten")
    try:
        klachten = supabase.table("klachten").select("*").order("id", desc=True).execute().data
        if klachten:
            for k in klachten:
                with st.expander(f"Klacht #{k.get('id', 'N/A')} - {k.get('onderwerp', 'Geen onderwerp')}"):
                    st.write(f"**Naam:** {k.get('volledige_naam')}")
                    st.write(f"**Omschrijving:** {k.get('omschrijving')}")
                    if k.get('bestands_url'): st.markdown(f"[Bekijk bijlage]({k['bestands_url']})")
                    if st.button("Afgehandeld", key=f"done_{k['id']}"):
                        supabase.table("klachten").update({"status": "Afgehandeld"}).eq("id", k['id']).execute()
                        st.rerun()
        else: st.info("Geen klachten gevonden.")
    except Exception as e: st.error(f"Fout: {e}")
else:
    # --- FORMULIER ---
    st.markdown("<h1 class='title-style'>Welkom bij de Klachten Unit Wanica</h1>", unsafe_allow_html=True)
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            email = st.text_input("E-mailadres")
        with col2:
            telefoon = st.text_input("Telefoonnummer")
            onderwerp = st.selectbox("Onderwerp", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        bestand = st.file_uploader("Voeg foto of document toe", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Verstuur klacht"):
            url = None
            if bestand:
                bestandsnaam = f"{uuid.uuid4()}_{bestand.name}"
                supabase.storage.from_("klacht-bestanden").upload(bestandsnaam, bestand.getvalue())
                url = f"{SUPABASE_URL}/storage/v1/object/public/klacht-bestanden/{bestandsnaam}"
            
            supabase.table("klachten").insert({
                "volledige_naam": naam, "email": email, "telefoon": telefoon, 
                "onderwerp": onderwerp, "omschrijving": omschrijving, "status": "Nieuw", "bestands_url": url
            }).execute()
            st.success("Uw klacht is verzonden!")
