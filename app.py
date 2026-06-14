import streamlit as st
import pandas as pd
import plotly.express as px
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
    .header-text { margin-top: 10px; font-size: 1.1em; font-style: italic; }
    .contact-info { font-size: 0.95em; margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); }
    </style>
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="header-text">
            Welkom op de pagina van het Klachtenunit van het Commissariaat Wanica Centrum.<br>
            Wij vinden het belangrijk dat uw stem gehoord wordt. Via deze pagina kunt u uw klacht of opmerking indienen.
        </div>
        <div class="contact-info">
            📍 <b>Adres:</b> Tawajarieweg 20 | 📞 <b>Tel:</b> (+597) 366660 | ✉️ <b>E-mail:</b> klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

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
        st.success("Ingelogd als Admin")
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        response = supabase.table("klachten").select("*").execute()
        klachten = response.data
        
        for k in klachten:
            with st.expander(f"Klacht: {k.get('volledige_naam', 'Anoniem')} - Status: {k.get('status', 'Nieuw')}"):
                st.write(f"**E-mail:** {k.get('email', '-')}")
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                if k.get('email'):
                    st.markdown(f'<a href="mailto:{k["email"]}">📧 E-mail cliënt</a>', unsafe_allow_html=True)

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Beheer")
        response = supabase.table("klachten").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            st.subheader("Verdeling per Klachtensoort")
            fig = px.pie(df, names='klachtensoort', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig)
            st.dataframe(df)
            
            st.subheader("🗑️ Klacht Verwijderen")
            target_id = st.selectbox("Selecteer ID om te verwijderen", df['id'].tolist())
            if st.button("Verwijder geselecteerde klacht"):
                supabase.table("klachten").delete().eq("id", target_id).execute()
                st.rerun()

   elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Medewerkersbeheer")
        
        # Medewerker toevoegen
        with st.expander("Nieuwe medewerker toevoegen"):
            with st.form("add_user"):
                new_user = st.text_input("Gebruikersnaam")
                new_role = st.selectbox("Rol", ["admin", "editor", "viewer"])
                if st.form_submit_button("Toevoegen"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": new_user, "rol": new_role}).execute()
                    st.success("Medewerker toegevoegd!")
                    st.rerun()

        # Medewerkers overzicht en beheer
        st.subheader("Huidige Medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        
        for m in medewerkers:
            cols = st.columns([2, 1, 1])
            cols[0].write(f"**{m['gebruikersnaam']}** ({m['rol']})")
            
            # Rol wijzigen
            if cols[1].button("Wijzig rol", key=f"edit_{m['id']}"):
                # Hier zou je een popup kunnen openen of de rol direct updaten
                pass 
            
            # Verwijderen
            if cols[2].button("🗑️", key=f"del_{m['id']}"):
                supabase.table("medewerkers").delete().eq("id", m['id']).execute()
                st.rerun()
# --- FORMULIER (Voor iedereen zichtbaar) ---
st.divider()
st.title("Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("Volledige naam")
        id_nr = st.text_input("ID Nummer")
        woonadres = st.text_input("Woonadres")
    with col2:
        email = st.text_input("E-mailadres")
        soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
    
    omschrijving = st.text_area("Omschrijving of oplossing")
    
    # --- NIEUW: File uploader ---
    uploaded_file = st.file_uploader("Upload foto of document (max 5MB)", type=['png', 'jpg', 'pdf'])
    
    if st.form_submit_button("Verstuur klacht"):
        file_path = None
        # --- LOGICA VOOR OPSLAG ---
        if uploaded_file is not None:
            # Sla het bestand op in Supabase Storage
            file_name = f"{id_nr}_{uploaded_file.name}"
            supabase.storage.from_("klachten-bijlagen").upload(file_name, uploaded_file.getvalue())
            file_path = file_name # Sla de naam op in de tabel zodat je de foto later kunt ophalen

        data_to_insert = {
            "volledige_naam": naam, 
            "id_nummer": id_nr, 
            "adres": woonadres, 
            "email": email, 
            "klachtensoort": soort, 
            "omschrijving": omschrijving, 
            "bijlage_pad": file_path, # Zorg dat deze kolom bestaat in je tabel
            "status": "Nieuw"
        }
        supabase.table("klachten").insert(data_to_insert).execute()
        st.success("Uw klacht inclusief bijlage is verzonden!")
