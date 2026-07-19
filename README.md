AI SUSTAV ZA SEMANTIČKO PRETRAŽIVANJE ZAKONSKIH TEKSTOVA

Opis: RAG sustav za pretraživanje pravnih dokumenata temeljen na ChromaDB i Groq API-ju"

Upute za pokretanje:
    1. Priprema API ključa (Obavezno):
      Kako bi aplikacija mogla komunicirati s AI modelom, potrebno je unijeti vaš Groq API ključ.
      Otvorite datoteku Program/ai_response.py.  
      Na 3. liniji koda pronađite varijablu za ključ i unutar navodnika zalijepite svoj generirani GROQ_API_KEY.
      Napomena: Iz sigurnosnih razloga, ova datoteka nije uključena u verzijsku kontrolu s važećim ključem.

    2. Pokretanje putem Dockera:
        docker-compose up --build

    3. Ručno pokretanje (ako ne koristite Docker):
        Backend:
            pip install -r requirements.txt
            python main.py
        Frontend:
            cd Ai-zakonik
            npm install
            npm run dev
