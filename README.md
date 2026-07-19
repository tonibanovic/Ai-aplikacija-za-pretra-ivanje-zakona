AI SUSTAV ZA SEMANTIČKO PRETRAŽIVANJE ZAKONSKIH TEKSTOVA

Opis: RAG sustav za pretraživanje pravnih dokumenata temeljen na ChromaDB i Groq API-ju"
Tehnologije: React (Frontend), FastAPI (Backend), ChromaDB (Vector DB), Llama 3.1 (Groq API).

Upute za pokretanje: 

Napomena: Preduvjet je imati instaliran Python 3.11.2 i Node.js v24.17

1. Povlačenje s github-a:
		
		git init
		git remote add origin https://github.com/tonibanovic/Ai-aplikacija-za-pretra-ivanje-zakona.git
		git pull origin master
		

2. Priprema API ključa (Obavezno): Kako bi aplikacija mogla komunicirati s AI modelom, potrebno je unijeti vaš Groq API ključ. Otvorite datoteku Program/ai_response.py.
Na 3. liniji koda pronađite varijablu za ključ i unutar navodnika zalijepite svoj generirani GROQ_API_KEY. Napomena: Iz sigurnosnih razloga, ova datoteka nije uključena u verzijsku kontrolu s važećim ključem.

3.  Pokretanje putem Dockera:
    docker-compose up --build

4. Ručno pokretanje (ako ne koristite Docker):
    Backend:
	cd Program
       	py -m pip install -r requirements.txt
   		py -m chroma_db.py
        py main.py
    Frontend:
	New Terminal
        cd Ai-zakonik
   		Prekopirati naredbu: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
        npm install
        npm run dev




