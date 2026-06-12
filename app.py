import streamlit as st

# 1. Pagina configuratie
st.set_page_config(page_title="Klachten Unit", layout="wide")

# 2. Custom CSS voor de professionele look
def set_custom_style():
    st.markdown("""
        <style>
        .header-banner { background-color: #1e40af; color: white; padding: 20px; border-radius: 10px; margin-bottom: 25px; text-align: center; }
        .card { background-color: #ffffff; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; margin-bottom: 20px; }
        [data-testid="stSidebar"] { background-color: #0f172a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        .stat-value { font-size: 28px; font-weight: bold; color: #2563eb; }
        h3 { color: #1e293b; margin-top: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

# 3. Sessie beheer
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 4. Sidebar
with st.sidebar:
    if not st.session_state.logged_in:
        st.title("🔐 Medewerker Login")
        with st.form("login_form"):
            user = st.text_input("Gebruikersnaam")
            pw = st.text_input("Wachtwoord", type="password")
            if st.form_submit_button("Inloggen"):
                if user == "admin" and pw == "geheim":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Onjuiste gegevens")
    else:
        st.title("Klachten Systeem")
        menu = st.radio("Navigatie", ["Dashboard", "Klacht Indienen"])
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.rerun()

# 5. Hoofdinhoud
if st.session_state.logged_in:
    if menu == "Dashboard":
        st.title("Admin Dashboard")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="card"><h3>Nieuwe Klachten</h3><div class="stat-value">12</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card"><h3>In Behandeling</h3><div class="stat-value">5</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="card"><h3>Afgehandeld</h3><div class="stat-value">7</div></div>', unsafe_allow_html=True)
    elif menu == "Klacht Indienen":
        st.title("Klacht Indienen")
        st.markdown('<div class="card">Formulier voor medewerkers volgt...</div>', unsafe_allow_html=True)
else:
    # Publieke pagina
    st.markdown('<div class="header-banner"><h1>Welkom bij de Klachten Unit</h1></div>', unsafe_allow_html=True)
    
  # 4 Kolommen voor contactgegevens
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.markdown("**📍 Adres:**<br>Tawajarieweg no. 20", unsafe_allow_html=True)
    with col_c2:
        st.markdown("**📞 Telefoon:**<br>+597-366660 / +597-366929", unsafe_allow_html=True)
    with col_c3:
        st.markdown("**💬 WhatsApp:**<br>+597-8921062", unsafe_allow_html=True)
    with col_c4:
        st.markdown("**✉️ E-mail:**<br>klachtenunitwanicacentrum@gmail.com", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Klacht Indienen")
    with st.form("burger_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Volledige Naam")
            st.text_input("ID-Nummer")
        with col2:
            st.text_input("Telefoonnummer")
            st.text_input("E-mailadres")
        
        st.selectbox("Soort klacht", ["Infrastructuur", "Dienstverlening", "Overig"])
        st.text_area("Omschrijving")
        st.file_uploader("Documenten of Foto's uploaden", accept_multiple_files=True)
        
        if st.form_submit_button("Verstuur Klacht"):
            st.success("Uw klacht is succesvol verzonden!")
    st.markdown('</div>', unsafe_allow_html=True)
