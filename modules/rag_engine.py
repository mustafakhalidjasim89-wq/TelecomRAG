import json
import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def get_vector_store():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="telecom_findings",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Initialize collection if empty
    if collection.count() == 0:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        with open("telecom_findings.json", "r", encoding="utf8") as f:
            data = json.load(f)
            
        documents = data["findings"]
        ids = [str(i) for i in range(len(documents))]
        embeddings = model.encode(documents).tolist()
        
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings
        )
    return collection

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_findings(observation: str, distance_threshold: float = 0.45):
    collection = get_vector_store()
    model = get_embedding_model()
    
    query_embedding = model.encode([observation]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )
    
    matched_findings = []
    if results and "documents" in results and len(results["documents"]) > 0:
        docs = results["documents"][0]
        distances = results["distances"][0]
        
        for doc, dist in zip(docs, distances):
            # Lower cosine distance = higher similarity
            if dist <= distance_threshold:
                matched_findings.append(doc)
                
    return matched_findings
