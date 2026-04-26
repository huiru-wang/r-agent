import os

from langchain_tavily import TavilySearch
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the web for the given query using Tavily.
    """

    tavily_tool = TavilySearch(
        max_results=1,
        topic="general",
        tavily_api_key=os.environ.get("TAVILY_API_KEY"),
    )
    response = tavily_tool.invoke({"query": query})

    if isinstance(response, dict) and "error" in response:
        error_val = response["error"]
        error_msg = str(error_val) if isinstance(error_val, ValueError) else error_val
        raise ValueError(f"Tavily search failed: {error_msg}")

    results = response.get("results", [])
    if not results:
        return "No results found."

    return results[0].get("content", "No content available.")
