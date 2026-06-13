import streamlit as st
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

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
        response = supabase.table("klachten").select("*").execute()
        klachten = response.data
        
        for k in klachten:
            with st.expander(f"Klacht van: {k.get('volledige_naam', 'Anoniem')} - Status: {k.get('status', 'Nieuw')}"):
                # 1. Alle gegevens tonen
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID Nummer:** {k.get('id_nummer', '-')}")
                    st.write(f"**E-mail:** {k.get('email', '-')}")
                with col2:
                    st.write(f"**Telefoon:** {k.get('telefoon_whatsapp', '-')}")
                    st.write(f"**Adres:** {k.get('adres', '-')}")
                st.write(f"**Soort klacht:** {k.get('klachtensoort', '-')}")
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                
                st.divider()

                # 2. Status wijzigen
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], 
                                             index=["Nieuw", "In behandeling", "Afgehandeld"].index(k.get('status', 'Nieuw')), 
                                             key=f"status_{k['id']}")
                if st.button("Update Status", key=f"upd_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()

                # 3. Interne notitie (alleen voor admin/medewerker)
                oude_notitie = k.get('interne_notitie', '')
                notitie = st.text_area("Interne notitie", value=oude_notitie, key=f"note_{k['id']}")
                if st.button("Opslaan Notitie", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({"interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.success("Notitie opgeslagen!")
                
                # 4. E-mail sturen
                if k.get('email'):
                    email_link = f"mailto:{k['email']}?subject=Update over uw klacht bij Wanica Centrum&body=Geachte {k['volledige_naam']},%0A%0AHierbij een update over uw ingediende klacht.%0A%0AMet vriendelijke groet,%0AKlachtenunit Wanica"
                    st.markdown(f'<a href="{email_link}" target="_blank" style="text-decoration:none; color:white; background:#004a99; padding:10px; border-radius:5px;">📧 E-mail naar klant sturen</a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fout bij het laden van klachten: {e}")
