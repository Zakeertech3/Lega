# backend/agents/defense_agent.py

import os
from openai import OpenAI
from backend.retriever import LegalRetriever
from dotenv import load_dotenv


class DefenseAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1" 
        )
        self.model = "llama3-70b-8192"

    def build_case(self, crime_description):
        """
        Build a defense case using relevant legal provisions.
        """
        print("[🔍] Defense Agent retrieving relevant sections...")
        ipc_retriever = LegalRetriever(document_type="ipc")
        evidence_retriever = LegalRetriever(document_type="evidence_act")

        ipc_results = ipc_retriever.retrieve(crime_description, top_k=2)
        evidence_results = evidence_retriever.retrieve("exceptions to admissibility", top_k=1)

        prompt = self._construct_prompt(crime_description, ipc_results + evidence_results)
        response = self._call_groq_api(prompt)

        return {
            "role": "Defense",
            "crime_description": crime_description,
            "retrieved_sections": ipc_results + evidence_results,
            "argument": response
        }

    def _construct_prompt(self, crime_description, sections):
        context = "\n\n".join([
            f"[{sec['doc_type']} Section {sec['section_id']}]: {sec['title']}\n{sec['content']}"
            for sec in sections
        ])

        prompt = f"""
You are the **Defense Agent** in a mock courtroom simulation. Your task is to construct a compelling defense based on the Indian Penal Code (IPC), Indian Evidence Act, and other applicable laws.

Given the alleged crime: "{crime_description}"

Here are relevant legal provisions:
{context}

Based on this information:
1. Identify possible defenses or mitigating circumstances
2. Challenge the applicability of certain charges
3. Present a concise but persuasive defense narrative

Ensure your argument clearly references section numbers and legal definitions.
"""

        return prompt

    def _call_groq_api(self, prompt):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a skilled Defense Lawyer assisting in a mock courtroom simulation."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=512
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to get response from Groq API: {str(e)}"