import asyncio
import os
import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from src.config.languages import SUPPORTED_LANGUAGES, normalize_language
from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM
from src.storage.blog_repository import BlogRepository

load_dotenv()
logger = logging.getLogger(__name__)

langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ.setdefault("LANGSMITH_API_KEY", langchain_api_key)

app = FastAPI(
    title="Agentic Blog Generation API",
    description="Generate Markdown blog posts with a LangGraph-powered LLM workflow.",
    version="0.1.0",
)
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
blog_repository = BlogRepository()


class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Blog topic to generate content for.")
    language: str | None = Field(
        default=None,
        min_length=2,
        description="Optional target language for translation, for example 'French'.",
    )
    tone: str = Field(default="professional", description="Desired writing tone.")
    audience: str = Field(default="technical readers", description="Target audience.")
    length: str = Field(default="medium", description="Desired output length.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "topic": "Agentic AI in software engineering",
                "language": "French",
                "tone": "professional",
                "audience": "software engineers",
                "length": "medium",
            }
        }
    )


class BlogResponse(BaseModel):
    id: int
    topic: str
    language: str | None = None
    title: str
    content: str
    research_notes: str | None = None
    outline: str | None = None
    editor_notes: str | None = None
    sources: list[dict[str, str]] = Field(default_factory=list)
    retrieval_warning: str | None = None
    seo: dict = Field(default_factory=dict)
    tone: str | None = None
    audience: str | None = None
    length: str | None = None
    status: str
    created_at: str


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/languages")
async def list_supported_languages():
    return {
        "default_language": "English",
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ],
    }


@app.post("/blogs", response_model=BlogResponse)
async def create_blog(payload: BlogRequest):
    try:
        record = await asyncio.to_thread(_generate_and_store_blog, payload)
        return BlogResponse(**record)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Blog generation failed.")
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {exc}") from exc


def _generate_and_store_blog(payload: BlogRequest):
    llm = GroqLLM().get_llm()
    graph = GraphBuilder(llm).setup_graph()

    initial_state = {
        "topic": payload.topic,
        "tone": payload.tone,
        "audience": payload.audience,
        "length": payload.length,
    }
    normalized_language = normalize_language(payload.language)
    if normalized_language:
        initial_state["current_language"] = normalized_language

    state = graph.invoke(initial_state)
    return blog_repository.create(state)


@app.get("/blogs", response_model=list[BlogResponse])
async def list_blogs():
    return [BlogResponse(**record) for record in blog_repository.list()]


@app.get("/blogs/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: int):
    record = blog_repository.get(blog_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Blog not found.")

    return BlogResponse(**record)


@app.delete("/blogs/{blog_id}")
async def delete_blog(blog_id: int):
    deleted = blog_repository.delete(blog_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blog not found.")

    return {"deleted": True}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
