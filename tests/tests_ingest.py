# tests/test_ingest.py

import os
import json
from backend.ingest import extract_sections

def test_extract_sections():
    pdf_path = "data/ipc_raw.pdf"
    output_file = "tests/test_ipc_sections.json"

    sections = extract_sections(pdf_path, output_file=output_file)

    assert len(sections) > 0, "Should extract at least one section"
    assert "section_id" in sections[0], "Each section should have an ID"
    assert "title" in sections[0], "Each section should have a title"
    assert "content" in sections[0], "Each section should have content"
    
# Run this after placing ipc_raw.pdf in the data/ folder. 
    