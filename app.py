import streamlit as st

st.set_page_config(page_title="Klachten Systeem", layout="wide")

# CSS voor de professionele look
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0f172a; }
    [data-testid="stSidebar"] * { color: #ffffff; }
    .card { background-color: #ffffff; border-radius: 12px; padding: 20px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# Session state voor inloggen
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Sidebar Logica
with st.sidebar:
    if not st.session_state.logged_in:
        st.title("🔐 Medewerkers Inlog")
        with st.form("login_sidebar"):
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

# Main Area
if st.session_state.logged_in:
    if menu == "Dashboard":
        st.title("Admin Dashboard")
        # Hier je dashboard cards...
    elif menu == "Klacht Indienen":
        st.title("Klacht Indienen")
        # Hier je formulier...
else:
    st.title("Welkom bij de Klachten Unit")
    st.write("Log in via het menu aan de linkerkant om toegang te krijgen tot het systeem.")
