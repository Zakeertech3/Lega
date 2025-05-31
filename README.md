# ⚖️ Indian Legal Courtroom Simulator

An AI-powered application that simulates realistic courtroom proceedings using Indian legal codes. Built with RAG (Retrieval-Augmented Generation) to ensure accurate legal citations and multi-agent architecture for dynamic trial simulation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

## 🎯 What Problem Does This Solve?

Legal education often struggles with a fundamental gap: how do you practice courtroom dynamics without access to actual trials? Law students memorize sections of the Indian Penal Code, but rarely see how different legal provisions interact in real arguments between prosecution and defense.

Traditional AI chatbots fail catastrophically in legal contexts because they hallucinate non-existent legal citations. Our solution uses **Retrieval-Augmented Generation (RAG)** to ground every legal argument in actual statutory provisions from the IPC, CrPC, and Indian Evidence Act.

**Why RAG?** Instead of the AI making up legal citations, it first searches through actual legal documents to find relevant sections, then uses those real provisions to build arguments. This means every legal reference in the simulation is authentic and verifiable.

## ✨ Features

- **🏛️ Complete Mock Trials**: Full courtroom simulation from prosecution arguments to final verdict
- **📚 Real Legal Citations**: Every argument backed by actual IPC/CrPC/Evidence Act sections  
- **🤖 Multi-Agent System**: Specialized AI agents for prosecution, defense, cross-examination, and judgment
- **🔍 Smart Legal Search**: FAISS-powered semantic search across Indian legal codes
- **📱 Interactive Interface**: Clean Streamlit UI with progress tracking and downloadable transcripts
- **🎓 Educational Focus**: Designed for law students and legal education

## 🚀 Quick Demo : https://drive.google.com/file/d/1KNz88N2nn6JULJ5PrRIwSQTxxWuC2Ejg/view?usp=sharing

Here's what a typical trial simulation looks like:

1. **Input**: "Rajesh broke into a house and stole jewelry worth ₹2,50,000, injuring the homeowner when caught"
2. **Prosecution**: Cites IPC Section 380 (theft in dwelling), Section 323 (voluntary hurt)
3. **Defense**: Argues Section 85 (intoxication), challenges evidence under Evidence Act  
4. **Cross-Examination**: Questions evidence quality and intent
5. **Verdict**: Judge weighs arguments with detailed legal reasoning

## 🏗️ How It Works (RAG Architecture)

### System Architecture Overview

```
┌──────────────────────────┐
│    IPC PDF (raw)        │
└────────────┬─────────────┘
             │
  [Split by section/paragraph]
             │
             ▼
┌──────────────────────────┐
│   Chunks & Metadata      │  ──► (Embed each chunk)  
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐       ┌──────────────────────────┐
│   Vector Database         │◄─────┤   Embedding Model       │
│  (IPC embeddings stored)  │─────►│ (e.g., Legal-BERT)      │
└────────────┬─────────────┘       └──────────────────────────┘
             │
             ▼
        [RAG Retriever]
             │        \
             │         \ (serves as a "tool" to all agents)
             │
             ▼
┌───────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│  Prosecution      │       │   Defense           │       │  Cross-Exam         │
│  Argument Agent   │       │  Argument Agent     │       │  / Rebuttal Agent   │
└─────────┬─────────┘       └────────┬────────────┘       └─────────┬───────────┘
          │  (calls Retriever)        │  (calls Retriever)         │ (calls Retriever)
          │                          │                            │
          ▼                          ▼                            ▼
  "Prosecution Argument"      "Defense Argument"         "Cross-Exam Questions"
          └────────────────────────────────────────────────────────────┐
                                                                      │
                                                                      ▼
                                                    ┌──────────────────────────┐
                                                    │  Judge / Adjudicator     │
                                                    │       Agent              │
                                                    └─────────┬───────────────┘
                                                              │
                                                              ▼
                                                     "Final Written Judgment"
```

### The Data Pipeline

