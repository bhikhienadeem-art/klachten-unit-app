import streamlit as st
import hashlib
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "PLAK_HIER_JE_ANON_API_SLEUTEL" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS VOOR HET ONTWERP ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .klacht-box { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #004a99; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
def check_login(username, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        response = supabase.table("gebruikers").select("*").eq("username", username).execute()
        if response.data and response.data[0]['password_hash'] == pw_hash:
            return response.data[0]
    except: return None
    return None

if "logged_in" not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.markdown("### 🔐 Medewerker Panel")
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
        if st.button("Uitloggen"): st.session_state.logged_in = False; st.rerun()

# --- HOOFDPROGRAMMA ---
if st.session_state.logged_in:
    st.title("DASHBOARD OVERZICHT")
    
    # Statistieken rij
    c1, c2, c3, c4 = st.columns(4)
    klachten = supabase.table("klachten").select("*").execute().data
    nieuw = len([k for k in klachten if k.get('status') == 'Nieuw'])
    c1.metric("Totaal Nieuw", nieuw)
    c2.metric("In Behandeling", "15") # Voorbeeldwaarde
    c3.metric("Afgehandeld", len([k for k in klachten if k.get('status') == 'Afgehandeld']))
    c4.metric("Gem. Reactietijd", "2.5 d")

    st.markdown("---")
    
    # Klachtenlijst
    for k in klachten:
        with st.container():
            st.markdown(f"**DETAILS KLACHT #{k.get('id')}**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"👤 **Naam:** {k.get('volledige_naam')}")
                st.write(f"📧 **E-mail:** {k.get('email')}")
            with col_b:
                st.write(f"🏷️ **Onderwerp:** {k.get('onderwerp')}")
                st.write(f"Status: {k.get('status')}")
            
            st.write(f"**Omschrijving:** {k.get('omschrijving')}")
            if k.get('bestands_url'): st.markdown(f"[🔗 Bekijk bijlage]({k['bestands_url']})")
            
            if st.button("Markeer als afgehandeld", key=f"btn_{k['id']}"):
                supabase.table("klachten").update({"status": "Afgehandeld"}).eq("id", k['id']).execute()
                st.rerun()
            st.markdown("---")
else:
    # Formulier (zoals eerder)
    st.title("Welkom bij de Klachten Unit Wanica")
    # ... (formulier code hier invullen) ...
