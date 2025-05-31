# backend/agents/cross_examiner_agent.py

import os
from openai import OpenAI
from backend.retriever import LegalRetriever
from dotenv import load_dotenv


class CrossExaminerAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1" 
        )
        self.model = "llama3-70b-8192"

    def examine(self, prosecution_argument, defense_argument):
        """
        Analyze both sides' arguments and generate targeted questions.
        """
        print("[🔍] Cross-Examiner analyzing arguments...")
        combined_input = self._combine_arguments(prosecution_argument, defense_argument)

        # Retrieve relevant sections from all documents
        ipc_retriever = LegalRetriever(document_type="ipc")
        evidence_retriever = LegalRetriever(document_type="evidence_act")

        ipc_results = ipc_retriever.retrieve(combined_input, top_k=1)
        evidence_results = evidence_retriever.retrieve(combined_input, top_k=1)

        retrieved_sections = ipc_results + evidence_results

        prompt = self._construct_prompt(prosecution_argument, defense_argument, retrieved_sections)
        response = self._call_groq_api(prompt)

        return {
            "role": "Cross-Examiner",
            "prosecution_summary": prosecution_argument["argument"][:300],
            "defense_summary": defense_argument["argument"][:300],
            "retrieved_sections": retrieved_sections,
            "questions": response
        }

    def _combine_arguments(self, p, d):
        return f"Prosecution: {p['crime_description']} - {p['argument'][:200]} | Defense: {d['argument'][:200]}"

    def _construct_prompt(self, p_arg, d_arg, sections):
        context = "\n\n".join([
            f"[{sec['doc_type']} Section {sec['section_id']}]: {sec['title']}\n{sec['content']}"
            for sec in sections
        ])

        prompt = f"""
You are the **Cross-Examiner Agent** in a mock courtroom simulation.

Your task is to critically analyze the arguments from both sides and generate targeted questions that challenge inconsistencies, assumptions, or legal misinterpretations.

Prosecution Argument Summary:
"{p_arg['argument'][:300]}..."

Defense Argument Summary:
"{d_arg['argument'][:300]}..."

Relevant Legal Provisions:
{context}

Generate 3–4 focused questions that test the strength of each side's case.
Focus on areas where the facts or law may be unclear, disputed, or incomplete.
"""

        return prompt

    def _call_groq_api(self, prompt):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an experienced Cross-Examiner in a legal trial."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=400
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to get response from Groq API: {str(e)}"