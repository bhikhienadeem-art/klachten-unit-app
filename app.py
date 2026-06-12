import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Pagina-instellingen
st.set_page_config(
    page_title="Klachten Unit - Commissariaat Wanica Centrum",
    page_icon="📋",
    layout="wide"
)

# 2. Supabase Verbinding (Veilig via Secrets)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Database configuratie herstarten vereist. Zorg ervoor dat de Secrets correct zijn ingevuld.")
    st.stop()

# 3. Navigatie via de zijbalk (Sidebar)
st.sidebar.title("Navigatie")
pagina = st.sidebar.radio("Ga naar:", ["📋 Klacht Indienen", "🔒 Medewerkers Dashboard"])

# ==============================================================================
# PAGINA 1: KLACHT INDIENEN (BURGER)
# ==============================================================================
if pagina == "📋 Klacht Indienen":
    st.title("📋 Klachten Unit Wanica Centrum")
    st.write("Welkom bij het officiële klachtenformulier. Vul de velden zo nauwkeurig mogelijk in.")
    st.markdown("---")

    # Het Formulier - Burgergegevens
    st.subheader("👤 Gegevens van de Melder")
    volledige_naam = st.text_input("Volledige Naam", placeholder="Voor- en achternaam")
    id_nummer = st.text_input("ID-Nummer", placeholder="Bijv. FI000000M")
    adres = st.text_input("Adres / Woonomgeving", placeholder="Straatnaam en ressort")
    telefoon_whatsapp = st.text_input("Telefoon- / WhatsApp-nummer", placeholder="Bijv. +597 8xxxxxx")

    st.markdown("---")

    # Het Formulier - Klachtdetails
    st.subheader("📝 Details van de Klacht")
    klachtensoort = st.text_input("Wat voor soort klacht is het?", placeholder="Bijvoorbeeld: Wegen, Vuilophaal, Wateroverlast, etc.")
    omschrijving = st.text_area("Korte omschrijving van de klacht", placeholder="Beschrijf hier zo duidelijk mogelijk wat er aan de hand is...")

    st.markdown("---")

    if st.button("Klacht Officieel Indienen", type="primary"):
        if not volledige_naam.strip() or not klachtensoort.strip() or not omschrijving.strip():
            st.warning("Zorg ervoor dat je ten minste je naam, het soort klacht en de omschrijving invult!")
        else:
            with st.spinner("Uw klacht wordt veilig verwerkt..."):
                try:
                    # Invoegen in de database (EXACT gematcht met jouw databasekolommen)
                    data_to_insert = {
                        "volledige_naam": str(volledige_naam),
                        "id_nummer": str(id_nummer),
                        "adres": str(adres),
                        "telefoon_whatsapp": str(telefoon_whatsapp),
                        "klachtensoort": str(klachtensoort),
                        "omschrijving": str(omschrijving),
                        "status": "Nieuw"  # Standaard status meegeven aan de status-kolom
                    }

                    # Veilige aanroep om interne postgrest-py bugs te voorkomen
                    supabase.table("klachten").insert(data_to_insert).execute()

                    st.success("🎉 Uw klacht is succesvol ontvangen en geregistreerd bij het Commissariaat!")
                    st.balloons()

                except Exception as error:
                    st.error("⚠️ De database weigert de gegevens op te slaan.")
                    st.info("Controleer of de applicatie-secrets in Streamlit Cloud gekoppeld zijn aan de juiste database.")
                    st.text(f"Foutdetails: {str(error)}")

# ==============================================================================
# PAGINA 2: MEDEWERKERS DASHBOARD (BEVEILIGD)
# ==============================================================================
elif pagina == "🔒 Medewerkers Dashboard":
    st.title("🔒 Medewerkers Dashboard")
    st.write("Dit gedeelte is uitsluitend toegankelijk voor geautoriseerd personeel.")
    
    wachtwoord = st.text_input("Voer het centrale medewerkerswachtwoord in:", type="password")
    
    if wachtwoord == "Wanica2026":
        st.success("Toegang verleend!")
        st.subheader("📋 Overzicht Ingediende Klachten")
        
        with st.spinner("Klachten ophalen uit de database..."):
            try:
                # Haal gegevens op uit de 'klachten' tabel
                response = supabase.table("klachten").select("*").execute()
                klachten_data = response.data
                
                if not klachten_data:
                    st.info("Er zijn momenteel nog geen klachten geregistreerd.")
                else:
                    df = pd.DataFrame(klachten_data)
                    
                    # Kolommen netjes sorteren voor het overzicht van de medewerker
                    kolommen_volgorde = [
                        "id", "created_at", "status", "volledige_naam", "id_nummer", 
                        "telefoon_whatsapp", "adres", "klachtensoort", "omschrijving"
                    ]
                    beschikbare_kolommen = [col for col in kolommen_volgorde if col in df.columns]
                    df = df[beschikbare_kolommen]
                    
                    st.dataframe(df, use_container_width=True)
                    
                    # Exporteren naar Excel/CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Klachtenrapport (CSV)",
                        data=csv,
                        file_name="klachten_rapport_wanica.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"Fout bij het laden van de gegevens: {str(e)}")
    elif wachtwoord != "":
        st.error("Onjuist wachtwoord. Toegang geweigerd.")
