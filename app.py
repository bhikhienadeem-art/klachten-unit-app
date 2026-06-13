import streamlit as st
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExNjI4MDgsImV4cCI6MjA5NjczODgwOH0.JxBByUdNydkVc4FQ0Eg5fvO3ERi13LvJHKHuJPH83uk" 
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
    [data-testid="stSidebar"] { background-color: #004a99 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
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

# --- DASHBOARD & FORMULIER ---
if st.session_state.logged_in:
    st.title("📊 Dashboard Ingekomen Klachten")
    try:
        response = supabase.table("klachten").select("*").execute()
        klachten = response.data
        if not klachten: st.info("Geen klachten gevonden.")
        for k in klachten:
            with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                st.write(f"**Status:** {k.get('status', 'Nieuw')}")
                if st.button("Markeer als Afgehandeld", key=f"btn_{k['id']}"):
                    supabase.table("klachten").update({"status": "Afgehandeld"}).eq("id", k['id']).execute()
                    st.rerun()
    except Exception as e: st.error(f"Fout bij ophalen: {e}")
else:
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving")
        if st.form_submit_button("Verstuur klacht"):
            try:
                supabase.table("klachten").insert({"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
                st.success("Uw klacht is succesvol verzonden naar het Commissariaat.")
            except Exception as e: st.error(f"Database fout: {e}")
