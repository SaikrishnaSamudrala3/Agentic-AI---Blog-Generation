import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


class GroqLLM:
    def __init__(self):
        load_dotenv()

    def get_llm(self):
        provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
        if provider == "openai":
            return self._get_openai_llm()

        if provider == "groq":
            return self._get_groq_llm()

        raise ValueError("LLM_PROVIDER must be either 'openai' or 'groq'.")

    def _get_openai_llm(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(api_key=openai_api_key, model=model)

    def _get_groq_llm(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq.")

        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(api_key=groq_api_key, model=model)
