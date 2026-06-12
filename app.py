import streamlit as st
import hashlib
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "sb_publishable_XnTLlOfaR0bfZ_gFXlOnuw_zxOi87kb"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- FUNCTIES ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    pw_hash = hash_password(password)
    try:
        response = supabase.table("gebruikers").select("*").eq("username", username).eq("password_hash", pw_hash).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        return None
    return None

def toon_admin_gebruikers_beheer():
    st.subheader("👥 Gebruikersbeheer")
    with st.form("add_user_form"):
        new_user = st.text_input("Nieuwe Gebruikersnaam")
        new_pw = st.text_input("Wachtwoord", type="password")
        new_role = st.selectbox("Rol", ["medewerker", "admin"])
        if st.form_submit_button("Voeg gebruiker toe"):
            pw_hash = hash_password(new_pw)
            supabase.table("gebruikers").insert({"username": new_user, "password_hash": pw_hash, "role": new_role}).execute()
            st.success("Gebruiker toegevoegd!")
            st.rerun()
    
    st.write("### Huidige Gebruikers")
    users = supabase.table("gebruikers").select("id, username, role").execute()
    st.table(users.data)

def toon_medewerker_paneel():
    st.subheader("📋 Klachten Overzicht")
    response = supabase.table("klachten").select("*").execute()
    klachten = response.data
    
    if not klachten:
        st.info("Geen klachten gevonden.")
        return

    for k in klachten:
        with st.expander(f"Klacht van: {k['volledige_naam']} | Status: {k.get('status', 'Nieuw')}"):
            st.write(f"**Omschrijving:** {k['omschrijving']}")
            new_status = st.selectbox("Status wijzigen", ["Nieuw", "In Behandeling", "Afgehandeld"], key=f"s_{k['id']}")
            reactie = st.text_area("Reactie", value=k.get('reactie_medewerker', ''), key=f"r_{k['id']}")
            if st.button("Opslaan", key=f"b_{k['id']}"):
                supabase.table("klachten").update({"status": new_status, "reactie_medewerker": reactie}).eq("id", k['id']).execute()
                st.success("Opgeslagen!")
                st.rerun()

# --- APP LOGICA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# Sidebar voor inloggen
with st.sidebar:
    if not st.session_state.logged_in:
        st.markdown("### 🔐 Medewerker Login")
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            user_data = check_login(user, pw)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.user_data = user_data
                st.rerun()
            else:
                st.error("Onjuiste gegevens")
    else:
        st.write(f"Ingelogd als: {st.session_state.user_data['username']}")
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()

# Hoofdscherm
if st.session_state.logged_in:
    rol = st.session_state.user_data['role']
    st.title(f"Dashboard - {rol.capitalize()}")
    if rol == "admin":
        menu = st.sidebar.radio("Beheer", ["Klachten", "Gebruikers"])
        if menu == "Klachten": toon_medewerker_paneel()
        else: toon_admin_gebruikers_beheer()
    else:
        toon_medewerker_paneel()
else:
    st.title("Welkom bij de Klachten Unit Wanica Centrum")
    st.write("Dien hieronder je klacht in:")
    with st.form("klacht_form"):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving klacht")
        if st.form_submit_button("Verstuur klacht"):
            if naam and omschrijving:
                supabase.table("klachten").insert({"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
                st.success("Klacht verstuurd!")
            else:
                st.error("Vul alle velden in.")
