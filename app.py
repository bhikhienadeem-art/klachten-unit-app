# --- FORMULIER ---
st.divider()
st.subheader("📝 Klacht indienen")
st.info("Vul onderstaand formulier in om uw klacht kenbaar te maken.")

# We splitsen het formulier op: Klacht info apart, Afspraak apart
with st.form("klacht_form_totaal"):
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("👤 Volledige naam")
        id_nr = st.text_input("🆔 ID Nummer")
        telefoon = st.text_input("📞 Telefoon/WhatsApp nummer")
        woonadres = st.text_input("🏠 Woonadres")
    with col2:
        email = st.text_input("📧 E-mailadres")
        soort = st.selectbox("📋 Soort klacht", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        uploaded_file = st.file_uploader("📎 Voeg foto of document toe", type=['png', 'jpg', 'pdf'])
        
    omschrijving = st.text_area("📝 Geef hier een korte omschrijving van uw klacht")

    # --- AFSPRAAK SECTIE (Visueel onderin het formulier) ---
    st.divider()
    st.subheader("📅 Afspraak maken (Optioneel)")
    st.write("Wilt u een fysieke afspraak maken? Kies hieronder datum en tijd.")
    
    col_cal1, col_cal2 = st.columns(2)
    with col_cal1:
        afspraak_datum = st.date_input("Kies datum")
    with col_cal2:
        tijden = [f"{h:02d}:{m:02d}" for h in range(8, 14) for m in [0, 15, 30, 45]] + ["14:00"]
        afspraak_tijd = st.selectbox("Kies tijdstip", tijden)
    
    submit = st.form_submit_button("Verstuur klacht & Afspraak")

if submit:
    supabase.table("klachten").insert({
        "volledige_naam": naam, "id_nummer": id_nr, "telefoon": telefoon, "adres": woonadres, 
        "email": email, "klachtensoort": soort, "omschrijving": omschrijving, 
        "status": "Nieuw", "bijlage_url": uploaded_file.name if uploaded_file else None,
        "afspraak_datum": str(afspraak_datum),
        "afspraak_tijd": afspraak_tijd
    }).execute()
    st.success(f"✅ Uw klacht is verzonden! Afspraak gepland op {afspraak_datum} om {afspraak_tijd}.")
