# --- INDIENEN KLACHT ---
    with st.form("klacht_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        naam = col1.text_input("Naam")
        id_nr = col1.text_input("ID Nummer")
        telefoon = col1.text_input("Telefoon")
        woonadres = col1.text_input("Woonadres")
        email = col2.text_input("E-mail")
        soort = col2.selectbox("Soort", ["Afval", "Wegen", "Wateroverlast", "Anders"])
        omschrijving = st.text_area("Omschrijving")
        file = st.file_uploader("Bijlage")
        
        if st.form_submit_button("Verstuur Klacht"):
            t_id = f"WAN-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            supabase.table("klachten").insert({
                "volledige_naam": naam, "id_nummer": id_nr, "telefoon_whatsapp": telefoon,
                "adres": woonadres, "email": email, "omschrijving": omschrijving,
                "status": "Nieuw", "ticket_id": t_id, "klachtensoort": soort
            }).execute()
            
            # VRIENDELIJKE MAIL VOOR CLIENT
            html_client = f"""
            <div style="font-family: Arial;">
                <h2 style="color:#004a99;">Uw melding is in goede orde ontvangen</h2>
                <p>Beste {naam},</p>
                <p>Hartelijk dank voor het indienen van uw klacht bij het Commissariaat Wanica Centrum.</p>
                <p>Uw melding (Referentie: <b>{t_id}</b>) is in behandeling genomen door ons team. Wij houden u via de e-mail op de hoogte van de voortgang.</p>
                <p>Met vriendelijke groet,<br><b>Klachtenunit Wanica Centrum</b></p>
            </div>"""
            stuur_mail(email, "Bevestiging van uw klacht", html_client)
            
            # GEDETAILLEERDE MAIL VOOR MEDEWERKER
            html_med = f"""
            <div style="font-family: Arial;">
                <h2 style="color:#d32f2f;">Nieuwe klacht gemeld: {t_id}</h2>
                <p>Er is zojuist een nieuwe klacht binnengekomen via het portaal. Hieronder staan de details:</p>
                <table border="1" cellpadding="10" style="border-collapse:collapse; width:100%;">
                    <tr><td><b>Naam:</b></td><td>{naam}</td></tr>
                    <tr><td><b>ID Nummer:</b></td><td>{id_nr}</td></tr>
                    <tr><td><b>Telefoon:</b></td><td>{telefoon}</td></tr>
                    <tr><td><b>Adres:</b></td><td>{woonadres}</td></tr>
                    <tr><td><b>Soort klacht:</b></td><td>{soort}</td></tr>
                    <tr><td><b>Omschrijving:</b></td><td>{omschrijving}</td></tr>
                </table>
                <p>Eventuele bewijsstukken vindt u in de bijlage van deze e-mail.</p>
            </div>"""
            stuur_mail("klachtenunitwanicacentrum@gmail.com", f"Nieuwe Klacht: {t_id}", html_med, bestand=file)
            
            st.success("✅ Uw klacht is verzonden. Bedankt voor uw melding!")
