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
    .stApp { background-color: #e3f2fd; }
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    
    /* Zorg dat tekst in inputvelden zichtbaar blijft in de sidebar */
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    .stTextInput input { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div style="font-size: 0.9em; margin-top: 15px;">
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
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard - Klachtenbeheer")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"👤 Klacht: {k.get('volledige_naam', 'Anoniem')} | Status: {k.get('status', 'Nieuw')}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🆔 ID:** {k.get('id_nummer', '-')}")
                col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}")
                col_a.write(f"**📞 Tel/WA:** {k.get('telefoon', '-')}")
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


    # 2. RAPPORTEN
    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        data = supabase.table("klachten").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(df, names='klachtensoort', title="Verdeling klachtensoort")
            st.plotly_chart(fig)
            st.dataframe(df)

    # 3. INSTELLINGEN
    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen - Beheer")
        with st.expander("➕ Medewerker toevoegen"):
            with st.form("add_user"):
                u = st.text_input("Gebruikersnaam")
                p = st.text_input("Wachtwoord", type="password")
                if st.form_submit_button("Toevoegen"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": u, "wachtwoord": p}).execute()
                    st.success("Toegevoegd!")


# --- FORMULIER (Alleen als niet ingelogd) ---
else:
    st.subheader("📝 Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("👤 Volledige naam")
        id_nr = col1.text_input("🆔 ID Nummer")
        telefoon = col1.text_input("📞 Telefoon/WhatsApp nummer")
        woonadres = col1.text_input("🏠 Woonadres")
        email = col2.text_input("📧 E-mailadres")
        soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        uploaded_file = col2.file_uploader("📎 Foto/Document", type=['png', 'jpg', 'pdf'])
        omschrijving = st.text_area("📝 Omschrijving")
        
        wil_afspraak = st.checkbox("Ik wil een afspraak maken")
        afspraak_datum = st.date_input("Kies datum") if wil_afspraak else None
        
        if st.form_submit_button("Verstuur"):
            supabase.table("klachten").insert({
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon": telefoon,
                "adres": woonadres, "email": email, "klachtensoort": soort,
                "omschrijving": omschrijving, "status": "Nieuw",
                "afspraak_datum": str(afspraak_datum) if wil_afspraak else None
            }).execute()
            st.success("✅ Verzonden!")
