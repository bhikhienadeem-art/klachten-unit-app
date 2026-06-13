import streamlit as st
import hashlib
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExNjI4MDgsImV4cCI6MjA5NjczODgwOH0.JxBByUdNydkVc4FQ0Eg5fvO3ERi13LvJHKHuJPH83uk" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS & HEADER ---
st.markdown("""
    <style>
    .header-bar { 
        background-color: #004a99; 
        color: white; 
        padding: 40px 20px; 
        text-align: center; 
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-bottom: 30px;
    }
    .main-title { font-size: 32px; font-weight: bold; margin-bottom: 15px; }
    .sub-text { font-size: 18px; line-height: 1.5; max-width: 800px; margin: 0 auto; }
    .contact-line { font-size: 14px; margin-top: 20px; color: #e0e0e0; }
    
    /* Blauwe zijbalk aanpassing */
    [data-testid="stSidebar"] {
        background-color: #004a99 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] input {
        background-color: white !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <div class="main-title">Welkom op de pagina van het Klachtenunit van het Commissariaat Wanica Centrum</div>
        <div class="sub-text">Wij vinden het belangrijk dat uw stem gehoord wordt. Via deze pagina kunt u uw klacht of opmerking indienen en, indien gewenst, een mogelijke oplossing voorstellen.</div>
        <div class="contact-line">
            📍 Tawajariweg #20 | 📞 366660 / 366929 | 💬 8921062 | 📧 klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN & SIDEBAR ---
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

# --- FORMULIER & DASHBOARD ---
if st.session_state.logged_in:
    st.title("📊 Dashboard Ingekomen Klachten")
    klachten_data = supabase.table("klachten").select("*").execute().data
    
    for k in klachten_data:
        with st.expander(f"Klacht van: {k['volledige_naam']} ({k['klachtensoort']})"):
            st.write(f"**Adres:** {k['adres']} | **ID:** {k['id_nummer']} | **Tel:** {k['telefoon_whatsapp']}")
            st.write(f"**Email:** {k['email']}")
            st.write(f"**Omschrijving:** {k['omschrijving']}")
            if k['bijlage_url']: st.markdown(f"[Bekijk bijlage]({k['bijlage_url']})")
            
            nieuwe_status = st.selectbox(
                "Status wijzigen", 
                ["Nieuw", "Door gestuurd naar de desbetreffende afdeling", "In behandeling", "Afgehandeld"],
                index=["Nieuw", "Door gestuurd naar de desbetreffende afdeling", "In behandeling", "Afgehandeld"].index(k['status'])
            )
            
            if st.button(f"Update status voor {k['volledige_naam']}", key=k['id']):
                supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                st.success("Status bijgewerkt!")
                st.rerun()
else:
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            id_nr = st.text_input("ID Nummer")
            email = st.text_input("E-mailadres")
        with col2:
            adres = st.text_input("Adres")
            telefoon = st.text_input("Telefoon/Whatsapp")
            soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        
        omschrijving = st.text_area("Omschrijving")
        bestand = st.file_uploader("Voeg bijlage toe (foto/PDF)", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Verstuur klacht"):
            url = None
            fout = False
            if bestand:
                try:
                    bestandsnaam = f"{uuid.uuid4()}_{bestand.name}"
                    supabase.storage.from_("klachten-bijlagen").upload(bestandsnaam, bestand.getvalue())
                    url = f"{SUPABASE_URL}/storage/v1/object/public/klachten-bijlagen/{bestandsnaam}"
                except Exception as e:
                    st.error(f"Fout bij uploaden: {e}")
                    fout = True
            
            if not fout:
                data = {
                    "volledige_naam": naam, "id_nummer": id_nr, "adres": adres,
                    "telefoon_whatsapp": telefoon, "email": email, "klachtensoort": soort,
                    "omschrijving": omschrijving, "bijlage_url": url, "status": "Nieuw"
                }
                try:
                    supabase.table("klachten").insert(data).execute()
                    st.success("Uw klacht is succesvol verzonden!")
                except Exception as e:
                    st.error(f"Database fout: {e}")
