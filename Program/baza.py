import sqlite3 

DATABASE_FILE = "baza.db"


def inicijaliziranje_baze():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS povijest(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_id TEXT NOT NULL,
                       prvo_pitanje TEXT NOT NULL,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
    """)
    
    
    conn.commit()
    conn.close()
    
def spremi_prvo_pitanje(session_id: str, pitanje: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO povijest(session_id, prvo_pitanje) VALUES (?, ?)",
        (session_id, pitanje)
    )
    
    conn.commit()
    conn.close()
    
    
def sesija_postoji(session_id: str) -> bool:
    """Provjerava postoji li sesija već u bazi podataka."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM povijest WHERE session_id = ?", (session_id,))
    rezultat = cursor.fetchone()
    
    conn.close()
    return rezultat is not None

def dohvati_sve_sesije():
    conn = sqlite3.connect("baza.db")
    cursor = conn.cursor()
    # ASC slaže od najstarijeg prema najnovijem (novi idu na dno)
    cursor.execute("SELECT session_id, prvo_pitanje FROM povijest ORDER BY id ASC")
    rezultati = cursor.fetchall()
    conn.close()
    return [{"session_id": r[0], "prvo_pitanje": r[1]} for r in rezultati]


def obrisi_sesiju(session_id: str):
    """Briše sesiju iz baze podataka prema session_id-u."""
    conn = sqlite3.connect("baza.db")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM povijest WHERE session_id = ?", (session_id,))
    
    conn.commit()
    conn.close()