import streamlit as st

# 1. Pagina configuratie: zet op 'wide' voor de dashboard layout
st.set_page_config(page_title="Klachten Dashboard", layout="wide")

# 2. Custom CSS voor de 'Card' look (schaduw, afgeronde hoeken)
def set_custom_style():
    st.markdown("""
        <style>
        .card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            margin-bottom: 20px;
        }
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

# 3. Sidebar Menu
with st.sidebar:
    st.title("Menu")
    st.radio("Ga naar:", ["Klacht Indienen", "Medewerkers Dashboard"])

# 4. Main Dashboard Layout
st.title("Klachten Dashboard")

# Bovenste rij: 3 Cards (vergelijkbaar met jouw voorbeeld)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><h3>Nieuwe Klachten</h3><p>12 dit jaar</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card"><h3>In Behandeling</h3><p>5 lopend</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="card"><h3>Afgehandeld</h3><p>7 voltooid</p></div>', unsafe_allow_html=True)

# Middelste rij: Formulier (in een card) + Tabel
form_col, info_col = st.columns([2, 1])

with form_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Klacht Indienen")
    with st.form("klacht_form"):
        naam = st.text_input("Volledige Naam")
        klacht = st.text_area("Omschrijving van de klacht")
        submit = st.form_submit_button("Indienen")
    st.markdown('</div>', unsafe_allow_html=True)

with info_col:
    st.markdown('<div class="card"><h3>Snelle Stats</h3><p>Respons tijd: 24u</p></div>', unsafe_allow_html=True)
