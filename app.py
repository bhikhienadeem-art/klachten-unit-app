import streamlit as st
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER MET GOUDEN RAND EN CONTACTGEGEVENS ---
st.markdown("""
    <style>
    .header-bar { 
        background-color: #004a99; 
        color: white; 
        padding: 25px; 
        text-align: center; 
        border: 5px solid #ffcc00; 
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .contact-info {
        font-size: 0.9em;
        margin-top: 10px;
        opacity: 0.9;
    }
    </style>
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="contact-info">
            📍 Indira Gandhiweg | 📞 (+597) 584xxx | ✉️ klachten.wanica@gov.sr
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN LOGICA ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
    st.session_state.rol = None

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    gebruiker = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        if gebruiker == "admin" and wachtwoord == "admin123":
            st.session_state.logged_in = True
            st.session_state.rol = 'admin'
            st.rerun()

# --- DASHBOARD (Alleen voor admins) ---
if st.session_state.logged_in and st.session_state.rol == 'admin':
    st.title("📊 Dashboard")
    try:
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')} - Status: {k.get('status', 'Nieuw')}"):
                st.write(f"**ID:** {k.get('id_nummer', '-')} | **Tel:** {k.get('telefoon_whatsapp', '-')}")
                st.write(f"**Email:** {k.get('email', '-')} | **Adres:** {k.get('adres', '-')}")
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                if st.button("Opslaan Notitie", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({"interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.success("Notitie opgeslagen!")
                
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], 
                                             index=["Nieuw", "In behandeling", "Afgehandeld"].index(k.get('status', 'Nieuw')), 
                                             key=f"status_{k['id']}")
                if st.button("Update Status", key=f"upd_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()
    except Exception:
        st.error("Kon klachten niet inladen.")

# --- FORMULIER (Altijd zichtbaar) ---
st.divider()
st.title("Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("Volledige naam")
        id_nr = st.text_input("ID Nummer")
        email = st.text_input("E-mailadres")
    with col2:
        adres = st.text_input("Woonadres")
        telefoon = st.text_input("Telefoon/Whatsapp")
        soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
    
    omschrijving = st.text_area("Omschrijving")
    
    if st.form_submit_button("Verstuur klacht"):
        data = {
            "volledige_naam": naam, "id_nummer": id_nr, "email": email,
            "adres": adres, "telefoon_whatsapp": telefoon,
            "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw"
        }
        supabase.table("klachten").insert(data).execute()
        st.success("Klacht succesvol verzonden!")
