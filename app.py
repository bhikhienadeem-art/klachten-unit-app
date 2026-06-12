import streamlit as st

# 1. Pagina configuratie
st.set_page_config(page_title="Klachten Unit", layout="wide")

# 2. Custom CSS - De 'fix' zit in de styling van de inputs en knoppen
def set_custom_style():
    st.markdown("""
        <style>
        /* Blauwe Header en Zijbalk */
        .header-banner { background-color: #1e40af; color: white; padding: 20px; border-radius: 10px; margin-bottom: 25px; text-align: center; }
        [data-testid="stSidebar"] { background-color: #1e40af !important; }
        [data-testid="stSidebar"] * { color: #ffffff !important; }
        
        /* Zorg dat input velden wit zijn en tekst leesbaar is */
        div[data-baseweb="base-input"] { background-color: #ffffff !important; }
        input { color: #1e293b !important; }
        
        /* De Inlogknop (Zoals in je voorbeeld) */
        div.stFormSubmitButton > button {
            background-color: #60a5fa !important; /* Lichtblauw */
            color: white !important;
            font-weight: bold !important;
            width: 100% !important;
            border-radius: 8px !important;
            border: none !important;
            height: 50px !important;
        }
        
        .stat-value { font-size: 28px; font-weight: bold; color: #2563eb; }
        h3 { color: #1e293b; margin-top: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

# 3. Sessie beheer
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 4. Sidebar - Inloggen
with st.sidebar:
    if not st.session_state.logged_in:
        st.markdown("### 🔐 Medewerker Login")
        with st.form("login_form"):
            user = st.text_input("Gebruikersnaam")
            pw = st.text_input("Wachtwoord", type="password")
            
            # De submit button activeert automatisch bij 'Enter'
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
# ... (rest van je code blijft hetzelfde)
