import os
import time
import pandas as pd
import csv
from chromadb import PersistentClient
from search_chroma import search_chroma
from ai_response import generate_answer

def pokreni_evaluaciju():
    # Postavke putanja
    direktorij_skripte = os.path.dirname(os.path.abspath(__file__))
    root_direktorij = os.path.dirname(direktorij_skripte)
    

    putanja_skup = os.path.join(root_direktorij, "Testne_datoteke", "Test_prototip.xlsx")
    putanja_izlaz = os.path.join(root_direktorij, "Testne_datoteke", "rezultati.csv")

    # 1. Učitavanje podataka
    if not os.path.exists(putanja_skup):
        print(f"❌ GREŠKA: Datoteka {putanja_skup} nije pronađena!")
        return

    print("📊 Učitavam testni skup...")
    try:
        # Čitanje točno onog sheet-a koji postoji u datoteci
        testni_skup = pd.read_excel(putanja_skup, sheet_name='testni_skup')
        testni_skup.columns = testni_skup.columns.str.strip()
    except Exception as e:
        print(f"❌ GREŠKA pri učitavanju Excela: {e}")
        return

    # 2. Priprema za provjeru ID-eva (P2)
    # Prilagodi putanju do 'chroma_db' mape ako je negdje drugdje
    try:
        client = PersistentClient(path="./chroma_db") 
        collection = client.get_collection("tvoja_kolekcija") # PROVJERI NAZIV KOLEKCIJE
        postojeci_ids = set(collection.get()["ids"])
    except Exception as e:
        print(f"⚠️ Upozorenje: Nije moguće učitati bazu za provjeru ID-eva: {e}")
        postojeci_ids = set()

    print(f"🚀 Započinje evaluacija za {len(testni_skup)} pitanja...")
    rezultati = []
    
    # 3. Glavna petlja
    for idx, (index, r) in enumerate(testni_skup.iterrows()):
        pitanje = str(r["pitanje"]).strip()
        zlatni_id = str(r["zlatni_clanci"]).strip()
        
        # P2 Provjera
        if zlatni_id not in postojeci_ids:
            print(f"⚠️ UPOZORENJE: ID '{zlatni_id}' ne postoji u bazi!")

        # Dohvat (P1: BEZ SORTIRANJA!)
        t0 = time.perf_counter()
        results = search_chroma(pitanje)
        t1 = time.perf_counter()

        dohvaceni_ids_str = ""
        if 'ids' in results and results['ids'] and len(results['ids']) > 0:
            # P1: Ovdje je uklonjeno .sort()
            ocisceni_ids = [str(x).strip() for x in results['ids'][0] if x]
            dohvaceni_ids_str = ";".join(ocisceni_ids)

        # Generiranje odgovora
        try:
            tg_start = time.perf_counter()
            kontekst = "\n\n".join(results['documents'][0]) if 'documents' in results and results['documents'] else ""
            odgovor_iz_ai = generate_answer(pitanje, kontekst)
            t_generiranje = time.perf_counter() - tg_start
        except:
            odgovor_iz_ai = "Greška."
            t_generiranje = 0.0

        rezultati.append({
            "id": r["id"],
            "kategorija": r["kategorija"],
            "pitanje": pitanje,
            "zlatni_clanci": zlatni_id,
            "dohvaceni_ids": dohvaceni_ids_str,
            "odgovor": odgovor_iz_ai,
            "t_dohvat": t1 - t0,
            "t_generiranje": t_generiranje
        })

        print(f"✅ [{idx+1}/{len(testni_skup)}] Obrađeno: {pitanje[:30]}...")
        time.sleep(1) # Pauza za API

    # 4. Spremanje rezultata
    pd.DataFrame(rezultati).to_csv(putanja_izlaz, index=False, sep=";", encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
    print(f"\n✨ Gotovo! Rezultati u: {putanja_izlaz}")

if __name__ == "__main__":
    pokreni_evaluaciju()