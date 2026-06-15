import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING (Stap 1: Professionele look) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    div.stButton > button { background-color: #004a99; color: white; border-radius: 5px; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-style: italic;">Welkom op de officiële klachtenpagina. Uw stem wordt gehoord.</div>
        <div style="font-size: 0.9em; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;">
            📍 Tawajarieweg 20 | 📞 (+597) 366660 | ✉️ klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("👤 Gebruikersnaam")
        wachtwoord = st.text_input("🔒 Wachtwoord", type="password")
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
        st.title("📊 Dashboard - Klachtenbeheer")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"👤 Klacht: {k.get('volledige_naam', 'Anoniem')} | Status: {k.get('status', 'Nieuw')}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🆔 ID:** {k.get('id_nummer', '-')}")
                col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}")
                col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                col_b.write(f"**📋 Soort:** {k.get('klachtensoort', '-')}")
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                if k.get('bijlage_url'): st.info(f"📎 Bijlage: {k['bijlage_url']}")
                
                st.divider()
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                huidige_status = k.get('status', 'Nieuw')
                idx = status_opties.index(huidige_status) if huidige_status in status_opties else 0
                nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=idx, key=f"status_{k['id']}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                if st.button("💾 Opslaan", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Beheer")
        data = supabase.table("klachten").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(df, names='klachtensoort', title="Verdeling per Klachtensoort")
            st.plotly_chart(fig)
            st.dataframe(df)
            target_id = st.selectbox("Selecteer ID om te verwijderen", df['id'].tolist())
            if st.button("🗑️ Verwijder klacht"):
                supabase.table("klachten").delete().eq("id", target_id).execute()
                st.rerun()

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        with st.expander("➕ Nieuwe medewerker"):
            with st.form("add_user"):
                new_user = st.text_input("Gebruikersnaam")
                new_pass = st.text_input("Wachtwoord", type="password")
                new_role = st.selectbox("Rol", ["admin", "editor", "viewer"])
                if st.form_submit_button("Toevoegen"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": new_user, "wachtwoord": new_pass, "rol": new_role}).execute()
                    st.rerun()

# --- FORMULIER ---
st.divider()
st.subheader("📝 Klacht indienen")
st.info("Vul onderstaand formulier in om uw klacht kenbaar te maken.")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("👤 Volledige naam")
        id_nr = st.text_input("🆔 ID Nummer")
        woonadres = st.text_input("🏠 Woonadres")
    with col2:
        email = st.text_input("📧 E-mailadres")
        soort = st.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'pdf'])
        
    omschrijving = st.text_area("📝 Omschrijving of voorstel voor oplossing")
    if st.form_submit_button("Verstuur klacht"):
        supabase.table("klachten").insert({
            "volledige_naam": naam, "id_nummer": id_nr, "adres": woonadres, 
            "email": email, "klachtensoort": soort, "omschrijving": omschrijving, 
            "status": "Nieuw", "bijlage_url": uploaded_file.name if uploaded_file else None
        }).execute()
        st.success("✅ Uw klacht is succesvol verzonden!")
