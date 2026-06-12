import streamlit as st

# 1. Pagina configuratie
st.set_page_config(page_title="Klachten Unit", layout="wide")

# 2. Custom CSS
def set_custom_style():
    st.markdown("""
        <style>
        /* Blauwe Header Banner met contactgegevens */
        .header-banner { 
            background-color: #1e40af; 
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 25px; 
            text-align: center; 
        }
        .contact-grid {
            display: flex; 
            justify-content: space-around; 
            padding-top: 15px; 
            font-size: 0.9em;
            flex-wrap: wrap;
        }
        /* Blauwe Zijbalk */
        [data-testid="stSidebar"] { 
            background-color: #1e40af !important; 
        }
        [data-testid="stSidebar"] * { 
            color: #ffffff !important; 
        }
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
            st.container(border=True).markdown("### Nieuwe Klachten<br><div class='stat-value'>12</div>", unsafe_allow_html=True)
        with col2:
            st.container(border=True).markdown("### In Behandeling<br><div class='stat-value'>5</div>", unsafe_allow_html=True)
        with col3:
            st.container(border=True).markdown("### Afgehandeld<br><div class='stat-value'>7</div>", unsafe_allow_html=True)
    else:
        st.title("Klacht Indienen")
        st.write("Formulier voor medewerkers.")
else:
    # Publieke pagina - Blauwe header met contact info
    st.markdown('''
        <div class="header-banner">
            <h1>Welkom bij de Klachten Unit</h1>
            <p>Dien hieronder uw klacht in. Medewerkers kunnen inloggen via de zijbalk.</p>
            <div class="contact-grid">
                <div>📍 <b>Adres:</b><br>Tawajarieweg no. 20</div>
                <div>📞 <b>Telefoon:</b><br>+597-366660 / +597-366929</div>
                <div>💬 <b>WhatsApp:</b><br>+597-8921062</div>
                <div>✉️ <b>E-mail:</b><br>klachtenunitwanicacentrum@gmail.com</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.header("Klacht Indienen")
    with st.container(border=True):
        with st.form("burger_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Volledige Naam")
                st.text_input("ID-Nummer")
            with c2:
                st.text_input("Telefoonnummer")
                st.text_input("E-mailadres")
            
            st.selectbox("Soort klacht", ["Infrastructuur", "Dienstverlening", "Overig"])
            st.text_area("Omschrijving")
            st.file_uploader("Documenten of Foto's uploaden", accept_multiple_files=True)
            
            if st.form_submit_button("Verstuur Klacht"):
                st.success("Uw klacht is succesvol verzonden!")
