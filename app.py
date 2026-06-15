import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    .stTextInput input { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_text = st.columns([1, 4]) 
with col_logo:
    st.image("orgineel logo Centrum.png", width=150)
with col_text:
    st.markdown("""
        <div class="header-bar">
            <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
            <div style="font-size: 0.9em; margin-top: 15px;">
                📍 Tawajarieweg 20 | 📞 (+597) 366660/366929 | 💬 WhatsApp: (+597) 8921062 | ✉️ klachtenunitwanicacentrum@gmail.com
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR & NAVIGATIE ---
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
    klachten = supabase.table("klachten").select("*").execute().data
    df_dash = pd.DataFrame(klachten)

    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        # Metric Cards (Stap 5)
        c1, c2, c3 = st.columns(3)
        c1.metric("Totaal Klachten", len(df_dash))
        c2.metric("Nieuw", len(df_dash[df_dash['status'] == 'Nieuw']))
        c3.metric("Afgehandeld", len(df_dash[df_dash['status'] == 'Afgehandeld']))
        
        for k in klachten:
            with st.expander(f"👤 Klacht: {k.get('volledige_naam', 'Anoniem')} | Status: {k.get('status', 'Nieuw')}"):
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                # Status update logica
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                nieuwe_status = st.selectbox("Status", status_opties, index=status_opties.index(k.get('status', 'Nieuw')), key=f"s_{k['id']}")
                if st.button("Opslaan", key=f"b_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        if not df_dash.empty:
            st.download_button("📥 Download CSV", data=df_dash.to_csv(index=False), file_name='klachten.csv')
            st.plotly_chart(px.pie(df_dash, names='klachtensoort'))
            st.dataframe(df_dash)

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")
        st.write("Gebruikersbeheer functionaliteit...")

else:
    # --- PUBLIEK FORMULIER ---
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form"):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Volledige naam")
        soort = col2.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        if st.form_submit_button("Verstuur"):
            supabase.table("klachten").insert({"volledige_naam": naam, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw"}).execute()
            st.success("Verzonden!")