The system processes three core legal documents:
- **Indian Penal Code (IPC)**: Criminal offenses and punishments
- **Code of Criminal Procedure (CrPC)**: Court procedures and processes
- **Indian Evidence Act**: Rules for evidence admissibility

**Processing Steps:**
1. **PDF Ingestion**: Extract raw text from legal documents using `pdfplumber`
2. **Section Parsing**: Split documents by legal sections using regex patterns to identify section boundaries
3. **Metadata Extraction**: Structure sections with IDs, titles, and content into JSON format
4. **Vector Embedding**: Convert text to semantic embeddings using Sentence Transformers (`bert-base-nli-mean-tokens`)
5. **Index Creation**: Build FAISS indices for fast similarity search and store them locally

### The Retrieval System

- **Vector Database**: FAISS for high-performance similarity search with L2 distance metrics
- **Embeddings**: Sentence Transformers (`bert-base-nli-mean-tokens`) for semantic understanding of legal text
- **Shared Retriever**: Single `LegalRetriever` class serves all agents as a tool for consistent legal document access
- **Search Strategy**: Each AI agent retrieves relevant legal sections based on the crime scenario using configurable top-k parameters
- **Multi-Document Support**: Agents can search across IPC, CrPC, and Evidence Act simultaneously for comprehensive legal coverage

### The Generation System

Four specialized AI agents powered by Groq's LLaMA 3 70B:

- **Prosecution Agent**: Builds cases citing relevant criminal law sections, focuses on offense elements and procedural requirements
- **Defense Agent**: Finds legal defenses and mitigating circumstances using IPC exceptions and Evidence Act provisions
- **Cross-Examiner Agent**: Identifies weaknesses and asks probing questions that expose logical inconsistencies between arguments
- **Judge Agent**: Synthesizes arguments and renders verdict with comprehensive legal reasoning, weighing burden of proof

**Agent Configuration:**
```python
agent_temperatures = {
    "prosecution": 0.3,     # Factual, structured arguments
    "defense": 0.3,         # Thorough, defensive reasoning  
    "cross_examiner": 0.5,  # Creative, probing questions
    "judge": 0.2            # Balanced, careful deliberation
}
```

Each agent uses specialized prompts and retrieval strategies tailored to their courtroom role, ensuring realistic and legally sound arguments throughout the trial simulation.

## 🛠️ Tech Stack

**Core RAG Components:**
- `sentence-transformers` - For semantic embeddings of legal text
- `faiss-cpu` - Vector similarity search and indexing
- `pdfplumber` - Extract text from legal PDF documents

**LLM Integration:**
- `groq` - High-performance LLM inference (LLaMA 3 70B via `llama3-70b-8192` model)
- `openai` - OpenAI-compatible API client for Groq integration and easy model switching

**Frontend & Utils:**
- `streamlit` - Interactive web interface
- `python-dotenv` - Environment management
- `PyYAML` - Configuration handling

### Why These Choices?

**FAISS over cloud vector DBs**: We wanted local deployment for sensitive legal data and offline classroom use.

**Sentence Transformers**: Better for domain-specific legal text than general-purpose embeddings, plus works offline.

