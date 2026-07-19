import chromadb
from sentence_transformers import SentenceTransformer
import os  

# model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


# Saznajemo točnu mapu gdje se nalazi ova skripta (mapa Program)
skripta_direktorij = os.path.dirname(os.path.abspath(__file__))
# Spajamo to s nazivom mape
chroma_putanja = os.path.join(skripta_direktorij, "chroma_storage")

# Chroma se sada spaja na fiksnu putanju
client = chromadb.PersistentClient(path=chroma_putanja)
# ----------------------------

collection = client.get_collection(name="zakoni")


def search_chroma(query):


    # embedding pitanja
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).tolist()


 
    # pretraga
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=9
    )

    return results