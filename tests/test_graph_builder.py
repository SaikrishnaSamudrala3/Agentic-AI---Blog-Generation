from src.graphs.graph_builder import GraphBuilder


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeWebRetriever:
    def retrieve(self, query: str, max_results: int = 5):
        return {
            "context": "Royal Challengers Bengaluru won IPL 2025.",
            "sources": [{"title": "IPL 2025 Final", "url": "https://example.com/ipl-2025"}],
            "warning": None,
        }


class FakeLLM:
    def invoke(self, prompt: str):
        if "Concept Research Agent" in prompt:
            return FakeResponse("- Agentic AI systems plan and act toward goals.")

        if "Use Case Research Agent" in prompt:
            return FakeResponse("- Agentic AI can automate engineering workflows.")

        if "Risk Research Agent" in prompt:
            return FakeResponse("- Agentic AI needs guardrails and evaluation.")

        if "Outline Agent" in prompt:
            return FakeResponse("## Outline\n- Intro\n- Workflow design")

        if "Writer Agent" in prompt:
            return FakeResponse(
                "# A Practical Guide to Agentic AI\n\n"
                "## Introduction\n\nAgentic AI helps automate multi-step work."
            )

        return FakeResponse(
            "# Edited Guide to Agentic AI\n\n"
            "## Introduction\n\nAgentic AI helps teams automate multi-step work."
        )


def test_graph_generates_blog_without_translation():
    graph = GraphBuilder(FakeLLM(), web_retriever=FakeWebRetriever()).setup_graph()

    state = graph.invoke({"topic": "Agentic AI"})

    assert state["blog"]["title"] == "Edited Guide to Agentic AI"
    assert "Agentic AI" in state["blog"]["content"]
    assert state["concept_notes"].startswith("- Agentic AI systems")
    assert state["use_case_notes"].startswith("- Agentic AI can")
    assert state["risk_notes"].startswith("- Agentic AI needs")
    assert "Royal Challengers Bengaluru" in state["retrieved_context"]
    assert state["sources"][0]["url"] == "https://example.com/ipl-2025"
    assert "## Concept Notes" in state["research_notes"]
    assert state["outline"].startswith("## Outline")
    assert state["editor_notes"].startswith("Editor Agent")
    assert state["seo"]["slug"] == "edited-guide-to-agentic-ai"


def test_graph_generates_directly_with_requested_language():
    graph = GraphBuilder(FakeLLM(), web_retriever=FakeWebRetriever()).setup_graph()

    state = graph.invoke({"topic": "Agentic AI", "current_language": "telugu"})

    assert state["current_language"] == "telugu"
    assert state["blog"]["title"] == "Edited Guide to Agentic AI"
    assert state["seo"]["keywords"][1] == "Telugu"
