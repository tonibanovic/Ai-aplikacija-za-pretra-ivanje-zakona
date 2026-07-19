import chromadb
from sentence_transformers import SentenceTransformer 
import re 
import os 

# Model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Chroma
skripta_direktorij = os.path.dirname(os.path.abspath(__file__))
chroma_putanja = os.path.join(skripta_direktorij, "chroma_storage")
client = chromadb.PersistentClient(path=chroma_putanja)

collection = client.get_or_create_collection(name="zakoni")

 
def chroma_translation(ime_datoteke):
    putanja_datoteke = os.path.join(skripta_direktorij, "zakoni", ime_datoteke)
    
    print(f"\nPokušavam otvoriti: {putanja_datoteke}")
    
    if not os.path.exists(putanja_datoteke):
        print(f"❌ GREŠKA: Datoteka '{ime_datoteke}' ne postoji u mapi 'zakoni'!")
        return

    try:
        with open(putanja_datoteke, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(putanja_datoteke, "r", encoding="cp1250") as f:
            text = f.read()

    # -----------------------------
    # NAZIV ZAKONA
    # -----------------------------
    lines = text.splitlines()
    naziv_zakona = "Nepoznat zakon"
    for line in lines[:20]:
        line = line.strip()
        if line and "Članak" not in line and "GLAVA" not in line:
            naziv_zakona = line
            break

    
    # Tražimo "Članak [broj]" samo ako je na početku reda, čime izbjegavamo spominjanja unutar teksta.
    pattern = r"^Članak\s+(\d+)\.?"
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    
    print(f"Pronađeno stvarnih članaka u datoteci: {len(matches)}")

    documents = []
    metadatas = []
    ids = []
    
    # Skup (set) u kojem pratimo koje smo ID-ove već iskoristili da spriječimo duplikate
    iskoristeni_idovi = set()

    for i in range(len(matches)):
        start_idx = matches[i].start()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
        
        clanak_tekst = text[start_idx:end_idx].strip()
        broj_clanka = matches[i].group(1)

        if len(clanak_tekst) < 20:
            continue

        cisto_ime = ime_datoteke.replace(".txt", "")
        predlozeni_id = f"{cisto_ime}_clanak_{broj_clanka}"
        
        # OSIGURAČ: Ako ID već postoji (za svaki slučaj), dodajemo pod-broj (npr. _dio_2)
        brojac_duplikata = 1
        konacni_id = predlozeni_id
        while konacni_id in iskoristeni_idovi:
            brojac_duplikata += 1
            konacni_id = f"{predlozeni_id}_dio_{brojac_duplikata}"
            
        iskoristeni_idovi.add(konacni_id)

        documents.append(clanak_tekst)
        metadatas.append({
            "zakon": naziv_zakona,
            "clanak": broj_clanka,
            "naslov": f"Članak {broj_clanka}"
        })
        ids.append(konacni_id)

    if not documents:
        print("Nema valjanih dokumenata za spremanje.")
        return

    # -----------------------------
    # EMBEDDINGS
    # -----------------------------
    print("Generiram embeddings...")
    embeddings = model.encode(
        documents,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    embeddings = embeddings.tolist()
    print("Embeddings gotovi!")

    # -----------------------------
    # SPREMANJE
    # -----------------------------
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Uspješno spremljen zakon: {naziv_zakona}")


# Pokretanje
chroma_translation("Zakon_o_radu.txt")
chroma_translation("Zakon_o_zastiti_potrosaca.txt")
chroma_translation("ZAKON_O_DRŽAVNIM_BLAGDANIMA_SPOMENDANIMA_I_NERADNIM DANIMA.txt")                