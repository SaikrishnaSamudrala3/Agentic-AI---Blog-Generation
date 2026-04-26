# Agentic AI Blog Generation

A portfolio-ready FastAPI, LangGraph, and Next.js project that generates Markdown blog posts through a role-based multi-agent workflow. The system retrieves current web context, runs independent research agents in parallel, then uses Outline, Writer, Editor, and SEO agents to create polished multilingual articles and store them in SQLite.

## Features

- Web Retrieval Agent using Tavily for current source grounding.
- Parallel Concept, Use Case, and Risk Research Agents for compact topic notes.
- Outline Agent for article structure.
- Writer Agent for direct-language drafting.
- Editor Agent for clarity, flow, and readability.
- SEO Agent for meta title, meta description, keywords, slug, and reading time.
- FastAPI backend with validated request and response models.
- SQLite persistence for generated blogs.
- Next.js UI for generation, preview, SEO review, sources, and history.
- CLI entry point for local generation.
- Docker Compose setup for API and UI.
- GitHub Actions CI for tests.
- Mocked tests that validate graph behavior without real LLM calls.

## Architecture

```text
Next.js UI / CLI / API Client
          |
          v
       FastAPI
          |
          v
   LangGraph StateGraph
          |
          +--> web_retrieval_agent
          |
          +--> concept_research_agent ┐
          +--> use_case_research_agent ├─ parallel research
          +--> risk_research_agent    ┘
          |
          +--> outline_agent
          +--> writer_agent
          +--> editor_agent
          +--> seo_agent
          |
          v
       SQLite
```

## Tech Stack

- Python 3.13
- FastAPI
- Next.js
- LangGraph
- LangChain
- OpenAI API by default, with optional Groq fallback
- SQLite
- Pydantic
- Pytest
- Docker
- GitHub Actions

## Project Structure

```text
.
├── app.py                      # FastAPI application
├── frontend                    # Next.js frontend
├── streamlit_app.py            # Legacy Streamlit frontend
├── main.py                     # CLI entry point
├── Dockerfile
├── docker-compose.yml
├── langgraph.json              # LangGraph Studio config
├── src
│   ├── graphs                  # LangGraph workflow builders
│   ├── llms                    # LLM provider wrapper
│   ├── nodes                   # Graph node implementations
│   ├── states                  # Shared graph state and schemas
│   └── storage                 # SQLite repository
└── tests                       # Mocked workflow and persistence tests
```

## Setup

```bash
git clone https://github.com/SaikrishnaSamudrala3/Agentic-AI---Blog-Generation.git
cd Agentic-AI---Blog-Generation

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Update `.env`:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key_here
DATABASE_URL=sqlite:///data/blogs.db
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

To use Groq instead, set:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

## Run The API

```bash
python app.py
```

Health check:

```bash
curl http://localhost:8000/health
```

List supported languages:

```bash
curl http://localhost:8000/languages
```

Generate and store a blog:

```bash
curl -X POST http://localhost:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Agentic AI in software engineering",
    "language": "french",
    "tone": "professional",
    "audience": "software engineers",
    "length": "medium"
  }'
```

Supported languages are currently English, French, Hindi, Spanish, German, and Telugu. The Writer and Editor agents write directly in the selected language.

List stored blogs:

```bash
curl http://localhost:8000/blogs
```

Fetch one blog:

```bash
curl http://localhost:8000/blogs/1
```

## Run The Next.js UI

Start the API first, then run:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Run From CLI

```bash
python main.py "Agentic AI in software engineering"
python main.py "Agentic AI in software engineering" --language french --audience "software engineers" --tone technical --length long
```

## Run With Docker

```bash
docker compose up --build
```

API: `http://localhost:8000`

UI: `http://localhost:3000`

## Run Tests

```bash
pytest
```

## Resume Highlights

- Built a role-based multi-agent content generation workflow with LangGraph.
- Added web retrieval for current-event grounding and source URLs.
- Designed parallel research agents plus Outline, Writer, Editor, and SEO agents with clear graph responsibilities.
- Exposed the workflow through a validated FastAPI service and a Next.js product UI.
- Added SQLite persistence with retrieval and delete APIs.
- Containerized the API and UI with Docker Compose.
- Added CI and mocked tests to validate behavior without external LLM calls.

## Next Improvements

- Add a RAG pipeline with document loading, embeddings, vector storage, and retrieval.
- Add an editor node for grammar, clarity, and tone refinement.
- Add async background jobs for long-running generations.
- Add authentication for stored blog history.
- Add more languages in `src/config/languages.py`.
- Deploy the API to Render/Railway and the Next.js UI to Vercel.
