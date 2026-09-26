import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "telecom_findings.json")

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def get_vector_store():
    client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "chroma_db"))
    collection = client.get_or_create_collection(
        name="telecom_findings_master",
        metadata={"hnsw:space": "cosine"}
    )
    
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"Missing required file: {JSON_PATH}")

    with open(JSON_PATH, "r", encoding="utf8") as f:
        data = json.load(f)
        
    documents = data["findings"]
    
    # Reload database if new findings were added to telecom_findings.json
    if collection.count() != len(documents):
        # Reset collection
        client.delete_collection("telecom_findings_master")
        collection = client.create_collection(
            name="telecom_findings_master",
            metadata={"hnsw:space": "cosine"}
        )
        
        model = get_embedding_model()
        ids = [str(i) for i in range(len(documents))]
        embeddings = model.encode(documents).tolist()
        
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings
        )
        
    return collection

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
