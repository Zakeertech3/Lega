# backend/agents/judge_agent.py

import os
from openai import OpenAI
from backend.retriever import LegalRetriever
from dotenv import load_dotenv


class JudgeAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1" 
        )
        self.model = "llama3-70b-8192"

    def render_verdict(self, prosecution_case, defense_case, cross_examination_questions):
        """
        Render a verdict based on all inputs.
        """
        print("[⚖️] Judge reviewing case details...")
        combined_input = self._combine_inputs(prosecution_case, defense_case, cross_examination_questions)

        # Retrieve relevant sections from all documents
        ipc_retriever = LegalRetriever(document_type="ipc")
        crpc_retriever = LegalRetriever(document_type="crpc")
        evidence_retriever = LegalRetriever(document_type="evidence_act")

        ipc_results = ipc_retriever.retrieve(combined_input, top_k=2)
        crpc_results = crpc_retriever.retrieve("criminal procedure", top_k=1)
        evidence_results = evidence_retriever.retrieve("burden of proof", top_k=1)

        retrieved_sections = ipc_results + crpc_results + evidence_results

        prompt = self._construct_prompt(prosecution_case, defense_case, cross_examination_questions, retrieved_sections)
        response = self._call_groq_api(prompt)

        return {
            "role": "Judge",
            "summary_input": combined_input[:500],
            "retrieved_sections": retrieved_sections,
            "verdict": response
        }

    def _combine_inputs(self, p, d, x):
        return f"{p['crime_description']} | {p['argument'][:200]} | {d['argument'][:200]} | {x['questions'][:200]}"

    def _construct_prompt(self, p_arg, d_arg, x_questions, sections):
        context = "\n\n".join([
            f"[{sec['doc_type']} Section {sec['section_id']}]: {sec['title']}\n{sec['content']}"
            for sec in sections
        ])

        prompt = f"""
You are the **Judge Agent** in a mock courtroom simulation.

Your task is to render a fair and legally sound verdict based on the evidence and arguments presented.

Crime Description:
"{p_arg['crime_description']}"

Prosecution Argument:
"{p_arg['argument'][:300]}..."

Defense Argument:
"{d_arg['argument'][:300]}..."

Cross-Examination Questions:
"{x_questions['questions'][:300]}..."

Relevant Legal Provisions:
{context}

Based on the above, issue a clear verdict:
- Was the act committed?
- Which IPC/CrPC/Evidence Act provisions apply?
- What is the appropriate judgment?

Cite specific sections and weigh both sides' arguments carefully.
"""

        return prompt

    def _call_groq_api(self, prompt):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a respected Judge issuing a legally sound verdict."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=600
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to get response from Groq API: {str(e)}"