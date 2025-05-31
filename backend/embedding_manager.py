# backend/embedding_manager.py

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


def build_vectorstore(json_path, model_name="bert-base-nli-mean-tokens", save_path=None):
    """
    Build a FAISS vector store from a JSON file of legal sections.
    
    Args:
        json_path (str): Path to input JSON file
        model_name (str): Name of the Sentence Transformer model
        save_path (str): Path to save FAISS index
    Returns:
        faiss.Index: Built FAISS index or None if skipped
    """
    # Load JSON data
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            sections = json.load(f)
    except Exception as e:
        print(f"[⚠️] Failed to load {json_path}: {e}")
        return None

    texts = [sec["content"] for sec in sections]

    if len(texts) == 0:
        print(f"[⚠️] No sections found in {json_path}. Skipping...")
        return None

    # Load embedding model
    print(f"[🧠] Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    # Generate embeddings
    print(f"[🧬] Generating embeddings for {len(texts)} sections...")
    try:
        embeddings = model.encode(texts, show_progress_bar=True)
    except Exception as e:
        print(f"[⚠️] Failed to generate embeddings: {e}")
        return None

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index if path provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        faiss.write_index(index, save_path)
        print(f"[💾] Vector store saved to: {save_path}")

    return index


if __name__ == "__main__":
    DATA_DIR = "data"
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
    VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstore")
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    # List of documents to embed
    docs = {
        "ipc_sections.json": "ipc_vectorstore.faiss",
        "crpc_sections.json": "crpc_vectorstore.faiss",
        "evidence_act_sections.json": "evidence_act_vectorstore.faiss"
    }

    MODEL_NAME = "bert-base-nli-mean-tokens"

    for json_file, faiss_file in docs.items():
        json_path = os.path.join(PROCESSED_DIR, json_file)
        faiss_path = os.path.join(VECTORSTORE_DIR, faiss_file)

        print(f"\n[📁] Processing: {json_file}")
        result = build_vectorstore(json_path, model_name=MODEL_NAME, save_path=faiss_path)

        if result is None:
            print(f"[⚠️] Skipped {json_file}")
        else:
            print(f"[✓] Completed {json_file}")

    print("\n[✅] All done!")