from typing import NotRequired, TypedDict

from pydantic import BaseModel, Field


class Blog(BaseModel):
    title: str = Field(description="Title of the blog post")
    content: str = Field(description="Main content of the blog post")


class BlogSEO(BaseModel):
    meta_title: str = Field(description="SEO meta title")
    meta_description: str = Field(description="SEO meta description")
    keywords: list[str] = Field(description="SEO keywords")
    slug: str = Field(description="URL-friendly slug")
    reading_time_minutes: int = Field(description="Estimated reading time in minutes")


class BlogState(TypedDict):
    topic: str
    blog: NotRequired[dict[str, str] | Blog]
    draft_blog: NotRequired[dict[str, str] | Blog]
    concept_notes: NotRequired[str]
    use_case_notes: NotRequired[str]
    risk_notes: NotRequired[str]
    research_notes: NotRequired[str]
    retrieved_context: NotRequired[str]
    sources: NotRequired[list[dict[str, str]]]
    retrieval_warning: NotRequired[str]
    outline: NotRequired[str]
    editor_notes: NotRequired[str]
    seo: NotRequired[dict | BlogSEO]
    current_language: NotRequired[str]
    tone: NotRequired[str]
    audience: NotRequired[str]
    length: NotRequired[str]
