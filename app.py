import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <p>📍 Tawajarieweg 20 | 📞 (+597) 366660 | ✉️ klachtenunitwanicacentrum@gmail.com</p>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
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
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"👤 {k.get('volledige_naam')} | Status: {k.get('status', 'Nieuw')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                if st.button("🗑️ Klacht verwijderen", key=f"del_{k['id']}"):
                    supabase.table("klachten").delete().eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        data = supabase.table("klachten").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            st.plotly_chart(px.pie(df, names='klachtensoort'))
            st.dataframe(df)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Beheer")
        # Toevoegen
        with st.expander("➕ Medewerker toevoegen"):
            with st.form("add_user"):
                u = st.text_input("Gebruikersnaam")
                p = st.text_input("Wachtwoord", type="password")
                if st.form_submit_button("Toevoegen"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p}).execute()
                    st.rerun()
        # Verwijderen
        st.subheader("👥 Medewerkers beheren")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        for m in medewerkers:
            col1, col2 = st.columns([3, 1])
            col1.write(f"Gebruiker: {m['gebruikersnaam']}")
            if col2.button("❌", key=f"del_user_{m['id']}"):
                supabase.table("medewerkers").delete().eq("id", m['id']).execute()
                st.rerun()

# --- FORMULIER (Voor niet-ingelogde gebruikers) ---
else:
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        naam = st.text_input("Volledige naam")
        omschrijving = st.text_area("Omschrijving")
        if st.form_submit_button("Verstuur"):
            supabase.table("klachten").insert({"volledige_naam": naam, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
            st.success("Verzonden!")
