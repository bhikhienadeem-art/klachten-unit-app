import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Stel de pagina-configuratie in
st.set_page_config(
    page_title="Klachten Unit Wanica",
    page_icon="https://wanica.gov.sr/images/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS STYLING (Bijgewerkt voor VEEL meer kleur!) ---
# Ik heb een verloopachtergrond toegevoegd (gradient) die overgaat van een diep blauw
# naar een levendig geel, geïnspireerd door de Surinaamse vlag en het Wanica-logo.
# Ook de knoppen en actie-elementen hebben we geel en blauw gemaakt.
st.markdown("""
    <style>
    /* Hoofdpagina achtergrondverloop: Blauw naar Geel */
    .stApp {
        background: linear-gradient(135deg, #003a7a 0%, #004a99 30%, #ffdf00 80%, #ffcc00 100%);
        background-attachment: fixed;
    }
    
    /* Header balk styling */
    .header-bar {
        background-color: #004a99; /* Deep Wanica Blue */
        color: white;
        padding: 30px;
        text-align: center;
        border: 7px solid #ffcc00; /* Gold Yellow border */
        border-radius: 15px;
        margin-bottom: 40px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    .header-bar h1 { margin: 0; color: white !important; font-size: 2.5em; }
    .header-text { margin-top: 15px; font-size: 1.2em; font-style: italic; color: #ffdf00; }
    .contact-info { font-size: 1.0em; margin-top: 20px; padding-top: 15px; border-top: 2px solid #ffdf00; color: white; }

    /* Inlog Sidebar styling: Blauw */
    [data-testid="stSidebar"] {
        background-color: #003a7a;
        color: white;
    }
    [data-testid="stSidebar"] [data-testid="stHeader"] { color: #ffcc00 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #ffcc00 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }

    /* Expander styling: Wit met Blauw-Gele details */
    div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        border: 2px solid #004a99;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    div[data-testid="stExpander"] label { color: #004a99 !important; font-weight: bold; }

    /* Knoppen styling: Geel met Blauw */
    div.stButton > button {
        background-color: #ffcc00; /* Wanica Gold */
        color: #003a7a !important; /* Deep Blue text */
        border-radius: 8px;
        border: 2px solid #003a7a;
        font-weight: bold;
        transition: transform 0.2s, background-color 0.2s;
    }
    div.stButton > button:hover {
        background-color: #ffdf00;
        transform: scale(1.05);
    }

    /* Formulier styling: Wit met Geel-Blauw accent */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        border: 3px solid #ffcc00;
        padding: 30px;
        box-shadow: 6px 6px 15px rgba(0,0,0,0.15);
    }
    [data-testid="stForm"] h3 { color: #004a99 !important; font-weight: bold; }
    
    /* Text input accenten */
    div.stTextInput label, div.stSelectbox label, div.stTextArea label { color: #004a99 !important; font-weight: bold; }
    
    /* Divider accent */
    hr { border: 0; height: 3px; background: linear-gradient(to right, #004a99, #ffcc00, #004a99); margin: 40px 0; }

    /* Iconen in actieknoppen goud maken */
    .del-btn-icon, .save-btn-icon { color: #ffcc00; font-size: 1.2em; }
    
    /* E-mail link styling: Blauw met Gele knop effect */
    a.mailto-link {
        text-decoration: none;
        color: #003a7a !important;
        background-color: #ffdf00;
        padding: 12px 18px;
        border-radius: 8px;
        border: 2px solid #003a7a;
        font-weight: bold;
        display: inline-block;
        transition: transform 0.2s;
    }
    a.mailto-link:hover { transform: scale(1.05); }
    </style>
""", unsafe_allow_html=True)

# --- HEADER (Blijft zoals het was, maar met betere CSS-styling) ---
st.markdown("""
    <div class="header-bar">
        <h1>🏢 Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="header-text">
            Samen bouwen we aan een beter Wanica.<br>
            Uw stem telt. Via deze pagina kunt u uw klacht of suggestie veilig en direct indienen.
        </div>
        <div class="contact-info">
            📍 <b>Bezoekadres:</b> Tawajarieweg 20, Domburg | 📞 <b>Tel:</b> (+597) 366660<br>
            ✉️ <b>E-mail:</b> klachtenunitwanicacentrum@gmail.com
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.image("https://jouw-supabase-url.supabase.co/storage/v1/object/public/images/WanicaLogo.png", width=120) # Placeholder voor jouw logo
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("👤 Gebruikersnaam")
        wachtwoord = st.text_input("🔒 Wachtwoord", type="password")
        col_login = st.columns([1,1])
        with col_login[0]:
            if st.button("🔓 Inloggen", use_container_width=True):
                if gebruiker == "admin" and wachtwoord == "admin123":
                    st.session_state.logged_in = True
                    st.success("✅ Ingelogd als Admin")
                    st.rerun()
                else:
                    st.error("❌ Ongeldige gegevens.")
    else:
        st.success("✅ Ingelogd als Admin")
        st.session_state.menu = st.radio("🏠 Navigatie", ["📊 Dashboard", "📈 Rapporten", "⚙️ Instellingen"])
        if st.button("🔒 Uitloggen", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if st.session_state.menu == "📊 Dashboard":
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
                notitie = st.text_area("✍️ Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                
                col_actions = st.columns([1, 1, 3])
                with col_actions[0]:
                    if st.button("💾 Opslaan", key=f"save_{k['id']}", use_container_width=True):
                        supabase.table("klachten").update({"status": nieuwe_status, "interne_notitie": notitie}).eq("id", k['id']).execute()
                        st.rerun()
                with col_actions[1]:
                    if k.get('email'):
                        # Kleurrijke mailto-knop
                        st.markdown(f'<a href="mailto:{k["email"]}?subject=Update over uw klacht bij Wanica Centrum&body=Geachte {k.get("volledige_naam")}" class="mailto-link">📧 E-mail</a>', unsafe_allow_html=True)

    elif st.session_state.menu == "📈 Rapporten":
        st.title("📈 Rapporten & Beheer")
        data = supabase.table("klachten").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            # Kleurrijke Plotly grafiek
            fig = px.pie(df, names='klachtensoort', title="🗺️ Verdeling per Klachtensoort", color_discrete_sequence=px.colors.sequential.Bluered_r)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("🗑️ Klacht verwijderen")
            target_id = st.selectbox("Selecteer ID om te verwijderen", df['id'].tolist())
            if st.button("🗑️ Verwijder klacht", use_container_width=True):
                supabase.table("klachten").delete().eq("id", target_id).execute()
                st.rerun()

    elif st.session_state.menu == "⚙️ Instellingen":
        st.title("⚙️ Instellingen - Medewerkers")
        with st.expander("➕ Nieuwe medewerker"):
            with st.form("add_user"):
                st.subheader("➕ Toevoegen")
                new_user = st.text_input("👤 Gebruikersnaam")
                new_pass = st.text_input("🔒 Wachtwoord", type="password")
                new_role = st.selectbox("📋 Rol", ["admin", "editor", "viewer"])
                if st.form_submit_button("Toevoegen"):
                    supabase.table("medewerkers").insert({"gebruikersnaam": new_user, "wachtwoord": new_pass, "rol": new_role}).execute()
                    st.rerun()
        
        st.subheader("👥 Huidige Medewerkers")
        medewerkers = supabase.table("medewerkers").select("*").execute().data
        for m in medewerkers:
            cols = st.columns([2, 2, 1])
            cols[0].write(f"**👤 {m['gebruikersnaam']}**")
            cols[1].write(f"Rol: {m['rol']}")
            if cols[2].button("🗑️", key=f"del_{m['id']}", use_container_width=True):
                supabase.table("medewerkers").delete().eq("id", m['id']).execute()
                st.rerun()

# --- FORMULIER ---
st.divider()
st.subheader("📋 Klacht indienen")
st.info("💡 Tip: Vul alle velden zo compleet mogelijk in voor een snelle afhandeling.")
with st.form("klacht_form", clear_on_submit=True):
    st.subheader("✍️ Uw gegevens")
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("👤 Volledige naam")
        id_nr = st.text_input("🆔 ID Nummer")
        telefoon = st.text_input("📞 Telefoon/WhatsApp nummer")
        woonadres = st.text_input("🏠 Woonadres")
    with col2:
        email = st.text_input("📧 E-mailadres")
        soort = st.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'pdf'])
        
    omschrijving = st.text_area("📝 Omschrijving of suggestie voor oplossing")
    if st.form_submit_button("Verstuur klacht"):
        file_name = uploaded_file.name if uploaded_file else None
        # Let op: de echte bestandsupload naar Supabase Storage moet nog toegevoegd worden
        supabase.table("klachten").insert({
            "volledige_naam": naam, "id_nummer": id_nr, "telefoon": telefoon, "adres": woonadres, 
            "email": email, "klachtensoort": soort, "omschrijving": omschrijving, 
            "status": "Nieuw", "bijlage_url": file_name
        }).execute()
        st.success("✅ Uw klacht is succesvol verzonden! Wij nemen zo snel mogelijk contact op.")
