import streamlit as st

# 1. Pagina configuratie
st.set_page_config(page_title="Klachten Dashboard", layout="wide")

# 2. Custom CSS voor de professionele look
def set_custom_style():
    st.markdown("""
        <style>
        /* Modern Cards */
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
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

# 3. Sidebar
with st.sidebar:
    st.title("Klachten Systeem")
    menu = st.radio("Navigatie", ["Dashboard", "Klacht Indienen"])

# 4. Dashboard Logica
if menu == "Dashboard":
    st.title("Dashboard")
    
    # Grid met 3 statistiek-cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h3>Nieuwe Klachten</h3><div class="stat-value">12</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>In Behandeling</h3><div class="stat-value">5</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h3>Afgehandeld</h3><div class="stat-value">7</div></div>', unsafe_allow_html=True)

# 5. Klacht Indienen Pagina
elif menu == "Klacht Indienen":
    st.title("Klacht Indienen")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.form("klacht_form"):
        st.subheader("Burger Gegevens")
        col_a, col_b = st.columns(2)
        with col_a:
            naam = st.text_input("Volledige Naam")
        with col_b:
            id_nummer = st.text_input("ID-Nummer")
        
        st.subheader("Details van de Klacht")
        soort = st.selectbox("Wat voor soort klacht is het?", ["Selecteer...", "Infrastructuur", "Dienstverlening", "Overig"])
        omschrijving = st.text_area("Korte omschrijving van de klacht")
        
        submit = st.form_submit_button("Indienen")
        
        if submit:
            st.success("Klacht succesvol verzonden!")
    st.markdown('</div>', unsafe_allow_html=True)