**Groq LLaMA 3 70B**: Incredibly fast inference (perfect for real-time courtroom simulation) with free tier access for educational use. While GPT-4 or Claude 3 would be ideal for production, Groq gives us 70B parameter quality at lightning speed for educational purposes.

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Zakeetech3/lega.git
cd ipc-courtroom-simulator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Get a Groq API key**
- Sign up at [console.groq.com](https://console.groq.com)
- Copy your API key (it's free!)

4. **Prepare legal documents**
```bash
# Place your legal PDF files in data/ directory
# Then run the ingestion pipeline
python backend/ingest.py
python backend/embedding_manager.py
```

5. **Launch the application**
```bash
streamlit run frontend/streamlit_app.py
```

## 📁 Project Structure

```ipc_courtroom_simulator/
│
├── data/
│   ├── ipc_raw.pdf
│   ├── crpc_raw.pdf
│   ├── evidence_act_raw.pdf
│   │
│   ├── processed/
│   │   ├── ipc_sections.json
│   │   ├── crpc_sections.json
│   │   └── evidence_act_sections.json
│   │
│   └── vectorstore/
│       ├── ipc_vectorstore.faiss
│       ├── crpc_vectorstore.faiss
│       └── evidence_act_vectorstore.faiss
│
├── backend/
│   ├── agents/
│   │   ├── prosecution_agent.py
│   │   ├── defense_agent.py
│   │   ├── cross_examiner_agent.py
│   │   └── judge_agent.py
│   │
│   ├── core.py               # CourtroomSimulator class
│   ├── ingest.py             # PDF parsing & section extraction
│   ├── embedding_manager.py  # FAISS index creation
│   ├── retriever.py          # LegalRetriever class
│   │
│   └── utils/
│       ├── logger.py
│       ├── helpers.py
│       ├── prompt_templates.py
│       └── config_loader.py
│
├── frontend/
│   └── streamlit_app.py      # Streamlit UI
│
├── config/
│   └── config.yaml            # Configuration settings
│
├── .env                       # Stores Groq API key
├── requirements.txt           # Python dependencies
│
└── tests/                     # ✅ New: Folder for all test files
    ├── test_ingest.py         # Tests for PDF ingestion
    ├── test_embedding_manager.py  # Tests for FAISS embedding generation
    ├── test_retriever.py      # Tests for legal retrieval logic
    ├── test_agents.py          # Tests for Prosecution, Defense, etc.
    ├── test_core.py           # Tests for courtroom flow
```

## 🎯 Use Cases

- **Law Schools**: Interactive legal education and mock trial practice
- **Legal Training**: Professional development for young lawyers
- **Research**: Understanding patterns in legal argumentation
- **Public Education**: Making legal concepts accessible to citizens

## 🔬 Technical Details

### Model Configuration

This project uses Groq API with the `llama3-70b-8192` model. Each agent uses different parameters optimized for their role:

```python
prosecution: temperature=0.3  # Factual, structured arguments
defense: temperature=0.3      # Thorough, defensive reasoning
cross_examiner: temperature=0.5  # Creative, probing questions
judge: temperature=0.2        # Balanced, careful deliberation
```

**Note**: This project uses Groq API with models like `llama3-70b-8192`. You can also integrate local LLMs (e.g., via Ollama or LM Studio) by modifying the agent files to use different API endpoints or local model servers.

### Retrieval Strategy
```python
# Different agents search different legal domains
prosecution_retrieval = [IPC_offenses, CrPC_procedures]
defense_retrieval = [IPC_defenses, Evidence_Act_exceptions] 
judge_retrieval = [IPC_sections, CrPC_procedures, Evidence_burden_of_proof]
```

## 🧪 Testing

Run the test suite to verify everything works:
```bash
python -m pytest tests/
```

Tests cover:
- PDF ingestion and section extraction
- Vector store creation and retrieval
- Individual agent responses
- Full trial simulation pipeline

## ⚠️ Important Notes

**Educational Use Only**: This is a learning tool, not a replacement for professional legal advice. The AI agents provide educational simulations based on statutory law but cannot account for case law, recent amendments, or jurisdiction-specific variations.

**Current Scope**: Limited to Indian criminal law (IPC, CrPC, Evidence Act). Civil law, constitutional law, and other legal domains are not included.

## 🤝 Contributing

Contributors are welcome! Here are ways to help:
- Add support for more legal documents
- Improve agent reasoning capabilities
- Enhance the user interface
- Add more comprehensive tests
- Optimize retrieval performance

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).


---

**Built for legal education and AI research** • [⭐ Star this repo](https://github.com/yourusername/ipc-courtroom-simulator) • [🐛 Report issues](https://github.com/yourusername/ipc-courtroom-simulator/issues)
