import streamlit as st
from supabase import create_client, Client
import os
import time

# 1. Pagina-instellingen
st.set_page_config(
    page_title="Klachten Unit - Commissariaat Wanica Centrum",
    page_icon="📋",
    layout="centered"
)

# 2. Supabase Verbinding (Veilig via Secrets)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Database configuratie herstarten vereist. Zorg ervoor dat de Secrets correct zijn ingevuld.")
    st.stop()

# 3. Applicatie Titel & Header
st.title("📋 Klachten Unit Wanica Centrum")
st.write("Welkom bij het officiële klachtenformulier. Vul de velden zo nauwkeurig mogelijk in.")

st.markdown("---")

# 4. Het Formulier
st.subheader("👤 Gegevens van de Melder")
volledige_naam = st.text_input("Volledige Naam", placeholder="Voor- en achternaam")
id_nummer = st.text_input("ID-Nummer", placeholder="Bijv. FI000000M")
adres = st.text_input("Adres / Woonomgeving", placeholder="Straatnaam en district/ressort")
telefoon_whatsapp = st.text_input("Telefoon- / WhatsApp-nummer", placeholder="Bijv. +597 8xxxxxx")

st.markdown("---")

st.subheader("📝 Details van de Klacht")
soort_klacht = st.text_input(
    "Wat voor soort klacht is het?",
    placeholder="Bijvoorbeeld: Wegen, Vuilophaal, Wateroverlast, etc."
)

omschrijving = st.text_area(
    "Korte omschrijving van de klacht",
    placeholder="Beschrijf hier zo duidelijk mogelijk wat er aan de hand is..."
)

bijlage = st.file_uploader(
    "Voeg een foto of document toe (optioneel)",
    type=["png", "jpg", "jpeg", "pdf"]
)

st.markdown("---")

# 5. Verwerkingslogica bij indienen
if st.button("Klacht Officieel Indienen", type="primary"):
    if not volledige_naam.strip() or not soort_klacht.strip() or not omschrijving.strip():
        st.warning("Zorg ervoor dat je ten minste je naam, het soort klacht en de omschrijving invult!")
    else:
        with st.spinner("Uw klacht wordt veilig verwerkt..."):
            try:
                bijlage_url = None

                # Stap A: Als er een bijlage is, upload deze naar Supabase Storage
                if bijlage is not None:
                    file_bytes = bijlage.read()
                    bestandsnaam = f"klacht_{int(time.time())}_{bijlage.name}"
                    
                    # Upload naar de bucket 'klachten-bijlagen'
                    storage_res = supabase.storage.from_("klachten-bijlagen").upload(
                        path=bestandsnaam,
                        file=file_bytes,
                        file_options={"content-type": bijlage.type}
                    )
                    
                    # Haal de publieke link op
                    bijlage_url = supabase.storage.from_("klachten-bijlagen").get_public_url(bestandsnaam)

                # Stap B: Sla alle gegevens op in de database tabel 'klachten'
                supabase.table("klachten").insert({
                    "volledige_naam": volledige_naam,
                    "id_nummer": id_nummer,
                    "adres": adres,
                    "telefoon_whatsapp": telefoon_whatsapp,
                    "soort_klacht": soort_klacht,
                    "omschrijving": omschrijving,
                    "bijlage_url": bijlage_url
                }).execute()

                # Stap C: Succes!
                st.success("🎉 Uw klacht is succesvol ontvangen en geregistreerd bij het Commissariaat!")
                st.balloons()

            except Exception as error:
                st.error(f"Er ging iets mis met het opslaan in de database: {error}")
