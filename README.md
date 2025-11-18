Here’s a polished README.md for your Agentic AI Tutor project, fully compatible for GitHub and clearly reflecting both the architecture and your real-world migration/setup experience:*

# Agentic AI Tutor: Adaptive Learning with Local LLMs

## Overview

Agentic AI Tutor is a free, privacy-focused, adaptive learning system designed to help students prepare for competitive exams (JEE, SAT, GRE, etc.). It uses multi-agent AI orchestration, Retrieval-Augmented Generation (RAG), and local Large Language Models (LLMs) powered by [Ollama](https://ollama.ai/)—**no OpenAI API or cloud costs required**!

- **Personalized learning:** Adapts quizzes and study plans based on your progress
- **Full privacy:** All computations, documents, and student data stay on your machine
- **No API costs:** Runs 100% free after setup

***

## Features

- **Natural language chat:** Ask questions and get grounded, contextual explanations
- **Adaptive quizzes:** Automatic quiz generation, dynamically adjusts difficulty
- **Progress tracking:** Tracks your strengths, weaknesses, and learning gains
- **Runs locally:** Powered by Ollama and open-source LLMs (Mistral, Neural-Chat, etc.)
- **Intuitive UI:** Streamlit interface for easy interaction

***

## Screenshots

<img src="User_Interface_1.png" alt="My Image" width="…" height="…">
<img src="User_Interface_2.png" alt="My Image" width="…" height="…">
***

## Getting Started

### 1. Requirements

- Python 3.9+
- [Ollama](https://ollama.ai/) (for running local LLMs)
- 8GB+ RAM recommended
- pip (Python package manager)

### 2. Setup

#### 2.1. Clone the Repository

```bash
git clone https://github.com/rajatt12/agentic-ai-tutor.git
cd agentic-ai-tutor
```

#### 2.2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3. Install Ollama and Download a Model

- [Download Ollama](https://ollama.ai/download) and follow platform-specific install instructions.
- Download a local LLM (e.g., mistral or neural-chat):

```bash
ollama pull mistral
# OR for faster inference
ollama pull neural-chat
```

#### 2.4. Prepare Your Study Material (Optional)

Place any PDFs you want the tutor to "study" in the `data/study_materials/` directory.

Build the vector index:
```bash
python load_documents.py
```
(Omit this step if you want the tutor to answer from its own general knowledge.)

***

### 3. Running

#### 3.1. Start Ollama Server

In one terminal:
```bash
ollama serve
```
Keep this running.

#### 3.2. Start the Web App

In a new terminal:
```bash
python -m streamlit run app.py
```

***

## Troubleshooting & Notes

- If you see `"model 'gpt-3.5-turbo' not found"` errors, be sure you have updated all agent files to use `model="mistral"` or `model="neural-chat"`, not OpenAI models.
- If you see `"APIConnectionError"`, make sure `ollama serve` is running.
- If you get port errors (`address already in use`), ensure only one Ollama server is running and wait ~60 seconds for the port to free up if you just closed one.
- If using OpenAI API, keep your `.env` file with your key; for Ollama, `.env` can be blank or missing.

***

## Migration From OpenAI API

**This project originally used OpenAI’s GPT-3.5 Turbo API. When free credits ran out, we switched to Ollama:**

- **Before:** Cloud LLM, fast and expensive, required API key and internet, risk of exceeding free quota.
- **After:** Ollama runs entirely local (no API keys, no cost, full privacy), but responses are slower (30-60s on CPU).

**Tip:** Use `model="neural-chat"` for faster answers; outputs may be less detailed, but latency drops 3x.

***

## Project Structure

```
.
├── app.py                        # Streamlit UI
├── agents/
│   ├── planner_agent.py
│   ├── quiz_agent.py
│   └── retriever_agent.py
├── utils/
│   ├── embeddings.py
│   └── student_profiles.py
├── data/
│   └── study_materials/          # Place your PDFs here
├── database/
│   └── vector_store/             # ChromaDB storage
├── requirements.txt
└── README.md
```

***

## Tech Stack

| Component        | Technology         |
|------------------|-------------------|
| LLMs             | Ollama (Mistral, Neural-Chat, etc.) |
| Retrieval        | ChromaDB + Sentence Transformers |
| UI               | Streamlit         |
| Scripting        | Python 3.12       |
| Orchestration    | LangChain (optional), custom multi-agent system |


***


***

## References

- [Ollama Documentation](https://ollama.ai/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [ChromaDB](https://docs.trychroma.com/)
- [Sentence-Transformers](https://www.sbert.net/)

***

