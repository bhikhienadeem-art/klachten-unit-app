import streamlit as st
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .header-bar { 
        background-color: #004a99; color: white; padding: 20px; text-align: center; 
        border: 5px solid #ffcc00; margin-bottom: 20px; 
    }
    .contact-info { font-size: 14px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="contact-info">
            📍 Tawajariweg #20 | 📞 366660 / 366929 | 💬 8921062 <br>
            📧 klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN ---
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

# --- DASHBOARD & FORMULIER LOGICA ---
if st.session_state.logged_in:
    if st.session_state.rol == 'admin':
        tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Medewerker Beheer"])
        
        with tab1:
            st.title("📊 Dashboard")
            try:
                klachten = supabase.table("klachten").select("*").execute().data
                for k in klachten:
                    with st.expander(f"Klacht van: {k.get('volledige_naam', 'Anoniem')} - Status: {k.get('status', 'Nieuw')}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**ID Nummer:** {k.get('id_nummer', '-')}")
                            st.write(f"**E-mail:** {k.get('email', '-')}")
                        with col_b:
                            st.write(f"**Telefoon:** {k.get('telefoon_whatsapp', '-')}")
                            st.write(f"**Adres:** {k.get('adres', '-')}")
                        
                        st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                        
                        # Status wijzigen
                        nieuwe_status = st.selectbox("Status wijzigen", ["Nieuw", "In behandeling", "Afgehandeld"], 
                                                     index=["Nieuw", "In behandeling", "Afgehandeld"].index(k.get('status', 'Nieuw')), 
                                                     key=f"status_{k['id']}")
                        
                        if st.button("Update Status", key=f"upd_{k['id']}"):
                            supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                            st.rerun()

                        # Interne notitie
                        notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                        if st.button("Opslaan Notitie", key=f"save_{k['id']}"):
                            supabase.table("klachten").update({"interne_notitie": notitie}).eq("id", k['id']).execute()
                            st.success("Notitie opgeslagen")
                        
                        # Email sturen
                        if k.get('email'):
                            st.markdown(f'<a href="mailto:{k["email"]}?subject=Update over uw klacht&body=Geachte {k["volledige_naam"]}," style="text-decoration:none; color:white; background:#004a99; padding:8px 12px; border-radius:5px;">📧 E-mail sturen naar client</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Kon klachten niet ophalen.")
        
        with tab2:
            st.subheader("Medewerker Beheer")
    else:
        st.title("Dashboard (Medewerker)")
else:
    # --- PUBLIEK FORMULIER ---
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
            try:
                data = {
                    "volledige_naam": naam,
                    "id_nummer": id_nr, 
                    "email": email,
                    "adres": adres,
                    "telefoon_whatsapp": telefoon,
                    "klachtensoort": soort,
                    "omschrijving": omschrijving,
                    "status": "Nieuw"
                }
                supabase.table("klachten").insert(data).execute()
                st.success("Klacht succesvol verzonden!")
            except Exception as e:
                st.error(f"Fout: {e}")
