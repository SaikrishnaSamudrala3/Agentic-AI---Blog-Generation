# Agentic AI Blog Generation

A full-stack agentic blog generator that creates Markdown articles with a LangGraph multi-agent workflow. The backend uses FastAPI, the primary frontend is built with Next.js, and generated blogs are stored in SQLite with research notes, source URLs, SEO metadata, and history.

## What It Does

- Generates blog posts from a topic, audience, tone, length, and language.
- Retrieves current web context with Tavily when `TAVILY_API_KEY` is configured.
- Runs parallel research agents for concepts, use cases, and risks.
- Builds an outline, writes the article, edits it, and generates SEO metadata.
- Stores generated posts in SQLite.
- Exposes the workflow through a FastAPI API, a Next.js UI, a Streamlit UI, and a CLI.
- Supports English, French, Hindi, Spanish, German, and Telugu.

## Tech Stack

- Python 3.13
- FastAPI and Uvicorn
- LangGraph and LangChain
- OpenAI by default, with optional Groq support
- Tavily for web retrieval
- SQLite for local persistence
- Next.js 16, React 19, and TypeScript
- Streamlit as an alternate UI
- Pytest and GitHub Actions CI
- Docker and Docker Compose

## Project Structure

```text
.
├── app.py                    # FastAPI app and API route definitions
├── main.py                   # CLI entry point for local generation
├── streamlit_app.py          # Optional Streamlit UI
├── langgraph.json            # LangGraph Studio config
├── Dockerfile                # Backend container
├── docker-compose.yml        # Backend + frontend local container setup
├── requirements.txt          # Python dependency list for pip/Docker
├── pyproject.toml            # Python project metadata and pytest config
├── uv.lock                   # uv lockfile
├── request.json              # Example request payload
├── data/                     # Local SQLite database folder, ignored by git
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Main Next.js UI
│   │   ├── api.ts            # API client helpers
│   │   ├── types.ts          # Frontend TypeScript types
│   │   ├── layout.tsx        # App shell metadata/layout
│   │   └── globals.css       # UI styling
│   ├── package.json          # Frontend scripts and dependencies
│   └── Dockerfile            # Frontend container
├── src/
│   ├── config/
│   │   └── languages.py      # Supported language normalization/display
│   ├── graphs/
│   │   ├── graph_builder.py  # LangGraph workflow topology
│   │   └── studio.py         # LangGraph Studio graph export
│   ├── llms/
│   │   └── groqllm.py        # OpenAI/Groq LLM provider factory
│   ├── nodes/
│   │   └── blog_node.py      # Agent node implementations
│   ├── retrieval/
│   │   └── web_retriever.py  # Tavily search integration
│   ├── states/
│   │   └── blogstate.py      # Shared graph state and response schemas
│   └── storage/
│       └── blog_repository.py # SQLite persistence layer
├── tests/                    # Mocked graph, language, and storage tests
└── .github/workflows/ci.yml  # GitHub Actions test workflow
```

## Agent Workflow

```text
API / CLI / UI
     |
     v
FastAPI or local CLI
     |
     v
LangGraph StateGraph
     |
     +--> Web Retrieval Agent
     |
     +--> Concept Research Agent ┐
     +--> Use Case Research Agent ├─ parallel research
     +--> Risk Research Agent    ┘
     |
     +--> Outline Agent
     +--> Writer Agent
     +--> Editor Agent
     +--> SEO Agent
     |
     v
SQLite blog history
```

## Environment Setup

Clone the repository and create a Python environment:

```bash
git clone https://github.com/SaikrishnaSamudrala3/Agentic-AI---Blog-Generation.git
cd Agentic-AI---Blog-Generation

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your keys:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Optional Groq provider.
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Optional, but recommended for web-grounded output.
TAVILY_API_KEY=your_tavily_api_key_here

DATABASE_URL=sqlite:///data/blogs.db
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Optional LangSmith tracing.
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

To use Groq instead of OpenAI:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

If `TAVILY_API_KEY` is missing, generation still runs, but web retrieval is skipped and the response includes a retrieval warning.

## Run The Backend API

```bash
python app.py
```

The local API runs at `http://localhost:8000`.

Useful routes:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/languages
curl http://localhost:8000/blogs
curl http://localhost:8000/blogs/1
```

Generate and store a blog:

```bash
curl -X POST http://localhost:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Agentic AI in software engineering",
    "language": "French",
    "tone": "professional",
    "audience": "software engineers",
    "length": "medium"
  }'
```

Delete a stored blog:

```bash
curl -X DELETE http://localhost:8000/blogs/1
```

## Run The Next.js UI

Start the backend first. Then, in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The UI lets you generate a blog, preview Markdown, inspect research notes and SEO metadata, view source URLs, download Markdown, browse history, and delete stored posts.

## Run The Streamlit UI

Start the backend first. Then run:

```bash
streamlit run streamlit_app.py
```

Streamlit uses `API_BASE_URL` from `.env`, defaulting to `http://localhost:8000`.

## Run From The CLI

```bash
python main.py "Agentic AI in software engineering"
python main.py "Agentic AI in software engineering" \
  --language french \
  --audience "software engineers" \
  --tone technical \
  --length long
```

The CLI prints the generated Markdown and SEO metadata to the terminal. It does not store the result in SQLite; storage is handled by the API route.

## Run With Docker Compose

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Next.js UI: `http://localhost:3000`
- SQLite data: Docker volume `blog_data`

The backend Dockerfile listens on `${PORT:-10000}` for deployment platforms such as Render. Docker Compose maps the API container to local port `8000`.

## LangGraph Studio

The graph is exported from `src/graphs/studio.py` and configured in `langgraph.json`:

```bash
langgraph dev
```

This uses `.env` for provider keys and graph settings.

## Run Tests

```bash
pytest
```

The tests use fake LLM and fake web retriever objects, so they do not require OpenAI, Groq, or Tavily API calls.

CI runs the same test suite through `.github/workflows/ci.yml` on pushes and pull requests.

## API Response Shape

Generated blog records include:

- `id`, `topic`, `language`, `title`, `content`, `status`, `created_at`
- `research_notes`, `outline`, and `editor_notes`
- `sources` from Tavily retrieval
- `retrieval_warning` when retrieval is unavailable
- `seo` with meta title, meta description, keywords, slug, and reading time
- `tone`, `audience`, and `length`

## Notes For Deployment

- Set `OPENAI_API_KEY` or `GROQ_API_KEY` in the backend environment.
- Set `TAVILY_API_KEY` if you want source-grounded generation.
- Set `DATABASE_URL=sqlite:///data/blogs.db` for local or volume-backed SQLite.
- Set `CORS_ORIGINS` to include your deployed frontend URL.
- Set `NEXT_PUBLIC_API_BASE_URL` in the frontend environment to the deployed backend URL.

