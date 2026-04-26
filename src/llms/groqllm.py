import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


class GroqLLM:
    def __init__(self):
        load_dotenv()

    def get_llm(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is required. Add it to your environment or .env file.")

        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        return ChatGroq(api_key=groq_api_key, model=model)
