from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM


llm = GroqLLM().get_llm()
graph = GraphBuilder(llm).build_graph().compile()
