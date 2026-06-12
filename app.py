import streamlit as st

# Pagina configuratie
st.set_page_config(page_title="Klachten Dashboard", layout="wide")

# 1. CSS Stijlen
def set_custom_style():
    st.markdown("""
        <style>
        .card { background-color: #ffffff; border-radius: 12px; padding: 20px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 20px; }
        [data-testid="stSidebar"] { background-color: #0f172a; }
        [data-testid="stSidebar"] * { color: #ffffff; }
        .stat-value { font-size: 28px; font-weight: bold; color: #2563eb; }
        h3 { color: #1e293b; margin-top: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

# 2. Inlog beheer in session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Inlogpagina
def login_page():
    st.title("🔐 Medewerkers Login")
    with st.form("login"):
        user = st.text_input("Gebruikersnaam")
        pw = st.text_input("Wachtwoord", type="password")
        if st.form_submit_button("Inloggen"):
            if user == "admin" and pw == "geheim": # Pas dit aan naar je wens
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Ongeldige gegevens")

# 4. Dashboard (Alleen zichtbaar indien ingelogd)
def show_dashboard():
    with st.sidebar:
        st.title("Klachten Systeem")
        if st.button("Log uit"):
            st.session_state.logged_in = False
            st.rerun()
        menu = st.radio("Navigatie", ["Dashboard", "Klacht Indienen"])

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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("klacht"):
            st.text_input("Volledige Naam")
            st.text_area("Omschrijving")
            if st.form_submit_button("Indienen"):
                st.success("Verzonden!")
        st.markdown('</div>', unsafe_allow_html=True)

# Main app flow
if not st.session_state.logged_in:
    login_page()
else:
    show_dashboard()
