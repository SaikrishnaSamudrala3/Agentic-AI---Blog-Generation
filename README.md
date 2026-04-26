# Agentic AI Blog Generation

A portfolio-ready FastAPI, LangGraph, and Streamlit project that generates Markdown blog posts through a fast agentic workflow. The system creates planning notes, writes the final article directly in the selected language, generates SEO metadata, and stores the result in SQLite.

## Features

- Planning node for compact research notes and outline.
- Content generation directly in the selected language.
- SEO node for meta title, meta description, keywords, slug, and reading time.
- FastAPI backend with validated request and response models.
- SQLite persistence for generated blogs.
- Streamlit UI for generation, preview, SEO review, and history.
- CLI entry point for local generation.
- Docker Compose setup for API and UI.
- GitHub Actions CI for tests.
- Mocked tests that validate graph behavior without real LLM calls.

## Architecture

```text
Streamlit UI / CLI / API Client
          |
          v
       FastAPI
          |
          v
   LangGraph StateGraph
          |
          +--> planning
          +--> content_generation
          +--> seo_generation
          |
          v
       SQLite
```

## Tech Stack

- Python 3.13
- FastAPI
- Streamlit
- LangGraph
- LangChain
- Groq LLM API
- SQLite
- Pydantic
- Pytest
- Docker
- GitHub Actions

## Project Structure

```text
.
├── app.py                      # FastAPI application
├── streamlit_app.py            # Streamlit frontend
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
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
DATABASE_URL=sqlite:///data/blogs.db
API_BASE_URL=http://localhost:8000
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

Supported languages are currently English, French, Hindi, Spanish, German, and Telugu. English is the default and skips the translation node.

List stored blogs:

```bash
curl http://localhost:8000/blogs
```

Fetch one blog:

```bash
curl http://localhost:8000/blogs/1
```

## Run The UI

Start the API first, then run:

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`.

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

UI: `http://localhost:8501`

## Run Tests

```bash
pytest
```

## Resume Highlights

- Built a fast agentic content generation workflow with LangGraph.
- Designed graph nodes for planning, direct-language drafting, and SEO metadata generation.
- Exposed the workflow through a validated FastAPI service and a Streamlit product UI.
- Added SQLite persistence with retrieval and delete APIs.
- Containerized the API and UI with Docker Compose.
- Added CI and mocked tests to validate behavior without external LLM calls.

## Next Improvements

- Add a real web research provider such as Tavily or SerpAPI.
- Add a RAG pipeline with document loading, embeddings, vector storage, and retrieval.
- Add an editor node for grammar, clarity, and tone refinement.
- Add async background jobs for long-running generations.
- Add authentication for stored blog history.
- Add more languages in `src/config/languages.py`.
- Deploy the API and UI to Render, Railway, or Hugging Face Spaces.
