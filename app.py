import streamlit as st
from supabase import create_client, Client
import os
import time
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

    # Het Formulier
    st.subheader("👤 Gegevens van de Melder")
    volledige_naam = st.text_input("Volledige Naam", placeholder="Voor- en achternaam")
    id_nummer = st.text_input("ID-Nummer", placeholder="Bijv. FI000000M")
    adres = st.text_input("Adres / Woonomgeving", placeholder="Straatnaam en ressort")
    telefoon_whatsapp = st.text_input("Telefoon- / WhatsApp-nummer", placeholder="Bijv. +597 8xxxxxx")

    st.markdown("---")

    st.subheader("📝 Details van de Klacht")
    soort_klacht = st.text_input("Wat voor soort klacht is het?", placeholder="Bijvoorbeeld: Wegen, Vuilophaal, Wateroverlast, etc.")
    omschrijving = st.text_area("Korte omschrijving van de klacht", placeholder="Beschrijf hier zo duidelijk mogelijk wat er aan de hand is...")
    bijlage = st.file_uploader("Voeg een foto of document toe (optioneel)", type=["png", "jpg", "jpeg", "pdf"])

    st.markdown("---")

    if st.button("Klacht Officieel Indienen", type="primary"):
        if not volledige_naam.strip() or not soort_klacht.strip() or not omschrijving.strip():
            st.warning("Zorg ervoor dat je ten minste je naam, het soort klacht en de omschrijving invult!")
        else:
            with st.spinner("Uw klacht wordt veilig verwerkt..."):
                try:
                    bijlage_url = None

                    # Upload foto naar storage indien aanwezig
                    if bijlage is not None:
                        try:
                            file_bytes = bijlage.read()
                            bestandsnaam = f"klacht_{int(time.time())}_{bijlage.name}"
                            
                            supabase.storage.from_("klachten-bijlagen").upload(
                                path=bestandsnaam,
                                file=file_bytes,
                                file_options={"content-type": bijlage.type}
                            )
                            bijlage_url = supabase.storage.from_("klachten-bijlagen").get_public_url(bestandsnaam)
                        except Exception as storage_err:
                            st.warning(f"⚠️ Kon bijlage niet uploaden, maar we proberen de klacht wel op te slaan. Fout: {storage_err}")

                    # VEILIGE INSERT: We vangen de response direct op zonder geforceerde kettingfuncties
                    query = supabase.table("klachten").insert({
                        "volledige_naam": str(volledige_naam),
                        "id_nummer": str(id_nummer),
                        "adres": str(adres),
                        "telefoon_whatsapp": str(telefoon_whatsapp),
                        "soort_klacht": str(soort_klacht),
                        "omschrijving": str(omschrijving),
                        "bijlage_url": str(bijlage_url) if bijlage_url else None
                    })
                    
                    # Voer handmatig uit om de interne Postgrest-bug te omzeilen
                    result = query.execute()

                    st.success("🎉 Uw klacht is succesvol ontvangen en geregistreerd bij het Commissariaat!")
                    st.balloons()

                except Exception as error:
                    st.error("⚠️ De database weigert de gegevens op te slaan.")
                    st.info("Dit betekent meestal dat een kolomnaam in Supabase niet exact overeenkomt met de code, of dat er missende rechten zijn.")
                    st.text(f"Ruwe foutdetails: {str(error)}")

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
        
        with st.spinner("Klachten ophalen..."):
            try:
                response = supabase.table("klachten").select("*").execute()
                klachten_data = response.data
                
                if not klachten_data:
                    st.info("Er zijn momenteel nog geen klachten geregistreerd.")
                else:
                    df = pd.DataFrame(klachten_data)
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Fout bij het laden van de gegevens: {str(e)}")
    elif wachtwoord != "":
        st.error("Onjuist wachtwoord. Toegang geweigerd.")
