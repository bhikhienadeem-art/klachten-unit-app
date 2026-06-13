import streamlit as st
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
# Vul hier je nieuwe, geregenereerde anon publieke sleutel in
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "PLAK_HIER_JE_NIEUWE_ANON_SLEUTEL" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { padding-top: 0rem; }
    .header-bar { 
        background-color: #004a99; color: white; padding: 40px 20px; 
        text-align: center; width: 100vw; margin-left: calc(-50vw + 50%);
        margin-bottom: 30px;
    }
    .main-title { font-size: 32px; font-weight: bold; margin-bottom: 15px; }
    [data-testid="stSidebar"] { background-color: #004a99 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
""", unsafe_html=True)

st.markdown("""
    <div class="header-bar">
        <div class="main-title">Welkom bij het Klachtenunit van het Commissariaat Wanica Centrum</div>
    </div>
""", unsafe_html=True)

# --- LOGIN ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    user = st.text_input("Gebruikersnaam")
    pw = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if user == "admin" and pw == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Ongeldige gegevens")

# --- LOGICA ---
if st.session_state.logged_in:
    st.title("📊 Dashboard Ingekomen Klachten")
    try:
        response = supabase.table("klachten").select("*").execute()
        data = response.data
        if not data: st.info("Geen klachten gevonden.")
        else:
            for k in data:
                with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')}"):
                    st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                    st.write(f"**Status:** {k.get('status', 'Nieuw')}")
                    
                    nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], key=f"s_{k['id']}")
                    if st.button("Update", key=f"b_{k['id']}"):
                        supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                        st.rerun()
    except Exception as e: st.error(f"Fout: {e}")
else:
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving")
        if st.form_submit_button("Verstuur"):
            data = {"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}
            try:
                supabase.table("klachten").insert(data).execute()
                st.success("Klacht verzonden!")
            except Exception as e: st.error(f"Database fout: {e}")
