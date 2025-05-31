# backend/ingest.py

import re
import json
import pdfplumber
import os


def extract_sections(pdf_path, section_pattern=r"(?i)(?=\bsection\s+\d+)", output_file=None):
    """
    Generic function to extract sections from any legal PDF.
    Args:
        pdf_path (str): Path to input PDF
        section_pattern (str): Regex pattern to split sections
        output_file (str): Optional path to save JSON output
    Returns:
        list: List of extracted sections
    """
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"[❌] Error reading PDF: {e}")
        return []

    raw_sections = re.split(section_pattern, full_text)
    if not raw_sections[0].strip():
        raw_sections.pop(0)

    sections = []
    for sec in raw_sections:
        sec_id_match = re.search(r"section\s+(\d+)", sec[:150], re.IGNORECASE)
        if not sec_id_match:
            continue

        sec_id = sec_id_match.group(1)
        title_end_match = re.search(r"[:\.]\s*\n?", sec)
        title_end_idx = title_end_match.end() if title_end_match else sec.find("\n")
        title = sec[:title_end_idx].strip()
        content = sec.strip()

        sections.append({
            "section_id": sec_id,
            "title": title,
            "content": content
        })

    # Save to JSON if output file is provided
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4)

    print(f"[✓] Extracted {len(sections)} sections from {os.path.basename(pdf_path)}")
    return sections


if __name__ == "__main__":
    import os

    DATA_DIR = "data"
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Define all PDFs and their output paths
    docs = {
        "ipc_raw.pdf": os.path.join(PROCESSED_DIR, "ipc_sections.json"),
        "crpc_raw.pdf": os.path.join(PROCESSED_DIR, "crpc_sections.json"),
        "evidence_act_raw.pdf": os.path.join(PROCESSED_DIR, "evidence_act_sections.json")
    }

    for pdf_file, json_file in docs.items():
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        print(f"\n[+] Processing {pdf_file}...")
        extract_sections(pdf_path, output_file=json_file)