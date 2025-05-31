# backend/utils/helpers.py

import re


def clean_text(text):
    """Remove extra whitespace and normalize line breaks."""
    return re.sub(r'\s+', ' ', text).strip()


def truncate_text(text, max_length=200):
    """Truncate long text with ellipsis."""
    return (text[:max_length] + "...") if len(text) > max_length else text


def format_ipc_citation(section):
    """Format an IPC section as a citation string."""
    return f"IPC Section {section['section_id']}: {section['title']}"


def format_legal_citation(section):
    """Format any legal section with document type."""
    return f"{section['doc_type']} Section {section['section_id']}: {section['title']}"