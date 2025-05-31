# tests/test_embedding_manager.py

from backend.embedding_manager import build_vectorstore

def test_build_vectorstore():
    json_path = "data/processed/ipc_sections.json"
    save_path = "tests/test_ipc_vectorstore.faiss"

    index = build_vectorstore(json_path, save_path=save_path)

    assert index.ntotal > 0, "FAISS index should contain vectors"

