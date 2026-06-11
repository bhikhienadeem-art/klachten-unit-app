import streamlit as st
from supabase import create_client, Client
import os

# --- 1. SUPABASE KOPPELING ---
# VERVANG DEZE TWEE STRINGS MET JOUW EIGEN SUPABASE GEGEVENS!
SUPABASE_URL = "https://jouw-project-id.supabase.co"
SUPABASE_KEY = "jouw-anon-public-key-hier"

# Maak verbinding met Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. APP TITEL & STYLING ---
st.set_page_config(page_title="Klachten Unit - Wanica Centrum", page_icon="📝", layout="centered")

st.title("🏛️ Commissariaat Wanica Centrum")
st.subheader("Digitaal Loket - Klachten Unit")
st.write("Burgers kunnen hier officieel een klacht indienen. Vul het formulier hieronder zo volledig mogelijk in.")

st.divider()

# --- 3. HET KLACHTENFORMULIER ---
with st.form("klachten_form", clear_on_submit=True):
    st.write("### 👤 Persoons- & Contactgegevens")
    
    volledige_naam = st.text_input("Volledige Naam", placeholder="Voor- en achternaam")
    id_nummer = st.text_input("ID-Nummer", placeholder="FI123456")
    adres = st.text_input("Woonadres", placeholder="Straatnaam, nummer, wijk")
    telefoon = st.text_input("Telefoon- / WhatsApp-nummer", placeholder="+597 8xxxxxx")
    email = st.text_input("E-mailadres", placeholder="voorbeeld@email.com")
    
    st.divider()
    
    st.write("### 📋 Details van de Klacht")
    
    # Open invoerveld zodat burgers zelf het type klacht kunnen typen
    klachtensoort = st.text_input("Wat voor soort klacht is het?", placeholder="Bijvoorbeeld: Wegen, Vuilophaal, Wateroverlast, etc.")
    
    omschrijving = st.text_area("Korte omschrijving van de klacht", placeholder="Beschrijf hier zo duidelijk mogelijk wat er aan de hand is...")
    
    # Bestandsupload (Foto's of Documenten)
    geupload_bestand = st.file_uploader("Voeg een foto of document toe (optioneel)", type=["png", "jpg", "jpeg", "pdf"])
    
    st.divider()
    
    # Verzendknop
    verzend_knop = st.form_submit_button("Klacht Officieel Indienen")

# --- 4. DATA VERWERKEN NA KLIK OP KNOP ---
if verzend_knop:
    # Controleer of de belangrijkste velden zijn ingevuld
    if not volledige_naam or not id_nummer or not omschrijving:
        st.error("⚠️ Vul alstublieft tenminste uw Naam, ID-nummer en de omschrijving van de klacht in.")
    else:
        with st.spinner("Uw klacht wordt verwerkt..."):
            bijlage_url = None
            
            # Als er een bestand is geüpload, stuur het naar Supabase Storage
            if geupload_bestand is not None:
                try:
                    bestandsnaam = f"{id_nummer}_{geupload_bestand.name}"
                    # Upload naar de bucket 'klachten-bijlagen'
                    res = supabase.storage.from_("klachten-bijlagen").upload(
                        path=bestandsnaam,
                        file=geupload_bestand.getvalue(),
                        file_options={"content-type": geupload_bestand.type}
                    )
                    # Haal de publieke URL op van de geüploade foto
                    bijlage_url = supabase.storage.from_("klachten-bijlagen").get_public_url(bestandsnaam)
                except Exception as e:
                    st.warning(f"Het formulier wordt verzonden, maar de bijlage kon niet worden geüpload: {e}")

            # Sla alle tekstgegevens op in de tabel 'klachten'
            data = {
                "volledige_naam": volledige_naam,
                "id_nummer": id_nummer,
                "adres": adres,
                "telefoon_whatsapp": telefoon,
                "email": email,
                "klachtensoort": klachtensoort,
                "omschrijving": omschrijving,
                "bijlage_url": bijlage_url,
                "status": "Nieuw"
            }
            
            try:
                supabase.table("klachten").insert(data).execute()
                st.success("✅ Uw klacht is succesvol ingediend! Het Commissariaat Wanica Centrum neemt deze zo snel mogelijk in behandeling.")
            except Exception as e:
                st.error(f"Er ging iets mis met het opslaan in de database: {e}")