# frontend/streamlit_app.py

import sys
import os
sys.path.append(os.path.abspath("."))  

import streamlit as st
from backend.core import CourtroomSimulator
from backend.utils.helpers import truncate_text



def display_legal_section(section):
    """Display a legal section with title and content."""
    st.markdown(f"**📌 [{section['doc_type']} Section {section['section_id']}]**")
    st.markdown(f"*{section['title']}*")
    with st.expander("View Full Section"):
        st.markdown(section["content"])
    st.markdown("---")


def main():
    st.set_page_config(page_title="⚖️ IPC Mock Courtroom", layout="wide")
    st.title("⚖️ Indian Legal Courtroom Simulator")
    st.markdown("""
    Describe a crime scenario, and watch how a simulated courtroom interprets the law using:
    - Indian Penal Code (IPC)
    - Code of Criminal Procedure (CrPC)
    - Indian Evidence Act
    
    All arguments are backed by retrieval-augmented legal reasoning.
    """)

    crime_description = st.text_area(
        "Describe the alleged crime:",
        placeholder="E.g., A man stabbed another during an argument, leading to death.",
        height=150
    )

    if st.button("Start Trial"):
        if not crime_description.strip():
            st.warning("Please enter a valid crime description.")
            return

        with st.spinner("🏛️ Running mock trial..."):
            simulator = CourtroomSimulator()
            trial_result = simulator.run_trial(crime_description)

        st.success("✅ Trial completed successfully.")

        # Prosecution Argument
        st.markdown("### 👨‍⚖️ Prosecution Argument")
        st.markdown(trial_result["prosecution"]["argument"])
        for sec in trial_result["prosecution"]["retrieved_sections"]:
            display_legal_section(sec)

        # Defense Argument
        st.markdown("### 🧑‍⚖️ Defense Argument")
        st.markdown(trial_result["defense"]["argument"])
        for sec in trial_result["defense"]["retrieved_sections"]:
            display_legal_section(sec)

        # Cross-Examiner Questions
        st.markdown("### 🔍 Cross-Examination")
        st.markdown(trial_result["cross_examination"]["questions"])

        # Judge Verdict
        st.markdown("### 🏛️ Final Judgment")
        st.markdown(trial_result["verdict"]["verdict"])
        for sec in trial_result["verdict"]["retrieved_sections"]:
            display_legal_section(sec)


if __name__ == "__main__":
    main()