from groq import Groq

GROQ_API_KEY = "";  

client = Groq(api_key=GROQ_API_KEY)

def generate_answer(query, context):
    
    
    MAX_ZNAKOVA = 6000
    if context and len(context) > MAX_ZNAKOVA:
        print(f"⚠️ Upozorenje: Kontekst je predugačak ({len(context)} znakova). Skraćujem na {MAX_ZNAKOVA}...")
        context = context[:MAX_ZNAKOVA] + "\n\n... [Tekst zakona je skraćen radi optimizacije API-ja] ..."
    
    system_instruction = """
    Ti si napredni pravni asistent za hrvatske zakone. Tvoj zadatak je detaljno i 
    jasno odgovoriti na korisnikovo pitanje na temelju ustupljenog teksta zakona.
    
    PRAVILA:
    1. Odgovaraj isključivo na hrvatskom jeziku, prirodnim, tečnim i profesionalnim tonom.
    2. Koristi samo činjenice iz ustupljenog teksta. Ne izmišljaj vanjske informacije.
    3. Odgovor treba biti opširniji i detaljniji. Ako tekst sadrži tablicu, listu ili više opcija (npr. različita trajanja otkaznih rokova), nemoj izabrati samo jedan primjer, već u obliku kratkog odlomka objasni cijeli raspon i uvjete kako bi korisnik dobio potpunu sliku.
    4. Odgovori moraju biti koncizni, izravni i duljine do nekoliko rečenica. Obavezno završi svaku započetu misao i nemoj ostavljati nedovršene rečenice.
    5. Ako u ustupljenom tekstu nema odgovora na pitanje, odgovori točno ovako: "Na temelju pronađenih članaka zakona, ne mogu odgovoriti na ovo pitanje."
    """

    user_content = f"""
    USTUPLJENI TEKST ZAKONA NA TEMELJU KOJEG MORAŠ ODGOVORITI:
    {context}

    KORISNIKOVO PITANJE:
    {query}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1,  # Blago povišeno za prirodniji i bogatiji rječnik
        max_tokens=2000    # Povećano da model može ispisati opširan odgovor
    )

    return response.choices[0].message.content.strip() 
