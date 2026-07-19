import pandas as pd
import numpy as np
import time
import os

# Uvozimo potrebne objekte iz tvojih modula
# Pretpostavka: u tvojim skriptama su 'model' i 'collection' globalni objekti
from search_chroma import model, collection
from ai_response import generate_answer

# Postavke
MAPA = r'C:\Users\Toni\Desktop\Ai-aplikacija-za-pretra-ivanje-zakona\Testne_datoteke'
PUTANJA_TEST = os.path.join(MAPA, 'Test_prototip.xlsx')

def izmjeri_performanse():
    df = pd.read_excel(PUTANJA_TEST)
    mjerenja = []

    print(f"[INFO] Mjerim performanse za {len(df)} pitanja...")

    for i, row in df.head(60).iterrows():
        query = row['pitanje']
        
        # 1. MJERENJE UGRADNJE (CPU)
        start = time.perf_counter()
        query_embedding = model.encode([query], convert_to_numpy=True).tolist()
        t_ugradnja = time.perf_counter() - start
        
        # 2. MJERENJE PRETRAGE (ChromaDB)
        start = time.perf_counter()
        results = collection.query(query_embeddings=query_embedding, n_results=9)
        t_pretraga = time.perf_counter() - start
        
        # 3. MJERENJE GENERIRANJA (Groq API)
        context = "\n".join(results['documents'][0])
        start = time.perf_counter()
        _ = generate_answer(query, context)
        t_generiranje = time.perf_counter() - start
        
        mjerenja.append([t_ugradnja, t_pretraga, t_generiranje])
        time.sleep(30)

    # OBRADA PODATAKA
    df_v = pd.DataFrame(mjerenja, columns=['ugradnja', 'pretraga', 'generiranje'])
    df_v = df_v.iloc[1:] # Uklanjamo prvi zbog hladnog starta
    df_v['ukupno'] = df_v['ugradnja'] + df_v['pretraga'] + df_v['generiranje']
    
    def get_stats(col):
        return [col.mean(), col.std(), col.quantile(0.50), col.quantile(0.95)]

    tablica = pd.DataFrame({
        'Ugradnja upita (CPU)': get_stats(df_v['ugradnja']),
        'Pretraga ChromaDB': get_stats(df_v['pretraga']),
        'Generiranje (Groq API)': get_stats(df_v['generiranje']),
        'Ukupno (End-to-End)': get_stats(df_v['ukupno'])
    }, index=['Sredina (s)', 'St. devijacija (s)', 'p50 (s)', 'p95 (s)']).T
    
    print("\n--- TABLICA 5.6: ANALIZA PERFORMANSI SUSTAVA ---")
    print(tablica.to_string(formatters={
        'Sredina (s)': '{:.4f}s'.format, 
        'St. devijacija (s)': '{:.4f}s'.format, 
        'p50 (s)': '{:.4f}s'.format, 
        'p95 (s)': '{:.4f}s'.format
    }))

if __name__ == "__main__":
    izmjeri_performanse()