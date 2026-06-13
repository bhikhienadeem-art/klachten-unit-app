import streamlit as st
import hashlib
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExNjI4MDgsImV4cCI6MjA5NjczODgwOH0.JxBByUdNydkVc4FQ0Eg5fvO3ERi13LvJHKHuJPH83uk" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS & HEADER ---
st.markdown("""
    <style>
    .header-bar { 
        background-color: #004a99; 
        color: white; 
        padding: 25px; 
        border-radius: 10px; 
        margin-bottom: 20px; 
        text-align: center; 
    }
    .contact-info {
        font-size: 15px;
        margin-top: 10px;
        line-height: 1.8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <h1>Klachten Unit Wanica Centrum</h1>
        <div class="contact-info">
            📍 Adres: Tawajariweg #20, Lelydorp <br>
            📞 Tel: +597 366660 / +597 366929 <br>
            💬 WhatsApp: +597 8921062 <br>
            📧 E-mail: klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar"><h2>Klachten Unit Wanica Centrum</h2></div>', unsafe_allow_html=True)

# --- LOGIN ---
def check_login(username, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        response = supabase.table("gebruikers").select("*").eq("username", username).execute()
        return response.data[0] if (response.data and response.data[0]['password_hash'] == pw_hash) else None
    except: return None

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- FORMULIER & DASHBOARD ---
if st.session_state.logged_in:
    st.title("DASHBOARD")
    klachten = supabase.table("klachten").select("*").execute().data
    st.write(klachten)
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
                    # Gebruik de juiste bucketnaam: klachten-bijlagen
                    supabase.storage.from_("klachten-bijlagen").upload(bestandsnaam, bestand.getvalue())
                    url = f"{SUPABASE_URL}/storage/v1/object/public/klachten-bijlagen/{bestandsnaam}"
                except Exception as e:
                    st.error(f"Fout bij uploaden: {e}")
                    fout = True
            
            if not fout:
                data = {
                    "volledige_naam": naam,
                    "id_nummer": id_nr,
                    "adres": adres,
                    "telefoon_whatsapp": telefoon,
                    "email": email,
                    "klachtensoort": soort,
                    "omschrijving": omschrijving,
                    "bijlage_url": url,
                    "status": "Nieuw"
                }
                try:
                    supabase.table("klachten").insert(data).execute()
                    st.success("Uw klacht is succesvol verzonden!")
                except Exception as e:
                    st.error(f"Database fout: {e}")
