import argparse

from src.config.languages import normalize_language
from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM


def generate_blog(
    topic: str,
    language: str | None = None,
    tone: str = "professional",
    audience: str = "technical readers",
    length: str = "medium",
):
    llm = GroqLLM().get_llm()
    graph = GraphBuilder(llm).setup_graph()

    initial_state = {
        "topic": topic,
        "tone": tone,
        "audience": audience,
        "length": length,
    }
    normalized_language = normalize_language(language)
    if normalized_language:
        initial_state["current_language"] = normalized_language

    return graph.invoke(initial_state)


def main():
    parser = argparse.ArgumentParser(description="Generate a blog post with the agentic workflow.")
    parser.add_argument("topic", help="Topic for the blog post.")
    parser.add_argument(
        "--language",
        "-l",
        help="Optional target language for translation, for example 'french'.",
    )
    parser.add_argument("--tone", default="professional", help="Desired writing tone.")
    parser.add_argument("--audience", default="technical readers", help="Target audience.")
    parser.add_argument("--length", default="medium", help="Desired output length.")
    args = parser.parse_args()

    state = generate_blog(args.topic, args.language, args.tone, args.audience, args.length)
    blog = state["blog"]

    print(f"# {blog['title']}\n")
    print(blog["content"])
    if state.get("seo"):
        print("\n## SEO Metadata")
        for key, value in state["seo"].items():
            print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
