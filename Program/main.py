import uvicorn
from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from typing import List
from search_chroma import search_chroma
from ai_response import generate_answer
from baza import inicijaliziranje_baze, spremi_prvo_pitanje, sesija_postoji, dohvati_sve_sesije, obrisi_sesiju 

app = FastAPI(title="AI Zakonik - API")

inicijaliziranje_baze() 

# Omogućavamo CORS kako bi React mogao slati zahtjeve FastAPI-ju
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PYDANTIC MODELI ZA VALIDACIJU ---

# Što nam React šalje (npr. {"pitanje": "Koliko traje otkazni rok?"})
class ChatRequest(BaseModel):
    session_id: str
    pitanje: str

# Kako izgleda pojedinačna kartica izvora
class IzvorModel(BaseModel):
    zakon: str
    clanak: str
    tekst: str

# Što FastAPI vraća natrag u React
class ChatResponse(BaseModel):
    odgovor_ai: str
    izvori: List[IzvorModel]

# --- ENDPOINT ---

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        upit = request.pitanje
        s_id = request.session_id
        
        if not sesija_postoji(s_id):
            # Ako sesija ne postoji u bazi, ovo je PRVO pitanje! Spremi ga.
            spremi_prvo_pitanje(s_id, upit)

        # 1. Pozivamo funkciju iz search_chroma.py
        results = search_chroma(upit)

        # Osigurač: Ako ChromaDB ne vrati ništa
        if not results or 'documents' not in results or not results['documents'][0]:
            return ChatResponse(
                odgovor_ai="Na temelju pronađenih članaka zakona, ne mogu odgovoriti na ovo pitanje.",
                izvori=[]
            )

        # 2. Skupljamo tekstove za kontekst 
        svi_tekstovi = []
        for i in range(len(results['documents'][0])):
            tekst = results['documents'][0][i]
            svi_tekstovi.append(tekst)
        
        kontekst_za_ai = "\n\n".join(svi_tekstovi)

        # 3. Pozivamo funkciju iz ai_response.py za Groq LLM
        odgovor_iz_ai = generate_answer(upit, kontekst_za_ai)

        # 4. Pakiramo izvore u strukturiranu listu za React kartice
        formatirani_izvori = []
        for i in range(len(results['documents'][0])):
            meta = results['metadatas'][0][i]
            tekst = results['documents'][0][i]
            
            formatirani_izvori.append(
                IzvorModel(
                    zakon=meta.get('zakon', 'Nepoznat zakon'),
                    clanak=meta.get('naslov', f"Članak {meta.get('clanak', '')}"),
                    tekst=tekst
                )
            )

        # 5. Vraćamo gotov odgovor natrag na frontend
        return ChatResponse(
            odgovor_ai=odgovor_iz_ai,
            izvori=formatirani_izvori
        )

    except Exception as e:
        # Ako se dogodi bilo kakva greška (npr. Groq API ključ, mreža...), baci 500
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/povijest")
async def povijest_endpoint():
    try:
        return dohvati_sve_sesije()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.delete("/api/povijest/{session_id}")
async def obrisi_povijest_endpoint(session_id: str):
    try:
        # Provjeravamo postoji li uopće ta sesija prije brisanja
        if not sesija_postoji(session_id):
            raise HTTPException(status_code=404, detail="Sesija nije pronađena.")
            
        obrisi_sesiju(session_id)
        return {"status": "success", "message": f"Sesija {session_id} je obrisana."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)