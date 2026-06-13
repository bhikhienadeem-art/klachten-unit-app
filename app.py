import streamlit as st
import hashlib
import uuid
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "PLAK_HIER_JE_NIEUWE_ANON_SLEUTEL" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- CSS & HEADER ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    [data-testid="stSidebar"] { background-color: #004a99; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    .klacht-box { background-color: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #004a99; box-shadow: 2px 2px 5px #ddd; }
    .header-bar { background-color: #004a99; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
    h1 { color: #004a99; }
    </style>
""", unsafe_allow_html=True)

# Blauwe headerbalk met gegevens
st.markdown("""
    <div class="header-bar">
        <h2 style="color: white; margin: 0;">Klachten Unit Wanica Centrum</h2>
        <p style="margin: 5px; font-size: 14px;">
            📍 Adres: Tawajariweg #20, Lelydorp | 📞 Tel: +597 366660/+597 366929 | 💬 WhatsApp: +597 8921062 | 📧 E-mail: klachtenunitwanicacentrum@gmail.com
        </p>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN ---
def check_login(username, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        response = supabase.table("gebruikers").select("*").eq("username", username).execute()
        if response.data and response.data[0]['password_hash'] == pw_hash:
            return response.data[0]
    except: return None
    return None

if "logged_in" not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.markdown("### 🔐 Medewerker Panel")
    if not st.session_state.logged_in:
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            data = check_login(user, pw)
            if data:
                st.session_state.logged_in = True
                st.session_state.user_data = data
                st.rerun()
            else: st.error("Onjuiste gegevens")
    else:
        st.write(f"Ingelogd: {st.session_state.user_data.get('username')}")
        if st.button("Uitloggen"): st.session_state.logged_in = False; st.rerun()

# --- DASHBOARD LOGICA ---
if st.session_state.logged_in:
    st.title("DASHBOARD OVERZICHT")
    
    # Statistieken
    klachten = supabase.table("klachten").select("*").execute().data
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Totaal Nieuw", len([k for k in klachten if k.get('status') == 'Nieuw']))
    c2.metric("In Behandeling", "15")
    c3.metric("Afgehandeld", len([k for k in klachten if k.get('status') == 'Afgehandeld']))
    c4.metric("Gem. Reactietijd", "2.5 d")

    st.markdown("---")
    
    for k in klachten:
        with st.container():
            st.markdown(f'<div class="klacht-box">', unsafe_allow_html=True)
            st.subheader(f"Klacht #{k.get('id')} - {k.get('volledige_naam')}")
            col1, col2 = st.columns(2)
            col1.write(f"📧 **E-mail:** {k.get('email')}")
            col1.write(f"📞 **Telefoon:** {k.get('telefoon')}")
            col2.write(f"🏷️ **Onderwerp:** {k.get('onderwerp')}")
            col2.write(f"Status: **{k.get('status')}**")
            st.write(f"📝 **Omschrijving:** {k.get('omschrijving')}")
            if k.get('bestands_url'): st.markdown(f"[🔗 Bekijk bijlage]({k['bestands_url']})")
            
            if k.get('status') != 'Afgehandeld':
                if st.button("Markeer als afgehandeld", key=f"done_{k['id']}"):
                    supabase.table("klachten").update({"status": "Afgehandeld"}).eq("id", k['id']).execute()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- KLANT FORMULIER ---
    st.title("Klacht indienen")
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Volledige naam")
            email = st.text_input("E-mailadres")
        with col2:
            telefoon = st.text_input("Telefoon/Whatsapp Nummer")
            onderwerp = st.selectbox("Onderwerp", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving/Eventueel oplossing")
        bestand = st.file_uploader("Voeg foto of document toe", type=['png', 'jpg', 'pdf'])
        
        if st.form_submit_button("Verstuur klacht"):
            url = None
            if bestand:
                bestandsnaam = f"{uuid.uuid4()}_{bestand.name}"
                supabase.storage.from_("klacht-bestanden").upload(bestandsnaam, bestand.getvalue())
                url = f"{SUPABASE_URL}/storage/v1/object/public/klacht-bestanden/{bestandsnaam}"
            
            supabase.table("klachten").insert({
                "volledige_naam": naam, "email": email, "telefoon": telefoon, 
                "onderwerp": onderwerp, "omschrijving": omschrijving, "status": "Nieuw", "bestands_url": url
            }).execute()
            st.success("Uw klacht is succesvol verzonden!")
