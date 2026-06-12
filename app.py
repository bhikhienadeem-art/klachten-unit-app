import streamlit as st

# Pagina configuratie
st.set_page_config(page_title="Klachten Unit", layout="wide")

# 1. Custom CSS voor de professionele look
def set_custom_style():
    st.markdown("""
        <style>
        /* Modern Cards */
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff;
        }
        /* Dashboard tekst */
        .stat-value { font-size: 28px; font-weight: bold; color: #2563eb; }
        h3 { color: #1e293b; margin-top: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

# 2. Sessie beheer
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Sidebar (Inloggen of Navigatie)
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

# 4. Main Page Logic
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
        # Formulier voor medewerkers (zelfde als burger)
        st.title("Klacht Indienen")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # Formulier code...
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Publieke pagina voor burgers
    st.title("Welkom bij de Klachten Unit")
    st.write("Dien hieronder uw klacht in. Medewerkers kunnen inloggen via de zijbalk.")
    
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
            st.success("Uw klacht is verzonden!")
    st.markdown('</div>', unsafe_allow_html=True)
