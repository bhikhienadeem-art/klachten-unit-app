import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
import uuid 

# 1. MOET ALTIJD ALS EERSTE
st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_text = st.columns([1, 4]) 
with col_logo:
    st.image("orgineel logo Centrum.png", width=150)
with col_text:
    st.markdown('<div class="header-bar"><h1>Klachtenunit Commissariaat Wanica Centrum</h1></div>', unsafe_allow_html=True)

# --- SIDEBAR ---
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
        if not df_dash.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal", len(df_dash))
            c2.metric("Nieuw", len(df_dash[df_dash['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df_dash[df_dash['status'] == 'Afgehandeld']))
            st.markdown("---")
        
        for k in klachten:
            status = k.get('status', 'Nieuw')
            soort = k.get('klachtensoort', 'Anders')
            if soort == "Wateroverlast": prio = "🔴 HOOG"
            elif soort == "Wegen": prio = "🟠 MEDIUM"
            else: prio = "🟢 LAAG"
                
            with st.expander(f"{prio} | 👤 {k.get('volledige_naam', 'Anoniem')} | {soort} | Status: {status}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🆔 Ticket:** {k.get('ticket_id', '-')}")
                col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                
                nieuwe_status = st.selectbox("Status", ["Nieuw", "In behandeling", "Afgehandeld"], 
                                           index=["Nieuw", "In behandeling", "Afgehandeld"].index(status), 
                                           key=f"st_{k['id']}")
                if st.button("💾 Opslaan", key=f"btn_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status}).eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        if not df_dash.empty:
            st.download_button("📥 Download CSV", data=df_dash.to_csv(index=False), file_name='klachten.csv')
            st.plotly_chart(px.pie(df_dash, names='klachtensoort'))
            st.dataframe(df_dash)
        else:
            st.info("Geen data om weer te geven.")

    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Gebruikersbeheer")
        with st.expander("➕ Nieuwe medewerker toevoegen"):
            with st.form("add_user_form", clear_on_submit=True):
                u = st.text_input("Gebruikersnaam")
                p = st.text_input("Wachtwoord", type="password")
                r = st.selectbox("Rol", ["Admin", "Medewerker", "Viewer"])
                if st.form_submit_button("Opslaan"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p, "rol": r}).execute()
                    st.success("✅ Toegevoegd!")
                    st.rerun()
        
        st.subheader("👥 Huidige medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        if medewerkers:
            st.table(pd.DataFrame(medewerkers)[['gebruikersnaam', 'rol']])
            te_verwijderen = st.selectbox("Selecteer om te verwijderen", options=[m['gebruikersnaam'] for m in medewerkers])
            if st.button("🗑️ Verwijder medewerker"):
                supabase.table("medewerkers").delete().eq("gebruikersnaam", te_verwijderen).execute()
                st.rerun()
else:
    # --- BURGERS PAGINA ---
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
        
        if st.form_submit_button("Verstuur Klacht"):
            ticket_nr = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            data = {
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw", "ticket_id": ticket_nr
            }
            supabase.table("klachten").insert(data).execute()
            st.success(f"✅ Klacht verzonden! Uw ticketnummer: {ticket_nr}")

    st.markdown("---")
    st.subheader("🗓️ Afspraak maken")
    with st.form("afspraak_form", clear_on_submit=True):
        naam_af = st.text_input("Uw Naam")
        datum = st.date_input("Datum")
        if st.form_submit_button("Afspraak Bevestigen"):
            st.success("✅ Afspraak bevestigd!")
