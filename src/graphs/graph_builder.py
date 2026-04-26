from langgraph.graph import END, START, StateGraph

from src.nodes.blog_node import BlogNode
from src.states.blogstate import BlogState


class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm

    def build_graph(self):
        """
        Build a fast blog generation graph.
        """
        graph = StateGraph(BlogState)
        blog_node = BlogNode(self.llm)

        graph.add_node("planning", blog_node.planning)
        graph.add_node("content_generation", blog_node.content_generation)
        graph.add_node("seo_generation", blog_node.seo_generation)

        graph.add_edge(START, "planning")
        graph.add_edge("planning", "content_generation")
        graph.add_edge("content_generation", "seo_generation")
        graph.add_edge("seo_generation", END)

        return graph

    def setup_graph(self, usecase: str | None = None):
        return self.build_graph().compile()
