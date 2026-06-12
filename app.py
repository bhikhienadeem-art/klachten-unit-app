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
                        file_bytes = bijlage.read()
                        bestandsnaam = f"klacht_{int(time.time())}_{bijlage.name}"
                        
                        storage_res = supabase.storage.from_("klachten-bijlagen").upload(
                            path=bestandsnaam,
                            file=file_bytes,
                            file_options={"content-type": bijlage.type}
                        )
                        bijlage_url = supabase.storage.from_("klachten-bijlagen").get_public_url(bestandsnaam)

                    # Invoegen in de database
                    supabase.table("klachten").insert({
                        "volledige_naam": volledige_naam,
                        "id_nummer": id_nummer,
                        "adres": adres,
                        "telefoon_whatsapp": telepon_whatsapp,
                        "soort_klacht": soort_klacht,
                        "omschrijving": omschrijving,
                        "bijlage_url": bijlage_url
                    }).execute()

                    st.success("🎉 Uw klacht is succesvol ontvangen en geregistreerd bij het Commissariaat!")
                    st.balloons()

                except Exception as error:
                    # Veilige foutweergave die controleert of de fout een dict of object is
                    st.error("⚠️ Er ging iets mis bij het opslaan in de database.")
                    if hasattr(error, 'message'):
                        st.code(error.message, language="text")
                    elif isinstance(error, dict):
                        st.json(error)
                    else:
                        st.code(str(error), language="text")

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
                response = supabase.table("klachten").select("*").order("created_at", ascending=False).execute()
                klachten_data = response.data
                
                if not klachten_data:
                    st.info("Er zijn momenteel nog geen klachten geregistreerd in de database.")
                else:
                    df = pd.DataFrame(klachten_data)
                    kolommen_volgorde = [
                        "id", "created_at", "volledige_naam", "id_nummer", 
                        "telefoon_whatsapp", "adres", "soort_klacht", "omschrijving", "bijlage_url"
                    ]
                    beschikbare_kolommen = [col for col in kolommen_volgorde if col in df.columns]
                    df = df[beschikbare_kolommen]
                    
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Klachtenrapport (CSV)",
                        data=csv,
                        file_name="klachten_rapport_wanica.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"Fout bij het laden van de gegevens: {e}")
    elif wachtwoord != "":
        st.error("Onjuist wachtwoord. Toegang geweigerd.")
