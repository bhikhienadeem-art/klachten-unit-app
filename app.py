import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime, time

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
                col_a.write(f"**📞 Tel/WA:** {k.get('telefoon_whatsapp', '-')}")
                col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                col_b.write(f"**📋 Soort:** {k.get('klachtensoort', '-')}")
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                huidige_status = k.get('status', 'Nieuw')
                nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=status_opties.index(huidige_status) if huidige_status in status_opties else 0, key=f"status_{k['id']}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                if st.button("💾 Opslaan", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Analyse")
        data = supabase.table("klachten").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(df, names='klachtensoort', title="Verdeling klachtensoort")
            st.plotly_chart(fig)
            st.dataframe(df)

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
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        # --- NIEUW: AFSPRAAK CALENDAR ---
        st.write("---")
        st.subheader("🤝 Afspraak maken (Optioneel)")
        wil_afspraak = st.checkbox("Ik wil een afspraak maken (Ma-Vr, 08:00 - 14:00)")
        
        afspraak_datum = None
        afspraak_tijd = None
        
        if wil_afspraak:
            col_a, col_b = st.columns(2)
            afspraak_datum = col_a.date_input("Kies datum")
            afspraak_tijd = col_b.time_input("Kies tijd", value=time(8, 0))
            
            # Valideer dag (ma-vr) en tijd (08-14)
            if afspraak_datum.weekday() >= 5:
                st.error("Afspraken zijn alleen mogelijk op maandag t/m vrijdag.")
            elif afspraak_tijd.hour < 8 or afspraak_tijd.hour >= 14:
                st.error("Afspraken zijn alleen mogelijk tussen 08:00 en 14:00 uur.")
        
        if st.form_submit_button("Verstuur"):
            file_url = None
            if uploaded_file is not None:
                file_path = f"bijlagen/{uploaded_file.name}"
                try:
                    supabase.storage.from_("bijlagen").upload(file_path, uploaded_file.getvalue())
                    file_url = supabase.storage.from_("bijlagen").get_public_url(file_path)
                except Exception as e:
                    st.error(f"Fout bij uploaden bestand: {e}")

            try:
                data = {
                    "volledige_naam": naam,
                    "id_nummer": id_nr,
                    "telefoon_whatsapp": telefoon,
                    "adres": woonadres,
                    "email": email,
                    "klachtensoort": soort,
                    "omschrijving": omschrijving,
                    "status": "Nieuw",
                    "bijlage_url": file_url,
                    "afspraak_datum": str(afspraak_datum) if wil_afspraak else None,
                    "afspraak_tijd": str(afspraak_tijd) if wil_afspraak else None
                }
                supabase.table("klachten").insert(data).execute()
                st.success("✅ Klacht en eventuele afspraak verzonden!")
            except Exception as e:
                st.error(f"Fout bij verzenden: {e}")
