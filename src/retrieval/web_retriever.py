import os
from typing import Any

import requests


class WebRetriever:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

    def retrieve(self, query: str, max_results: int = 5) -> dict[str, Any]:
        if not self.api_key:
            return {
                "context": "",
                "sources": [],
                "warning": "TAVILY_API_KEY is not configured, so web retrieval was skipped.",
            }

        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": max_results,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        sources = []
        context_parts = []
        if payload.get("answer"):
            context_parts.append("## Search Answer\n" + payload["answer"])

        for index, result in enumerate(payload.get("results", []), start=1):
            title = result.get("title") or "Untitled"
            url = result.get("url") or ""
            content = result.get("content") or ""
            sources.append({"title": title, "url": url})
            context_parts.append(f"## Source {index}: {title}\nURL: {url}\n{content}")

        return {
            "context": "\n\n".join(context_parts).strip(),
            "sources": sources,
            "warning": None,
        }
