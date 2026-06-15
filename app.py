import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE (Moet bovenaan staan om errors te voorkomen) ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 20px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    .stTextInput input { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER MET LOGO ---
col_l, col_r = st.columns([1, 4])
with col_l:
    # Zorg dat "orgineel logo Centrum.png" in je map staat
    st.image("orgineel logo Centrum.png", width=180)
with col_r:
    st.markdown("""
        <div class="header-bar">
            <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
            <div style="font-size: 0.9em; margin-top: 10px;">
                📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam", key="user_in")
        wachtwoord = st.text_input("Wachtwoord", type="password", key="pass_in")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    
    st.title("📊 Dashboard - Klachtenbeheer")
if st.session_state.menu == "Dashboard":
    # Haal data op
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten)
    
    # Bereken metrics
    totaal = len(df_dash)
    nieuw = len(df_dash[df_dash['status'] == 'Nieuw'])
    afgehandeld = len(df_dash[df_dash['status'] == 'Afgehandeld'])
    
    # Toon in 3 kolommen
    col1, col2, col3 = st.columns(3)
    col1.metric("Totaal Klachten", totaal)
    col2.metric("Nieuwe Klachten", nieuw, delta_color="inverse")
    col3.metric("Afgehandeld", afgehandeld)

elif st.session_state.menu == "Rapporten":
    st.title("📈 Rapporten & Analyse")
    data = supabase.table("klachten").select("*").execute().data
    if data:
        df = pd.DataFrame(data)
        
        # Download knop
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download rapport als CSV",
            data=csv,
            file_name='klachten_rapport.csv',
            mime='text/csv',
        )
        st.plotly_chart(px.pie(df, names='klachtensoort'))

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Gebruikersbeheer")
        with st.expander("➕ Nieuwe medewerker toevoegen"):
            with st.form("add_user_form"):
                u = st.text_input("Gebruikersnaam")
                p = st.text_input("Wachtwoord", type="password")
                r = st.selectbox("Rol", ["Admin", "Medewerker", "Viewer"])
                if st.form_submit_button("Opslaan"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p, "rol": r}).execute()
                    st.success(f"Medewerker {u} toegevoegd!")
                    st.rerun()
        
        st.subheader("👥 Huidige medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        if medewerkers:
            df_users = pd.DataFrame(medewerkers)
            st.table(df_users[['gebruikersnaam', 'rol']])
            te_verwijderen = st.selectbox("Selecteer gebruiker om te verwijderen", options=[m['gebruikersnaam'] for m in medewerkers])
            if st.button("Verwijder deze medewerker"):
                supabase.table("medewerkers").delete().eq("gebruikersnaam", te_verwijderen).execute()
                st.rerun()

else:
    # --- FORMULIER ---
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("👤 Volledige naam")
        id_nr = col1.text_input("🆔 ID Nummer")
        telefoon = col1.text_input("📞 Telefoon/WhatsApp nummer")
        woonadres = col1.text_input("🏠 Woonadres")
        email = col2.text_input("📧 E-mailadres")
        soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("📝 Omschrijving")
        
        # NIEUW: File uploader toevoegen
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if st.form_submit_button("Verstuur"):
            file_url = None
            
            # Bestand uploaden naar Storage als er een bestand is gekozen
            if uploaded_file is not None:
                file_path = f"bijlagen/{uploaded_file.name}"
                try:
                    # Upload naar Supabase Storage
                    supabase.storage.from_("bijlagen").upload(file_path, uploaded_file.getvalue())
                    # Haal de publieke URL op
                    file_url = supabase.storage.from_("bijlagen").get_public_url(file_path)
                except Exception as e:
                    st.error(f"Fout bij uploaden bestand: {e}")

            try:
                # Opslaan in de 'klachten' tabel
                data = {
                    "volledige_naam": naam,
                    "id_nummer": id_nr,
                    "telefoon_whatsapp": telefoon,
                    "adres": woonadres,
                    "email": email,
                    "klachtensoort": soort,
                    "omschrijving": omschrijving,
                    "status": "Nieuw",
                    "bijlage_url": file_url # Sla de link op in je database
                }
                supabase.table("klachten").insert(data).execute()
                st.success("✅ Klacht inclusief bijlage verzonden!")
            except Exception as e:
                st.error(f"Fout bij verzenden naar database: {e}")
