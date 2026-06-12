import streamlit as st
import uuid

# --- BESTAANDE VELDEN ---
telefoon = st.text_input("Telefoon- / WhatsApp-nummer")
email = st.text_input("E-mailadres (Optioneel)")

# Verondersteld dat je dit al had voor het type klacht
type_klacht = st.selectbox("Wat voor soort klacht is het?", ["Selecteer...", "Infrastructuur", "Milieu", "Overig"]) 
omschrijving = st.text_area("Korte omschrijving van de klacht")

# --- NIEUWE VELDEN ---
oplossing = st.text_area("Wat ziet u zelf als de gewenste oplossing? (Optioneel)")

# File uploader voor foto's en documenten
uploaded_files = st.file_uploader(
    "Bijlagen toevoegen (Foto's of documenten)", 
    type=["png", "jpg", "jpeg", "pdf", "docx"], 
    accept_multiple_files=True
)

st.markdown("---")

# --- VERWERKINGS LOGICA ---
if st.button("Klacht Officieel Indienen", type="primary"):
    if telefoon and omschrijving:  # Basis validatie
        
        bijlagen_urls = []
        
        # 1. Bestanden uploaden naar Supabase Storage (als er bestanden zijn geselecteerd)
        if uploaded_files:
            for file in uploaded_files:
                # Unieke naam genereren om overschrijven in de storage bucket te voorkomen
                ext = file.name.split(".")[-1]
                unieke_bestandsnaam = f"{uuid.uuid4()}.{ext}"
                
                try:
                    # Uploaden naar de bucket 'klachten-bijlagen'
                    # Zorg ervoor dat je deze bucket al hebt aangemaakt in Supabase Storage!
                    supabase.storage.from_('klachten-bijlagen').upload(
                        path=unieke_bestandsnaam,
                        file=file.getvalue(),
                        file_options={"content-type": file.type}
                    )
                    
                    # Haal de openbare URL op
                    url_res = supabase.storage.from_('klachten-bijlagen').get_public_url(unieke_bestandsnaam)
                    bijlagen_urls.append(url_res)
                    
                except Exception as e:
                    st.error(f"Fout bij het uploaden van {file.name}: {e}")
                    
        # 2. Data klaarmaken voor de database
        klacht_data = {
            "telefoon_nummer": telefoon,
            "email": email if email else None,
            "type_klacht": type_klacht,
            "omschrijving": omschrijving,
            "gewenste_oplossing": oplossing if oplossing else None,
            "status": "Nieuw",         # Dit vult automatisch je status kolom
            "bijlagen": { "urls": bijlagen_urls }  # Wordt als JSON object opgeslagen: {"urls": ["link1", "link2"]}
        }
        
        # 3. Insert uitvoeren in de Supabase tabel
        try:
            response = supabase.table("klachten").insert(klacht_data).execute()
            
            if response.data:
                st.success("🎉 Uw klacht is succesvol ontvangen en opgeslagen!")
                # Optioneel: st.rerun() om het formulier leeg te maken
            else:
                st.error("Er ging iets mis bij het opslaan van de gegevens.")
        except Exception as e:
            st.error(f"Database fout: {e}")
            
    else:
        st.warning("Vul alstublieft de verplichte velden in (Telefoonnummer en Korte omschrijving).")
