import streamlit as st
from supabase import create_client, Client
import os
import time  # Netjes toegevoegd voor unieke bestandsnamen!

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
st.title("📋 Details van de Klacht")
st.write("Welkom bij het officiële klachtenformulier van het Commissariaat Wanica Centrum.")
st.write("Vul de onderstaande velden zo nauwkeurig mogelijk in.")

st.markdown("---")

# 4. Het Formulier
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
    if not soort_klacht.strip() or not omschrijving.strip():
        st.warning("Zorg ervoor dat je zowel de soort klacht als de omschrijving invult!")
    else:
        with st.spinner("Uw klacht wordt veilig verwerkt..."):
            try:
                bijlage_url = None

                # Stap A: Als er een bijlage is, upload deze naar Supabase Storage
                if bijlage is not None:
                    file_bytes = bijlage.read()
                    # Maak een unieke bestandsnaam met time.time()
                    bestandsnaam = f"klacht_{int(time.time())}_{bijlage.name}"
                    
                    # Upload naar de bucket 'klachten-bijlagen'
                    storage_res = supabase.storage.from_("klachten-bijlagen").upload(
                        path=bestandsnaam,
                        file=file_bytes,
                        file_options={"content-type": bijlage.type}
                    )
                    
                    # Haal de publieke link op
                    bijlage_url = supabase.storage.from_("klachten-bijlagen").get_public_url(bestandsnaam)

                # Stap B: Sla op in de database tabel 'klachten'
                data, count = supabase.table("klachten").insert({
                    "soort_klacht": soort_klacht,
                    "omschrijving": omschrijving,
                    "bijlage_url": bijlage_url
                }).execute()

                # Stap C: Succes!
                st.success("🎉 Uw klacht is succesvol ontvangen en geregistreerd bij het Commissariaat!")
                st.balloons()

            except Exception as error:
                st.error(f"Er ging iets mis met het opslaan in de database: {error}")
