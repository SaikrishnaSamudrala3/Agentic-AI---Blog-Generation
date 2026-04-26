from src.config.languages import language_display_name
from src.retrieval.web_retriever import WebRetriever
from src.states.blogstate import BlogState


def _fallback_slug(title: str) -> str:
    slug = "".join(character.lower() if character.isalnum() else "-" for character in title)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "blog-post"


def _split_title_and_content(markdown: str, fallback_title: str) -> dict[str, str]:
    lines = markdown.strip().splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            title = line.replace("# ", "", 1).strip()
            content = "\n".join(lines[index + 1 :]).strip()
            return {"title": title or fallback_title, "content": content}

    return {"title": fallback_title, "content": markdown.strip()}


class BlogNode:
    """
    Role-based agents for the blog generation graph.
    """

    def __init__(self, llm, web_retriever: WebRetriever | None = None):
        self.llm = llm
        self.web_retriever = web_retriever or WebRetriever()

    def web_retrieval_agent(self, state: BlogState):
        """
        Web Retrieval Agent: fetch current grounding context and source URLs.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required for the web retrieval agent.")

        result = self.web_retriever.retrieve(topic)
        return {
            "retrieved_context": result["context"],
            "sources": result["sources"],
            "retrieval_warning": result["warning"],
        }

    def concept_research_agent(self, state: BlogState):
        """
        Concept Research Agent: define key ideas and terminology.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required for the concept research agent.")

        target_language = language_display_name(state.get("current_language"))
        prompt = """
        You are the Concept Research Agent in a multi-agent blog generation system.
        Your job is to define the key ideas, terminology, and mental models.

        Topic: {topic}
        Target audience: {audience}
        Final language: {target_language}

        Retrieved web context:
        {retrieved_context}

        Return Markdown bullets only.
        Use the retrieved web context as the primary source of truth.
        If the context is insufficient, say what is missing instead of inventing facts.
        """
        response = self.llm.invoke(
            prompt.format(
                topic=topic,
                audience=state.get("audience", "technical readers"),
                target_language=target_language,
                retrieved_context=state.get("retrieved_context", ""),
            )
        )
        return {"concept_notes": response.content.strip()}

    def use_case_research_agent(self, state: BlogState):
        """
        Use Case Research Agent: identify applications and examples.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required for the use case research agent.")

        target_language = language_display_name(state.get("current_language"))
        prompt = """
        You are the Use Case Research Agent in a multi-agent blog generation system.
        Your job is to identify practical applications, examples, and benefits.

        Topic: {topic}
        Target audience: {audience}
        Final language: {target_language}

        Retrieved web context:
        {retrieved_context}

        Return Markdown bullets only.
        Use the retrieved web context as the primary source of truth.
        If the context is insufficient, say what is missing instead of inventing facts.
        """
        response = self.llm.invoke(
            prompt.format(
                topic=topic,
                audience=state.get("audience", "technical readers"),
                target_language=target_language,
                retrieved_context=state.get("retrieved_context", ""),
            )
        )
        return {"use_case_notes": response.content.strip()}

    def risk_research_agent(self, state: BlogState):
        """
        Risk Research Agent: identify limitations and tradeoffs.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required for the risk research agent.")

        target_language = language_display_name(state.get("current_language"))
        prompt = """
        You are the Risk Research Agent in a multi-agent blog generation system.
        Your job is to identify risks, limitations, tradeoffs, and implementation concerns.

        Topic: {topic}
        Target audience: {audience}
        Final language: {target_language}

        Retrieved web context:
        {retrieved_context}

        Return Markdown bullets only.
        Use the retrieved web context as the primary source of truth.
        If the context is insufficient, say what is missing instead of inventing facts.
        """
        response = self.llm.invoke(
            prompt.format(
                topic=topic,
                audience=state.get("audience", "technical readers"),
                target_language=target_language,
                retrieved_context=state.get("retrieved_context", ""),
            )
        )
        return {"risk_notes": response.content.strip()}

    def outline_agent(self, state: BlogState):
        """
        Outline Agent: turn research notes into a blog structure.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required for the outline agent.")

        target_language = language_display_name(state.get("current_language"))
        prompt = """
        You are the Outline Agent in a multi-agent blog generation system.
        Create a clear outline for the Writer Agent.

        Topic: {topic}
        Target audience: {audience}
        Tone: {tone}
        Length: {length}
        Final language: {target_language}

        Concept notes:
        {concept_notes}

        Use case notes:
        {use_case_notes}

        Risk notes:
        {risk_notes}

        Retrieved web context:
        {retrieved_context}

        Return Markdown with:
        - Working title direction.
        - Introduction angle.
        - 3 to 6 main sections.
        - Practical examples to include.
        - Conclusion angle.
        """
        response = self.llm.invoke(
            prompt.format(
                topic=topic,
                audience=state.get("audience", "technical readers"),
                tone=state.get("tone", "professional"),
                length=state.get("length", "medium"),
                target_language=target_language,
                concept_notes=state.get("concept_notes", ""),
                use_case_notes=state.get("use_case_notes", ""),
                risk_notes=state.get("risk_notes", ""),
                retrieved_context=state.get("retrieved_context", ""),
            )
        )
        research_notes = "\n\n".join(
            [
                "## Retrieved Web Context\n" + state.get("retrieved_context", ""),
                "## Concept Notes\n" + state.get("concept_notes", ""),
                "## Use Case Notes\n" + state.get("use_case_notes", ""),
                "## Risk Notes\n" + state.get("risk_notes", ""),
            ]
        )
        return {"research_notes": research_notes.strip(), "outline": response.content.strip()}

    def writer_agent(self, state: BlogState):
        """
        Writer Agent: write the draft directly in the selected language.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required for the writer agent.")

        target_language = language_display_name(state.get("current_language"))
        length_rules = {
            "short": "600 to 900 words with 3 main sections.",
            "medium": "1000 to 1400 words with 4 main sections.",
            "long": "1600 to 2200 words with 5 to 6 main sections.",
        }
        prompt = """
        You are the Writer Agent in a multi-agent blog generation system.
        Write the draft directly in {target_language}.

        Topic: {topic}
        Target audience: {audience}
        Tone: {tone}
        Length target: {length_rule}

        Research notes:
        {research_notes}

        Outline:
        {outline}

        Retrieved web context:
        {retrieved_context}

        Sources:
        {sources}

        Requirements:
        - Return only Markdown.
        - Start with a single H1 title.
        - Use clear H2/H3 headings.
        - Include practical examples where useful.
        - Keep the article accurate and readable.
        - Use retrieved web context as the source of truth for current or factual claims.
        - Do not invent citations or source URLs.
        - If the retrieved context is insufficient, explicitly say what could not be verified.
        """
        response = self.llm.invoke(
            prompt.format(
                target_language=target_language,
                topic=topic,
                audience=state.get("audience", "technical readers"),
                tone=state.get("tone", "professional"),
                length_rule=length_rules.get(state.get("length", "medium"), length_rules["medium"]),
                research_notes=state.get("research_notes", ""),
                outline=state.get("outline", ""),
                retrieved_context=state.get("retrieved_context", ""),
                sources="\n".join(
                    f"- {source.get('title')}: {source.get('url')}"
                    for source in state.get("sources", [])
                ),
            )
        )
        return {"draft_blog": _split_title_and_content(response.content, topic)}

    def editor_agent(self, state: BlogState):
        """
        Editor Agent: improve the draft while preserving language and Markdown.
        """
        draft_blog = state["draft_blog"]
        target_language = language_display_name(state.get("current_language"))
        prompt = """
        You are the Editor Agent in a multi-agent blog generation system.
        Improve this draft directly in {target_language}.

        Goals:
        - Improve clarity, flow, and structure.
        - Keep the same technical meaning.
        - Keep Markdown formatting.
        - Preserve the target language.
        - Return only the improved Markdown article.

        # {title}

        {content}
        """
        response = self.llm.invoke(
            prompt.format(
                target_language=target_language,
                title=draft_blog["title"],
                content=draft_blog["content"],
            )
        )
        edited_blog = _split_title_and_content(response.content, draft_blog["title"])
        return {
            "blog": edited_blog,
            "editor_notes": "Editor Agent improved clarity, structure, and readability.",
        }

    def seo_agent(self, state: BlogState):
        """
        SEO Agent: generate lightweight metadata locally for the final blog.
        """
        blog = state["blog"]
        words = blog["content"].split()
        reading_time = max(1, round(len(words) / 200))
        keywords = [
            state["topic"],
            language_display_name(state.get("current_language")),
            state.get("audience", "technical readers"),
        ]
        return {
            "seo": {
                "meta_title": blog["title"][:60],
                "meta_description": blog["content"].replace("\n", " ")[:160],
                "keywords": keywords,
                "slug": _fallback_slug(blog["title"]),
                "reading_time_minutes": reading_time,
            }
        }
