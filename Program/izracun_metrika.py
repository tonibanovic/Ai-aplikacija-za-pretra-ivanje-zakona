import pandas as pd
import numpy as np
import os

# --- POSTAVKE ---
MAPA = r'C:\Users\Toni\Desktop\Ai-aplikacija-za-pretra-ivanje-zakona\Testne_datoteke'
PUTANJA_TEST = os.path.join(MAPA, 'Test_prototip.xlsx')
PUTANJA_REZ = os.path.join(MAPA, 'rezultati.csv')

def pokreni_evaluaciju():
    print("[INFO] Učitavam i spajam podatke...")
    
    # 1. Učitavanje
    test_df = pd.read_excel(PUTANJA_TEST)
    rez_raw = pd.read_csv(PUTANJA_REZ, sep='\t', encoding='cp1250')

    # Spajanje SVIH kolona 'zlatni_clanci' (1., 2. i 3.) u jednu
    zlatni_cols = [c for c in test_df.columns if 'zlatni_clanci' in c]
    test_df['svi_zlatni'] = test_df[zlatni_cols].apply(lambda row: ';'.join(row.dropna().astype(str)), axis=1)

    # Spajanje svih stupaca 'dohvaceni_ids'
    cols = [c for c in rez_raw.columns if 'dohvaceni_ids' in c]
    rez_raw['dohvaceni_ids'] = rez_raw[cols].apply(lambda x: ';'.join(x.dropna().astype(str)), axis=1)
    
    # 2. SPAJANJE I FILTRIRANJE
    df = pd.merge(test_df[['id', 'kategorija', 'svi_zlatni']], rez_raw[['id', 'dohvaceni_ids']], on='id', how='inner')
    
    # Mapiranje kategorija
    mapiranje = {
        'izravni': 'Izravni činjenični upit',
        'sinteza': 'Složena semantička sinteza'
    }
    df['kategorija'] = df['kategorija'].str.strip().str.lower().map(mapiranje)
    df = df.dropna(subset=['kategorija']) # Izbacuje 'izvan'
    
    # Filtriranje T01-T45
    df['broj'] = df['id'].str.extract('(\d+)').astype(int)
    df = df[df['broj'] <= 40]

    # 3. IZRAČUN METRIKA
    sve_p, sve_r, sve_mrr, kat = [], [], [], []
    for _, row in df.iterrows():
        zlatni = set(c.strip() for c in str(row['svi_zlatni']).split(";") if c.strip())
        dohvaceni = [c.strip() for c in str(row['dohvaceni_ids']).split(";") if c.strip()][:9]
        
        pogodci = [c for c in dohvaceni if c in zlatni]
        
        sve_p.append(len(pogodci) / 9)
        sve_r.append(len(pogodci) / len(zlatni) if zlatni else 0)
        
        rr = 0.0
        for i, clanak in enumerate(dohvaceni, 1):
            if clanak in zlatni:
                rr = 1.0 / i
                break
        sve_mrr.append(rr)
        kat.append(row['kategorija'])

    # 4. KONAČNA TABLICA
    res_df = pd.DataFrame({'Kategorija': kat, 'Precision@9': sve_p, 'Recall@9': sve_r, 'MRR': sve_mrr})
    finalna = res_df.groupby('Kategorija').mean().reset_index()
    
    ukupno = pd.DataFrame({
        'Kategorija': ['Ukupno (prosjek)'],
        'Precision@9': [res_df['Precision@9'].mean()],
        'Recall@9': [res_df['Recall@9'].mean()],
        'MRR': [res_df['MRR'].mean()]
    })
    
    finalna = pd.concat([finalna, ukupno], ignore_index=True)
    
    print("\n--- REZULTATI EVALUACIJE ---")
    print(finalna.to_string(index=False, formatters={'Precision@9': '{:.4f}'.format, 'Recall@9': '{:.4f}'.format, 'MRR': '{:.4f}'.format}))

if __name__ == "__main__":
    pokreni_evaluaciju()
