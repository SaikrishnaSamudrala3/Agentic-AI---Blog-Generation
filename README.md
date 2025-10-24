# Agentic-AI — Blog Generation

A lightweight, agent-based AI system for automating blog creation — from topic research to final polish — using orchestrated AI workflows.

---

## Features

- **Multi-Agent Workflow:** Automates the blog generation pipeline (research → draft → refine).  
- **Modular Architecture:** Easily extend with new agents, tools, or APIs.  
- **Customizable Workflow:** Define agent flows in `langgraph.json`.  
- **Flexible Input:** Accepts JSON or UI inputs for custom blog topics.  
- **Simple Setup:** Minimal dependencies; runs locally or via a web UI.

---

## Prerequisites

- Python 3.10 or higher  
- LLM API key (e.g., OpenAI or compatible)  
- (Optional) Web search or image generation API keys  
- Git (for cloning the repository)

---

## Installation and Running

```bash
# Clone the repository
git clone https://github.com/SaikrishnaSamudrala3/Agentic-AI---Blog-Generation.git
cd Agentic-AI---Blog-Generation

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate    # (Windows: .venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Run the main pipeline
python main.py

# Run the web app
python app.py




