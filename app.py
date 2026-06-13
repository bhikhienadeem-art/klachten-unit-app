import streamlit as st
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER ---
st.markdown("""
    <style>
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    .contact-info { font-size: 0.95em; margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); }
    </style>
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="contact-info">
            📍 <b>Adres:</b> Indira Gandhiweg | 📞 <b>Tel:</b> (+597) 584xxx | 💬 <b>WhatsApp:</b> (+597) 8xxx-xxx | ✉️ <b>E-mail:</b> klachten.wanica@gov.sr
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN & NAVIGATIE ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Ongeldige gegevens")
    else:
        st.success("Ingelogd als Admin")
        menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if menu == "Dashboard":
        st.title("📊 Dashboard")
        try:
            klachten = supabase.table("klachten").select("*").execute().data
            for k in klachten:
                with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')} - Status: {k.get('status', 'Nieuw')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {k.get('id_nummer', '-')}")
                        st.write(f"**Naam:** {k.get('volledige_naam', '-')}")
                        st.write(f"**E-mail:** {k.get('email', '-')}")
                    with col2:
                        st.write(f"**Telefoon:** {k.get('telefoon_whatsapp', '-')}")
                        st.write(f"**Adres:** {k.get('adres', '-')}")
                        st.write(f"**Soort:** {k.get('klachtensoort', '-')}")
                    st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                    
                    notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                    if st.button("Opslaan Notitie", key=f"save_{k['id']}"):
                        supabase.table("klachten").update({"interne_notitie": notitie}).eq("id", k['id']).execute()
                        st.success("Notitie opgeslagen!")
                    
                    status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                    huidige_status = k.get('status', 'Nieuw')
                    nieuwe_status = st.selectbox("Status", status_opties, index=status_opties.index(huidige_status) if huidige_status in status_opties else 0, key=f"status_{k['id']}")
                    if st.button("Update Status", key=f"upd_{k['id']}"):
                        supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                        st.rerun()
                    
                    if k.get('email'):
                        mail_link = f"mailto:{k['email']}?subject=Update over uw klacht {k.get('id_nummer', '')}&body=Beste {k.get('volledige_naam', 'cliënt')},%0A%0AHierbij een update over uw klacht..."
                        st.markdown(f'<a href="{mail_link}" target="_blank" style="padding:10px; background:#004a99; color:white; border-radius:5px; text-decoration:none;">📧 E-mail verzenden naar cliënt</a>', unsafe_allow_html=True)
                    else:
                        st.warning("Geen e-mailadres beschikbaar voor deze cliënt.")
        except Exception as e:
            st.error(f"Fout bij het laden van het dashboard: {e}")

    elif menu == "Rapporten":
        st.title("📈 Rapporten")
        st.selectbox("Type rapport", ["Wekelijks", "Maandelijks"])
        st.button("Genereer & Download Rapport")

    elif menu == "Instellingen":
        st.title("⚙️ Instellingen")
        tab1, tab2 = st.tabs(["Gebruikers", "Rollen"])
        with tab1:
            st.text_input("Nieuwe medewerker")
            st.button("Toevoegen")
        with tab2:
            st.write("Beheer rollen hier.")

# --- FORMULIER ---
st.divider()
st.title("Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("Volledige naam")
        id_nr = st.text_input("ID Nummer")
    with col2:
        email = st.text_input("E-mailadres")
        soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
    omschrijving = st.text_area("Omschrijving")
    upload = st.file_uploader("Upload bestand", type=['png', 'jpg', 'pdf'])
    
    if st.form_submit_button("Verstuur klacht"):
        supabase.table("klachten").insert({"volledige_naam": naam, "id_nummer": id_nr, "email": email, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
        st.success("Verzonden!")
