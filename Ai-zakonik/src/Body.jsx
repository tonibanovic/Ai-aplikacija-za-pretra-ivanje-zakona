import { useState, useEffect } from "react";

function Izvor_kartica({izvor}){
    const [otvoreno, setOtvoreno] = useState(false);

    let prikazTeksta = izvor.tekst || "";
    
    if (izvor.clanak && prikazTeksta.startsWith(izvor.clanak)) {
        // Odrežemo onoliko znakova koliko je dugačak naziv članka + maknemo prazna mjesta na početku
        prikazTeksta = prikazTeksta.substring(izvor.clanak.length).trim();
        
        // Opcionalno: Ako nakon članka ostane crtica ili točka (npr. "- Tekst zakona"), makni i to
        if (prikazTeksta.startsWith("-") || prikazTeksta.startsWith(".")) {
            prikazTeksta = prikazTeksta.substring(1).trim();
        }
    }


    return(
        <div className ={`izvor-kartica ${otvoreno ? 'otvorena' : ''}`} onClick = {()=>setOtvoreno(!otvoreno)}>
            <div className="izvor-zaglavlje">
                <h4>{izvor.zakon}</h4>
                <h5 className="izvor-clanak-broj">{izvor.clanak}</h5>
            </div>

                {otvoreno &&(
                    <p className = "izvor-tekst-otvoren">
                        {prikazTeksta}
                    </p>

                )}
                <div className = "prikazi-vise-kontejner">
                    <span className = "gumb-tekst">
                        {otvoreno ? "Prikaži manje" : "Prikaži više"}
                    </span>
                </div>
        </div>

    );
}



function Body({ messages, setMessages, isMenuOpen, sessionId}) {
    // messages će sada držati objekte: { tekst: "...", sender: "user" ili "ai", izvori: [...] }
    //const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false); // Da znamo kada AI razmišlja
    const [povijestRazgovora, setPovijestRazgovora] = useState([]);


    const dohvatiPovijestIzBaze = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/povijest");
            if (response.ok) {
                const data = await response.json();
                setPovijestRazgovora(data); // data je lista objekata [{"session_id": "...", "prvo_pitanje": "..."}]
            }
        } catch (error) {
            console.error("Greška pri dohvaćanju povijesti:", error);
        }
    };

    useEffect(() => {
        dohvatiPovijestIzBaze();
    }, []);

    const obrisiSesijuIzBaze = async (sId, e) => {
    // e.stopPropagation() sprječava da klik na kantu ujedno aktivira i klik na cijelu stavku chata 
    e.stopPropagation(); 

    if (!window.confirm("Jeste li sigurni da želite obrisati ovaj razgovor iz povijesti?")) return;

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/povijest/${sId}`, {
            method: "DELETE",
        });

        if (response.ok) {
            // Ako je backend uspješno obrisao, makni tu stavku iz lokalnog React stanja
            setPovijestRazgovora(prev => prev.filter(stavka => stavka.session_id !== sId));
        } else {
            alert("Greška prilikom brisanja sesije s poslužitelja.");
        }
    } catch (error) {
        console.error("Greška pri brisanju:", error);
    }
};


    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const korisnickoPitanje = input.trim();
       
        setInput(""); // Odmah isprazni input polje

        const vecPostoji = povijestRazgovora.some(stavka => stavka.session_id === sessionId);
            if (!vecPostoji) {
                setPovijestRazgovora(prev => [...prev, { session_id: sessionId, prvo_pitanje: korisnickoPitanje }]);
            }

        // 1. Dodaj korisnikovo pitanje u chat prostor
        const novePoruke = [
            ...messages,
            { tekst: korisnickoPitanje, sender: "user", izvori: [] }
        ];
        setMessages(novePoruke);
        setLoading(true);

        try {
            // 2. Slanje POST zahtjeva na FastAPI backend
            const response = await fetch("http://127.0.0.1:8000/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    session_id: sessionId,
                    pitanje: korisnickoPitanje }),
            });

            if (!response.ok) {
                throw new Error("Greška u komunikaciji s poslužiteljem.");
            }

            // 3. Prihvaćanje JSON odgovora s backenda
            const data = await response.json();

            // 4. Dodaj AI odgovor i njegove izvore u chat prostor
            setMessages([
                ...novePoruke,
                { 
                    tekst: data.odgovor_ai, 
                    sender: "ai", 
                    izvori: data.izvori // Lista izvora: [{zakon, clanak, tekst}, ...]
                }
            ]);

           dohvatiPovijestIzBaze();

        } catch (error) {
            console.error("Greška:", error);
            // U slučaju greške, ispiši obavijest u chat
            setMessages([
                ...novePoruke,
                { tekst: "❌ Došlo je do greške pri dohvaćanju odgovora.", sender: "ai", izvori: [] }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (

        <div className={`body-container ${isMenuOpen ? 'menu-otvoren' : ''}`}> 

<aside className="sidebar-menu">
    <div className="sidebar-content">
        <h3 id="Povijest">Povijest chata</h3>
        {povijestRazgovora.length === 0 ? (
            <p>Nema starih razgovora...</p>
        ) : (
            <div className="povijest-lista">
                {povijestRazgovora.map((stavka, indeks) => (
                    <div key={indeks} className="povijest-stavka" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="povijest-tekst">
                            📌 {stavka.prvo_pitanje && stavka.prvo_pitanje.length > 20 
                                ? stavka.prvo_pitanje.substring(0, 20) + "..." 
                                : stavka.prvo_pitanje || "Prazan razgovor"}
                        </span>
                        <button 
                            onClick={(e) => obrisiSesijuIzBaze(stavka.session_id, e)}
                            className="gumb-obrisi"
                            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }}
                        >
                            🗑️
                        </button>
                    </div>
                ))}
            </div>
        )}
    </div>
</aside>

            <main className="body">

                {/* Chat prostor gdje se prikazuju poruke */}
                <div className="chat-space">
                    {messages.map((msg, i) => (
                        <div key={i} className={`message-container ${msg.sender}`}>
                            {/* Balončić s tekstom poruke (korisnik ili AI) */}
                            <div className={`chat-bubble ${msg.sender}`}>
                                {msg.tekst}
                            </div>

                            {/* Ako poruka ima izvore (i šalje je AI), nacrtaj kartice ispod */}
                            {msg.sender === "ai" && msg.izvori && msg.izvori.length > 0 && (
                                <div className="izvori-kontejner">
                                    <p className="izvori-naslov">Korišteni izvori:</p>
                                    <div className="kartice-mreza">
                                        {msg.izvori.map((izvor, idx) => (
                                            <Izvor_kartica key = {idx} izvor = {izvor}/>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && <div className="loading-tekst">AI razmišlja i pretražuje zakone...</div>}
                </div>

                {/* Tražilica / Unos teksta */}
                <div className="placeholder">
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                sendMessage();
                            }
                        }}
                        placeholder={loading ? "Pričekajte odgovor..." : "Upiši pitanje..."}
                        disabled={loading}
                    />

                    <img
                        id="send_button"
                        src="/send_sign.png"
                        onClick={sendMessage}
                        style={{ opacity: loading ? 0.5 : 1, cursor: loading ? "not-allowed" : "pointer" }}
                        alt="Pošalji"
                    />
                </div>

            </main>
    </div>
    );
}

export default Body;