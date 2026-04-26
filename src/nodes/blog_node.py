from src.config.languages import language_display_name
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
    LangGraph node implementations for a fast blog generation flow.
    """

    def __init__(self, llm):
        self.llm = llm

    def planning(self, state: BlogState):
        """
        Produce compact research notes and an outline in one LLM call.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required to plan a blog.")

        target_language = language_display_name(state.get("current_language"))
        prompt = """
        You are a senior content strategist.
        Create compact planning notes for a blog post.

        Topic: {topic}
        Target audience: {audience}
        Tone: {tone}
        Length: {length}
        Final language: {target_language}

        Return Markdown with exactly these sections:
        ## Research Notes
        - 4 to 6 factual bullets.

        ## Outline
        - Introduction angle.
        - 3 to 5 main sections.
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
            )
        )
        plan = response.content.strip()
        return {"research_notes": plan, "outline": plan}

    def content_generation(self, state: BlogState):
        """
        Generate the final blog directly in the requested language.
        """
        topic = state.get("topic")
        if not topic:
            raise ValueError("Topic is required to generate blog content.")

        target_language = language_display_name(state.get("current_language"))
        length_rules = {
            "short": "600 to 900 words with 3 main sections.",
            "medium": "1000 to 1400 words with 4 main sections.",
            "long": "1600 to 2200 words with 5 to 6 main sections.",
        }
        system_prompt = """
        You are an expert technical blog writer.
        Write the final blog post directly in {target_language}.

        Topic: {topic}
        Target audience: {audience}
        Tone: {tone}
        Length target: {length_rule}

        Planning notes:
        {outline}

        Requirements:
        - Return only Markdown.
        - Start with a single H1 title.
        - Use clear H2/H3 headings.
        - Include practical examples where useful.
        - Keep the explanation accurate and readable for the target audience.
        - Do not invent citations or source URLs.
        """
        response = self.llm.invoke(
            system_prompt.format(
                target_language=target_language,
                topic=topic,
                audience=state.get("audience", "technical readers"),
                tone=state.get("tone", "professional"),
                length_rule=length_rules.get(state.get("length", "medium"), length_rules["medium"]),
                outline=state.get("outline", ""),
            )
        )
        return {"blog": _split_title_and_content(response.content, topic)}

    def seo_generation(self, state: BlogState):
        """
        Generate lightweight SEO metadata locally for the final blog content.
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
