from src.storage.blog_repository import BlogRepository


def test_blog_repository_creates_lists_gets_and_deletes_records(tmp_path):
    repository = BlogRepository(f"sqlite:///{tmp_path / 'blogs.db'}")

    record = repository.create(
        {
            "topic": "Agentic AI",
            "current_language": "english",
            "tone": "professional",
            "audience": "developers",
            "length": "medium",
            "research_notes": "- Research note",
            "outline": "## Outline",
            "seo": {"slug": "agentic-ai"},
            "blog": {
                "title": "Agentic AI Guide",
                "content": "Blog content",
            },
        }
    )

    assert record["id"] == 1
    assert record["seo"]["slug"] == "agentic-ai"

    assert len(repository.list()) == 1
    assert repository.get(1)["title"] == "Agentic AI Guide"
    assert repository.delete(1) is True
    assert repository.get(1) is None
