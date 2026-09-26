import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st

# Locate telecom_findings.json relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "telecom_findings.json")

@st.cache_resource
def get_vector_store():
    client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "chroma_db"))
    collection = client.get_or_create_collection(
        name="telecom_findings",
        metadata={"hnsw:space": "cosine"}
    )
    
    if collection.count() == 0:
        if not os.path.exists(JSON_PATH):
            raise FileNotFoundError(f"Missing required file: {JSON_PATH}")

        model = get_embedding_model()
        with open(JSON_PATH, "r", encoding="utf8") as f:
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
            if dist <= distance_threshold:
                matched_findings.append(doc)
                
    return matched_findings
