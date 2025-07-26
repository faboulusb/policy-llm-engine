import os
import json
import faiss
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from pdfplumber import open as pdf_open
from docx import Document
from config import Config
from engine.db import save_chunks_to_db

EMBEDDING_MODEL = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)

def extract_text_from_pdf(file_path):
    with pdf_open(file_path) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    tokens = text.split()
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = " ".join(tokens[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def embed_chunks(chunks: List[str]) -> np.ndarray:
    return EMBEDDING_MODEL.encode(chunks, convert_to_numpy=True)

def process_file(file_path, doc_type):
    filename = os.path.basename(file_path)
    print(f"📄 Processing: {filename}")

    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        print("❌ Unsupported file type:", file_path)
        return [], []

    chunks = chunk_text(text, Config.CHUNK_SIZE, Config.OVERLAP_SIZE)
    embeddings = embed_chunks(chunks)

    metadata = [
        {"text": chunk, "source": filename, "doc_type": doc_type, "chunk_id": i}
        for i, chunk in enumerate(chunks)
    ]

    return embeddings, metadata

def build_faiss_index(all_embeddings: List[np.ndarray], save_path: str):
    print("🔧 Building FAISS index...")
    dimension = all_embeddings[0].shape[1]
    index = faiss.IndexFlatL2(dimension)
    all_vectors = np.vstack(all_embeddings)
    index.add(all_vectors)
    faiss.write_index(index, save_path)
    print(f"✅ FAISS index saved at: {save_path}")

def run_indexing():
    root_dirs = {
        "data/policies/": "policy",
        "data/contracts/": "contract",
        "data/emails/": "email"
    }

    all_embeddings = []
    all_metadata = []

    for folder, doc_type in root_dirs.items():
        for file in os.listdir(folder):
            if file.endswith(".pdf") or file.endswith(".docx"):
                path = os.path.join(folder, file)
                embeddings, metadata = process_file(path, doc_type)
                if embeddings:
                    all_embeddings.append(embeddings)
                    all_metadata.extend(metadata)

    if all_embeddings:
        build_faiss_index(all_embeddings, Config.FAISS_INDEX_PATH)
        save_chunks_to_db(all_metadata, np.vstack(all_embeddings))
        print("✅ All embeddings and metadata saved.")

if __name__ == "__main__":
    run_indexing()
