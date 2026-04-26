from langgraph.graph import END, START, StateGraph

from src.nodes.blog_node import BlogNode
from src.states.blogstate import BlogState


class GraphBuilder:
    def __init__(self, llm, web_retriever=None):
        self.llm = llm
        self.web_retriever = web_retriever

    def build_graph(self):
        """
        Build a role-based multi-agent blog generation graph.
        """
        graph = StateGraph(BlogState)
        blog_node = BlogNode(self.llm, web_retriever=self.web_retriever)

        graph.add_node("web_retrieval_agent", blog_node.web_retrieval_agent)
        graph.add_node("concept_research_agent", blog_node.concept_research_agent)
        graph.add_node("use_case_research_agent", blog_node.use_case_research_agent)
        graph.add_node("risk_research_agent", blog_node.risk_research_agent)
        graph.add_node("outline_agent", blog_node.outline_agent)
        graph.add_node("writer_agent", blog_node.writer_agent)
        graph.add_node("editor_agent", blog_node.editor_agent)
        graph.add_node("seo_agent", blog_node.seo_agent)

        graph.add_edge(START, "web_retrieval_agent")
        graph.add_edge("web_retrieval_agent", "concept_research_agent")
        graph.add_edge("web_retrieval_agent", "use_case_research_agent")
        graph.add_edge("web_retrieval_agent", "risk_research_agent")
        graph.add_edge(
            ["concept_research_agent", "use_case_research_agent", "risk_research_agent"],
            "outline_agent",
        )
        graph.add_edge("outline_agent", "writer_agent")
        graph.add_edge("writer_agent", "editor_agent")
        graph.add_edge("editor_agent", "seo_agent")
        graph.add_edge("seo_agent", END)

        return graph

    def setup_graph(self, usecase: str | None = None):
        return self.build_graph().compile()
