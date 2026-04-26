from src.graphs.graph_builder import GraphBuilder
class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def invoke(self, prompt: str):
        if "Create compact planning notes" in prompt:
            return FakeResponse("## Research Notes\n- Agentic AI automates workflows.\n\n## Outline\n- Intro")

        return FakeResponse(
            "# A Practical Guide to Agentic AI\n\n"
            "## Introduction\n\nAgentic AI helps automate multi-step work."
        )


def test_graph_generates_blog_without_translation():
    graph = GraphBuilder(FakeLLM()).setup_graph()

    state = graph.invoke({"topic": "Agentic AI"})

    assert state["blog"]["title"] == "A Practical Guide to Agentic AI"
    assert "Agentic AI" in state["blog"]["content"]
    assert state["research_notes"].startswith("## Research Notes")
    assert state["outline"].startswith("## Research Notes")
    assert state["seo"]["slug"] == "a-practical-guide-to-agentic-ai"


def test_graph_generates_directly_with_requested_language():
    graph = GraphBuilder(FakeLLM()).setup_graph()

    state = graph.invoke({"topic": "Agentic AI", "current_language": "telugu"})

    assert state["current_language"] == "telugu"
    assert state["blog"]["title"] == "A Practical Guide to Agentic AI"
    assert state["seo"]["keywords"][1] == "Telugu"
