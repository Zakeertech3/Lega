# backend/agents/prosecution_agent.py

import os
from openai import OpenAI
from backend.retriever import LegalRetriever
from dotenv import load_dotenv


class ProsecutionAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1" 
        )
        self.model = "llama3-70b-8192"

    def build_case(self, crime_description):
        """
        Build a prosecution case using relevant legal provisions.
        """
        print("[🔍] Prosecution Agent retrieving relevant sections...")
        ipc_retriever = LegalRetriever(document_type="ipc")
        crpc_retriever = LegalRetriever(document_type="crpc")

        ipc_results = ipc_retriever.retrieve(crime_description, top_k=2)
        crpc_results = crpc_retriever.retrieve("arrest and procedure", top_k=1)

        prompt = self._construct_prompt(crime_description, ipc_results + crpc_results)
        response = self._call_groq_api(prompt)

        return {
            "role": "Prosecution",
            "crime_description": crime_description,
            "retrieved_sections": ipc_results + crpc_results,
            "argument": response
        }

    def _construct_prompt(self, crime_description, sections):
        context = "\n\n".join([
            f"[{sec['doc_type']} Section {sec['section_id']}]: {sec['title']}\n{sec['content']}"
            for sec in sections
        ])

        prompt = f"""
You are the **Prosecution Agent** in a mock courtroom simulation. Your task is to construct a compelling legal argument based on the Indian Penal Code (IPC), Code of Criminal Procedure (CrPC), and other applicable laws.

Given the alleged crime: "{crime_description}"

Here are relevant legal provisions:
{context}

Based on this information:
1. Identify the most applicable offense(s)
2. Cite supporting IPC, CrPC, or procedural provisions
3. Present a concise but persuasive prosecution narrative

Ensure your argument clearly references section numbers and legal definitions.
"""

        return prompt

    def _call_groq_api(self, prompt):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a skilled Prosecution Lawyer assisting in a mock courtroom simulation."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=512
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to get response from Groq API: {str(e)}"