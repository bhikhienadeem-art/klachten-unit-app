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
        
        # Data ophalen
        klachten = supabase.table("klachten").select("*").execute().data
        df_dash = pd.DataFrame(klachten)
        
        # --- METRIC CARDS (Stap 5) ---
        if not df_dash.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Totaal Klachten", len(df_dash))
            c2.metric("Nieuw", len(df_dash[df_dash['status'] == 'Nieuw']))
            c3.metric("Afgehandeld", len(df_dash[df_dash['status'] == 'Afgehandeld']))
            st.markdown("---")
        
        # --- KLACHTEN LIJST ---
        for k in klachten:
            # Expander met status kleur indicatie
            status = k.get('status', 'Nieuw')
            with st.expander(f"👤 {k.get('volledige_naam', 'Anoniem')} | 📋 {k.get('klachtensoort', '-')} | Status: {status}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**🆔 ID:** {k.get('id_nummer', '-')}")
                col_a.write(f"**🏠 Adres:** {k.get('adres', '-')}")
                col_a.write(f"**📞 Tel/WA:** {k.get('telefoon_whatsapp', '-')}")
                
                col_b.write(f"**📧 E-mail:** {k.get('email', '-')}")
                # Toon link naar bijlage indien aanwezig
                if k.get('bijlage_url'):
                    col_b.markdown(f"**📎 Bijlage:** [Bekijk bestand]({k['bijlage_url']})")
                
                st.write(f"**📝 Omschrijving:** {k.get('omschrijving', '-')}")
                
                # Status update & Interne notitie
                st.markdown("---")
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                huidige_idx = status_opties.index(status) if status in status_opties else 0
                
                nieuwe_status = st.selectbox("Status bijwerken", status_opties, index=huidige_idx, key=f"status_{k['id']}")
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                
                if st.button("💾 Status & Notitie Opslaan", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({
                        "status": nieuwe_status, 
                        "interne_notitie": notitie
                    }).eq("id", k['id']).execute()
                    st.success("Opgeslagen!")
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
