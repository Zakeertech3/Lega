# backend/retriever.py

import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class LegalRetriever:
    def __init__(self, document_type="ipc"):
        """
        Initialize retriever for a specific legal document.
        
        Args:
            document_type (str): One of ['ipc', 'crpc', 'evidence_act']
        """
        self.document_type = document_type
        self.model = SentenceTransformer("bert-base-nli-mean-tokens")

        # Map doc type to FAISS index and sections
        self.index_path = self._get_index_path()
        self.sections_path = self._get_sections_path()

        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"Vector store not found at {self.index_path}")

        if not os.path.exists(self.sections_path):
            raise FileNotFoundError(f"Sections JSON not found at {self.sections_path}")

        # Load FAISS index
        self.index = faiss.read_index(self.index_path)

        # Load corresponding sections
        with open(self.sections_path, "r", encoding="utf-8") as f:
            self.sections = json.load(f)

    def _get_index_path(self):
        base_path = "data/vectorstore"
        return {
            "ipc": os.path.join(base_path, "ipc_vectorstore.faiss"),
            "crpc": os.path.join(base_path, "crpc_vectorstore.faiss"),
            "evidence_act": os.path.join(base_path, "evidence_act_vectorstore.faiss")
        }[self.document_type]

    def _get_sections_path(self):
        base_path = "data/processed"
        return {
            "ipc": os.path.join(base_path, "ipc_sections.json"),
            "crpc": os.path.join(base_path, "crpc_sections.json"),
            "evidence_act": os.path.join(base_path, "evidence_act_sections.json")
        }[self.document_type]

    def retrieve(self, query_text, top_k=3):
        """
        Retrieve the top-k most relevant sections for the given query.
        Returns list of dicts with section info + similarity score.
        """
        query_emb = self.model.encode([query_text])
        distances, indices = self.index.search(np.array(query_emb), top_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            distance = distances[0][i]

            try:
                section = self.sections[idx]
                results.append({
                    "doc_type": self.document_type.upper(),
                    "section_id": section["section_id"],
                    "title": section["title"],
                    "content": section["content"][:500] + "..." if len(section["content"]) > 500 else section["content"],
                    "score": float(distance)
                })
            except IndexError:
                continue  # Skip invalid indices

        return results