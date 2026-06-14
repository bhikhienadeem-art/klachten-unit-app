import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURATIE ---
SUPABASE_URL = "https://hyxfprmtdqgocrgmvoyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5eGZwcm10ZHFnb2NyZ212b3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTE2MjgwOCwiZXhwIjoyMDk2NzM4ODA4fQ.crzk5TxZ5F27Ic_34kI7HSikAsvBgO9KfnXxGxVhFk8" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Klachten Unit Wanica", layout="wide")

# --- HEADER ---
st.markdown("""
    <style>
    .header-bar { background-color: #004a99; color: white; padding: 25px; text-align: center; border: 5px solid #ffcc00; border-radius: 10px; margin-bottom: 30px; }
    .header-text { margin-top: 10px; font-size: 1.1em; font-style: italic; }
    .contact-info { font-size: 0.95em; margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); }
    </style>
    <div class="header-bar">
        <h1>Klachtenunit Commissariaat Wanica Centrum</h1>
        <div class="header-text">
            Welkom op de pagina van het Klachtenunit van het Commissariaat Wanica Centrum.
        </div>
        <div class="contact-info">
            📍 <b>Adres:</b> Tawajarieweg 20 | 📞 <b>Tel:</b> (+597) 366660 | 💬 <b>WhatsApp:</b> (+597) 8921062
        </div>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATIE & LOGIN ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

with st.sidebar:
    st.header("🔑 Medewerkers Inlog")
    if not st.session_state.logged_in:
        gebruiker = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if gebruiker == "admin" and wachtwoord == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Ongeldige gegevens")
    else:
        st.success("Ingelogd als Admin")
        st.session_state.menu = st.radio("Navigatie", ["Dashboard", "Rapporten", "Instellingen"])
        if st.button("Uitloggen"):
            st.session_state.logged_in = False
            st.rerun()

# --- PAGINA LOGICA ---
if st.session_state.logged_in:
    if st.session_state.menu == "Dashboard":
        st.title("📊 Dashboard")
        klachten = supabase.table("klachten").select("*").execute().data
        for k in klachten:
            with st.expander(f"Klacht van: {k.get('volledige_naam', 'Anoniem')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID Nummer:** {k.get('id_nummer', '-')}")
                    st.write(f"**Naam:** {k.get('volledige_naam', '-')}")
                    st.write(f"**E-mail:** {k.get('email', '-')}")
                with col2:
                    st.write(f"**Woonadres:** {k.get('adres', '-')}")
                    st.write(f"**Soort:** {k.get('klachtensoort', '-')}")
                    st.write(f"**Status:** {k.get('status', 'Nieuw')}")
                
                st.write(f"**Omschrijving:** {k.get('omschrijving', '-')}")
                
                if k.get('email'):
                    mail_link = f"mailto:{k['email']}?subject=Update klacht {k.get('id_nummer', '')}"
                    st.markdown(f'<a href="{mail_link}" target="_blank" style="padding:10px; background:#004a99; color:white; border-radius:5px; text-decoration:none;">📧 E-mail cliënt</a>', unsafe_allow_html=True)
                
                st.divider()
                notitie = st.text_area("Interne notitie", value=k.get('interne_notitie', ''), key=f"note_{k['id']}")
                if st.button("Opslaan Notitie", key=f"save_{k['id']}"):
                    supabase.table("klachten").update({"interne_notitie": notitie}).eq("id", k['id']).execute()
                    st.success("Notitie opgeslagen!")
                
                status_opties = ["Nieuw", "In behandeling", "Afgehandeld"]
                huidige = k.get('status', 'Nieuw')
                nieuwe = st.selectbox("Wijzig status", status_opties, index=status_opties.index(huidige) if huidige in status_opties else 0, key=f"status_{k['id']}")
                if st.button("Update Status", key=f"upd_{k['id']}"):
                    supabase.table("klachten").update({"status": nieuwe}).eq("id", k['id']).execute()
                    st.rerun()

    elif st.session_state.menu == "Rapporten":
        st.title("📈 Rapporten & Beheer")
        
        # 1. Data ophalen
        klachten_data = supabase.table("klachten").select("*").execute().data
        df = pd.DataFrame(klachten_data)
        
        if not df.empty:
            # 2. Visuele Grafiek (Taartdiagram)
            st.subheader("Klachten per Status")
            status_counts = df['status'].value_counts()
            st.bar_chart(status_counts) # Je kunt ook st.pie_chart gebruiken
            
            # 3. Tabel met alle gegevens
            st.subheader("Alle Klachten Overzicht")
            st.dataframe(df, use_container_width=True)
            
            # 4. Verwijder functie
            st.divider()
            st.subheader("🗑️ Klacht Verwijderen")
            klacht_id_te_verwijderen = st.selectbox("Selecteer ID om te verwijderen", df['id'].tolist())
            if st.button("Verwijder geselecteerde klacht"):
                supabase.table("klachten").delete().eq("id", klacht_id_te_verwijderen).execute()
                st.success("Klacht verwijderd!")
                st.rerun()
            
            # 5. Opslaan & Printen
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Rapport downloaden (CSV)", csv, "klachten_rapport.csv", "text/csv")
            st.info("💡 Tip: Gebruik CTRL+P om deze pagina af te drukken als PDF.")
        else:
            st.write("Geen klachten gevonden.")
    elif st.session_state.menu == "Instellingen":
        st.title("⚙️ Instellingen")

# --- FORMULIER (Altijd zichtbaar) ---
st.divider()
st.title("Klacht indienen")
with st.form("klacht_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("Volledige naam")
        id_nr = st.text_input("ID Nummer")
        woonadres = st.text_input("Woonadres")
    with col2:
        email = st.text_input("E-mailadres")
        soort = st.selectbox("Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
    omschrijving = st.text_area("Omschrijving")
    if st.form_submit_button("Verstuur klacht"):
        supabase.table("klachten").insert({
            "volledige_naam": naam, "id_nummer": id_nr, "adres": woonadres, 
            "email": email, "klachtensoort": soort, "omschrijving": omschrijving, "status": "Nieuw"
        }).execute()
        st.success("Klacht verzonden!")
