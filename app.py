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
    st.session_state.page = "Dashboard"

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
            else:
                st.error("Onjuiste gegevens")
    else:
        st.write(f"Ingelogd als: {st.session_state.user_data['username']}")
        st.markdown("---")
        if st.button("Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
        if st.session_state.user_data.get('role') == 'admin':
            if st.button("Admin: Gebruikersbeheer"): st.session_state.page = "Admin"; st.rerun()
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.rerun()

# --- HOOFDPROGRAMMA ---
if st.session_state.logged_in:
    
    # 1. Dashboard Sectie
    if st.session_state.page == "Dashboard":
        st.title("Dashboard: Binnengekomen Klachten")
        klachten = supabase.table("klachten").select("*").order("id", desc=True).execute().data
        
        if klachten:
            for k in klachten:
                with st.expander(f"Klacht #{k.get('id')} - {k.get('onderwerp')} ({k.get('status')})"):
                    st.write(f"**Naam:** {k.get('volledige_naam')}")
                    st.write(f"**E-mail:** {k.get('email')}")
                    st.link_button("Stuur E-mail naar cliënt", f"mailto:{k.get('email')}?subject=Reactie op uw klacht")
                    
                    notitie = st.text_area("Voeg interne notitie toe", key=f"note_{k['id']}")
                    if st.button("Opslaan", key=f"btn_note_{k['id']}"):
                        supabase.table("interne_notities").insert({"klacht_id": k['id'], "notitie": notitie, "auteur": st.session_state.user_data['username']}).execute()
                        st.success("Notitie opgeslagen!")
                    
                    if k.get('status') != "Afgehandeld":
                        if st.button("Markeer als afgehandeld", key=f"done_{k['id']}"):
                            supabase.table("klachten").update({"status": "Afgehandeld"}).eq("id", k['id']).execute()
                            st.rerun()

    # 2. Admin Sectie
    elif st.session_state.page == "Admin" and st.session_state.user_data.get('role') == 'admin':
        st.title("Gebruikersbeheer")
        gebruikers = supabase.table("gebruikers").select("*").execute().data
        for g in gebruikers:
            col1, col2 = st.columns([3, 1])
            col1.write(f"{g['username']} - Rol: {g['role']}")
            if col2.button("Verwijder", key=f"del_{g['id']}"):
                supabase.table("gebruikers").delete().eq("id", g['id']).execute()
                st.rerun()

else:
    # Publieke inzend-pagina
    st.markdown("<h1 class='title-style'>Welkom bij de Klachten Unit Wanica</h1>", unsafe_allow_html=True)
    with st.form("klacht_form"):
        # ... (je formulier code) ...
        if st.form_submit_button("Verstuur"):
            st.success("Verstuurd!")
