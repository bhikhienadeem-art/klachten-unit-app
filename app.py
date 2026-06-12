import streamlit as st
import uuid
import requests

# --- 1. SUPABASE INITIALISATIE ---
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    supabase_url = st.secrets["SUPABASE_URL"].rstrip('/')
    supabase_key = st.secrets["SUPABASE_KEY"]
else:
    st.error("Supabase configuratie ontbreekt in secrets!")
    st.stop()

# Initialiseer de officiële Supabase Client
try:
    from supabase import create_client, Client
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"Fout bij laden van Supabase client: {e}")
    st.stop()

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
                    
                    # Methode A: Directe API Upload via het officiële REST endpoint
                    upload_url = f"{supabase_url}/storage/v1/object/klachten-bijlagen/{unieke_bestandsnaam}"
                    headers = {
                        "Authorization": f"Bearer {supabase_key}",
                        "apikey": supabase_key,
                        "Content-Type": file.type
                    }
                    
                    try:
                        res = requests.post(upload_url, headers=headers, data=file.getvalue())
                        
                        if res.status_code == 200:
                            pure_url = f"{supabase_url}/storage/v1/object/public/klachten-bijlagen/{unieke_bestandsnaam}"
                            bijlagen_urls.append(pure_url)
                            continue
                        else:
                            # Als de REST API faalt met PGRST125, proberen we direct Methode B (de SDK)
                            raise RuntimeError("REST API route niet bereikbaar, schakel over naar SDK.")
                            
                    except Exception:
                        # Methode B: Fallback via de SDK om eventuele URL-routing problemen te omzeilen
                        try:
                            supabase.storage.from_("klachten-bijlagen").upload(
                                path=unieke_bestandsnaam,
                                file=file.getvalue(),
                                file_options={"content-type": file.type}
                            )
                            pure_url = f"{supabase_url}/storage/v1/object/public/klachten-bijlagen/{unieke_bestandsnaam}"
                            bijlagen_urls.append(pure_url)
                        except Exception as sdk_err:
                            # Veilige weergave van de SDK fout zonder interne 'dict' attribute crashes
                            fout_boodschap = sdk_err.message if hasattr(sdk_err, 'message') else str(sdk_err)
                            st.error(f"Fout bij uploaden van {file.name}: {fout_boodschap}")
                            upload_succesvol = False
                            break
            
            # Data invoeren in de database als de uploads zijn geslaagd
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
                        st.error("Er ging iets mis bij het opslaan in de database.")
                except Exception as db_error:
                    st.error(f"Database fout: {str(db_error)}")
        else:
            st.warning("Vul alstublieft de verplichte velden in: Naam, Telefoonnummer en Omschrijving.")

elif page == "🔒 Medewerkers Dashboard":
    st.title("🔒 Medewerkers Dashboard")
    st.info("Dit gedeelte is klaar om ingericht te worden.")
