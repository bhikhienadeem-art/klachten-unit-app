import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INITIALISATIE ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER ---
col_l, col_r = st.columns([1, 4])
with col_l:
    st.image("orgineel logo Centrum.png", width=150)
with col_r:
    st.title("Klachtenunit Commissariaat Wanica Centrum")

# ... (Bovenaan je code blijft alles hetzelfde)

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    # ... (Jouw bestaande medewerkers logica: Dashboard, Rapporten, Instellingen)
    # [Laat dit deel staan zoals het is]
    pass 

else:
    # --- BURGERS PAGINA ---
    st.subheader("Welkom bij de Klachtenunit")
    
    # Gebruik tabs om de twee opties voor burgers te scheiden
    tab1, tab2 = st.tabs(["📝 Klacht indienen", "🗓️ Afspraak maken"])
    
    with tab1:
        # --- JOUW ORIGINELE KLACHTEN FORMULIER ---
        with st.form("klacht_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            naam = col1.text_input("👤 Volledige naam")
            id_nr = col1.text_input("🆔 ID Nummer")
            telefoon = col1.text_input("📞 Telefoon/WhatsApp nummer")
            woonadres = col1.text_input("🏠 Woonadres")
            email = col2.text_input("📧 E-mailadres")
            soort = col2.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
            omschrijving = st.text_area("📝 Omschrijving")
            uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'jpeg', 'pdf'])
            
            if st.form_submit_button("Verstuur"):
                file_url = None
                if uploaded_file is not None:
                    file_path = f"bijlagen/{uploaded_file.name}"
                    try:
                        supabase.storage.from_("bijlagen").upload(file_path, uploaded_file.getvalue())
                        file_url = supabase.storage.from_("bijlagen").get_public_url(file_path)
                    except Exception as e:
                        st.error(f"Fout bij uploaden bestand: {e}")

                data = {
                    "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                    "adres": woonadres, "email": email, "klachtensoort": soort,
                    "omschrijving": omschrijving, "status": "Nieuw", "bijlage_url": file_url
                }
                supabase.table("klachten").insert(data).execute()
                st.success("✅ Klacht inclusief bijlage verzonden!")

    with tab2:
        # --- NIEUWE AFSPRAKEN MODULE ---
        st.subheader("🗓️ Afspraak maken (Ma-Vr: 08:00 - 14:00)")
        with st.form("afspraak_form", clear_on_submit=True):
            naam_afspraak = st.text_input("Uw Naam")
            datum = st.date_input("Kies datum")
            
            # Tijdslots genereren van 08:00 tot 14:00
            tijdstippen = [t.strftime("%H:%M") for t in pd.date_range("08:00", "14:00", freq="15min")]
            tijd = st.selectbox("Selecteer tijdstip (15 min per afspraak)", tijdstippen)
            reden = st.text_area("Reden van bezoek")
            
            if st.form_submit_button("Afspraak Bevestigen"):
                # Controleer of het een werkdag is (maandag t/m vrijdag)
                if datum.weekday() >= 5:
                    st.error("⚠️ Afspraken zijn alleen mogelijk op werkdagen (maandag t/m vrijdag).")
                else:
                    supabase.table("afspraken").insert({
                        "naam": naam_afspraak,
                        "datum": str(datum),
                        "tijdstip": tijd,
                        "reden": reden
                    }).execute()
                    st.success(f"✅ Afspraak bevestigd op {datum} om {tijd}!")
