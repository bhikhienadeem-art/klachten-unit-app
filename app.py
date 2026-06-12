import streamlit as st
import requests
import pandas as pd

# 1. Pagina-instellingen
st.set_page_config(
    page_title="Klachten Unit - Commissariaat Wanica Centrum",
    page_icon="📋",
    layout="wide"
)

# 2. Haal de verbindingstokens veilig op uit de Secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
except Exception as e:
    st.error("Secrets niet gevonden. Zorg ervoor dat SUPABASE_URL en SUPABASE_KEY in Streamlit Cloud zijn ingevuld.")
    st.stop()

# 3. Navigatie via de zijbalk (Sidebar)
st.sidebar.title("Navigatie")
pagina = st.sidebar.radio("Ga naar:", ["📋 Klacht Indienen", "🔒 Medewerkers Dashboard"])

# ==============================================================================
# PAGINA 1: KLACHT INDIENEN (BURGER)
# ==============================================================================
if pagina == "📋 Klacht Indienen":
    st.title("📋 Klachten Unit Wanica Centrum")
    st.write("Vul het onderstaande formulier in om uw melding officieel te registreren.")
    st.markdown("---")

    # Formuliervelden
    st.subheader("👤 Gegevens van de Melder")
    volledige_naam = st.text_input("Volledige Naam", placeholder="Voor- en achternaam")
    id_nummer = st.text_input("ID-Nummer", placeholder="Bijv. FI000000M")
    adres = st.text_input("Adres / Woonomgeving", placeholder="Straatnaam en ressort")
    telefoon_whatsapp = st.text_input("Telefoon- / WhatsApp-nummer", placeholder="Bijv. +597 8xxxxxx")

    st.markdown("---")

    st.subheader("📝 Details van de Klacht")
    klachtensoort = st.text_input("Wat voor soort klacht is het?", placeholder="Bijv. Wegen, Vuilophaal, Wateroverlast")
    omschrijving = st.text_area("Korte omschrijving van de klacht", placeholder="Beschrijf hier uw klacht...")

    st.markdown("---")

    if st.button("Klacht Officieel Indienen", type="primary"):
        if not volledige_naam.strip() or not klachtensoort.strip() or not omschrijving.strip():
            st.warning("Vul ten minste de verplichte velden in: Naam, Klachtensoort en Omschrijving.")
        else:
            with st.spinner("Uw klacht wordt rechtstreeks naar de database verzonden..."):
                
                # We bouwen het datapakket exact op volgens jouw database kolommen
                data_pakket = {
                    "volledige_naam": str(volledige_naam),
                    "id_nummer": str(id_nummer),
                    "adres": str(adres),
                    "telefoon_whatsapp": str(telefoon_whatsapp),
                    "klachtensoort": str(klachtensoort),
                    "omschrijving": str(omschrijving),
                    "status": "Nieuw"
                }

                # Directe REST API headers voor PostgREST (Supabase)
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                }

                # Het exacte, directe endpoint naar de 'klachten' tabel
                rest_url = f"{SUPABASE_URL}/rest/v1/klachten"

                try:
                    # We omzeilen de supabase-py bibliotheek en schieten de data direct naar de REST API
                    response = requests.post(rest_url, json=data_pakket, headers=headers)
                    
                    if response.status_code in [200, 201]:
                        st.success("🎉 Uw klacht is succesvol ontvangen en direct opgeslagen in het systeem!")
                        st.balloons()
                    else:
                        st.error(f"⚠️ De database accepteert de verbinding niet (Statuscode: {response.status_code}).")
                        st.json(response.json())
                except Exception as api_error:
                    st.error("⚠️ Er kon geen netwerkverbinding met de database tot stand worden gebracht.")
                    st.text(str(api_error))

# ==============================================================================
# PAGINA 2: MEDEWERKERS DASHBOARD
# ==============================================================================
elif pagina == "🔒 Medewerkers Dashboard":
    st.title("🔒 Medewerkers Dashboard")
    wachtwoord = st.text_input("Voer het medewerkerswachtwoord in:", type="password")
    
    if wachtwoord == "Wanica2026":
        st.success("Toegang verleend!")
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        rest_url = f"{SUPABASE_URL}/rest/v1/klachten?select=*"
        
        try:
            response = requests.get(rest_url, headers=headers)
            if response.status_code == 200:
                klachten_data = response.json()
                if not klachten_data:
                    st.info("Er zijn nog geen klachten aanwezig.")
                else:
                    df = pd.DataFrame(klachten_data)
                    st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Kon gegevens niet ophalen via API. Statuscode: {response.status_code}")
        except Exception as e:
            st.error(f"Netwerkfout: {str(e)}")
