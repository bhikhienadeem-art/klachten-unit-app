import streamlit as st
import uuid
from supabase import create_client, Client

# --- 1. SUPABASE INITIALISATIE ---
@st.cache_resource
def init_supabase() -> Client:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- 2. PAGINA-INDELING & NAVIGATIE ---
st.set_page_config(page_title="Klachten Unit - Commissariaat Wanica Centrum", page_icon="📝", layout="centered")

page = st.sidebar.radio("Ga naar:", ["📝 Klacht Indienen", "🔒 Medewerkers Dashboard"])

if page == "📝 Klacht Indienen":
    st.title("📝 Klacht Indienen")
    st.subheader("Burger Gegevens")
    
    volledige_naam = st.text_input("Volledige Naam")
    id_nummer = st.text_input("ID-Nummer")
    adres = st.text_input("Adres")
    telefoon = st.text_input("Telefoon- / WhatsApp-nummer")
    email = st.text_input("E-mailadres (Optioneel)")
    
    st.subheader("Details van de Klacht")
    
    klachtensoort = st.selectbox(
        "Wat voor soort klacht is het?", 
        ["Selecteer...", "Infrastructuur", "Milieu", "Grondzaken", "Wegen & Waterkant", "Overig"]
    )
    
    omschrijving = st.text_area("Korte omschrijving van de klacht")
    oplossing = st.text_area("Wat ziet u zelf als de gewenste oplossing? (Optioneel)")
    
    uploaded_files = st.file_uploader(
        "Bijlagen toevoegen (Foto's of documenten)", 
        type=["png", "jpg", "jpeg", "pdf", "docx"], 
        accept_multiple_files=True
    )
    
    st.markdown("---")
    
    # --- 3. VERWERKINGS LOGICA ---
    if st.button("Klacht Officieel Indienen", type="primary"):
        if volledige_naam.strip() and telefoon.strip() and omschrijving.strip():
            
            bijlagen_urls = []
            upload_succesvol = True
            
            if uploaded_files:
                for file in uploaded_files:
                    ext = file.name.split(".")[-1]
                    unieke_bestandsnaam = f"{uuid.uuid4()}.{ext}"
                    
                    try:
                        # Haal de rauwe bytes op
                        file_bytes = file.getvalue()
                        
                        # Upload direct naar de bucket
                        supabase.storage.from_('klachten-bijlagen').upload(
                            path=unieke_bestandsnaam,
                            file=file_bytes
                        )
                        
                        # Publieke URL opvragen
                        url_data = supabase.storage.from_('klachten-bijlagen').get_public_url(unieke_bestandsnaam)
                        
                        # Veilige extractie van de URL string, ongeacht de SDK versie
                        if isinstance(url_data, str):
                            pure_url = url_data
                        elif isinstance(url_data, dict) and "publicUrl" in url_data:
                            pure_url = url_data["publicUrl"]
                        elif hasattr(url_data, "public_url"):
                            pure_url = url_data.public_url
                        else:
                            # Fallback: handmatig de URL opbouwen als de SDK vreemd doet
                            supabase_url = st.secrets["SUPABASE_URL"].rstrip('/')
                            pure_url = f"{supabase_url}/storage/v1/object/public/klachten-bijlagen/{unieke_bestandsnaam}"
                            
                        bijlagen_urls.append(pure_url)
                        
                    except Exception as upload_error:
                        # Converteer de error expliciet naar string om '.text' issues te omzeilen
                        st.error(f"Fout bij het uploaden van {file.name}: {str(upload_error)}")
                        upload_succesvol = False
            
            # Alleen opslaan als de uploads zijn geslaagd
            if upload_succesvol:
                klacht_data = {
                    "volledige_naam": volledige_naam,
                    "id_nummer": id_nummer if id_nummer else None,
                    "adres": adres if adres else None,
                    "telefoon_whatsapp": telefoon,
                    "email": email if email else None,
                    "klachtensoort": klachtensoort if klachtensoort != "Selecteer..." else "Overig",
                    "omschrijving": omschrijving,
                    "gewenste_oplossing": oplossing if oplossing else None,
                    "status": "Nieuw",
                    "bijlagen": { "urls": bijlagen_urls }
                }
                
                try:
                    response = supabase.table("klachten").insert(klacht_data).execute()
                    
                    if response.data:
                        st.success("🎉 Uw klacht is succesvol ontvangen en opgeslagen!")
                    else:
                        st.error("Er ging iets mis bij het opslaan van de gegevens.")
                except Exception as db_error:
                    st.error(f"Database fout: {str(db_error)}")
        else:
            st.warning("Vul alstublieft de verplichte velden in: Naam, Telefoonnummer en Omschrijving.")

elif page == "🔒 Medewerkers Dashboard":
    st.title("🔒 Medewerkers Dashboard")
    st.info("Dit gedeelte is klaar om in de volgende stap ingericht te worden.")
