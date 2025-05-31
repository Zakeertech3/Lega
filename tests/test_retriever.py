# tests/test_retriever.py

from backend.retriever import LegalRetriever

def test_retriever():
    retriever = LegalRetriever(document_type="ipc")
    results = retriever.retrieve("punishment for murder", top_k=1)

    assert len(results) == 1, "Should return one result"
    assert results[0]["section_id"] == "302", "Section 302 should match murder query"