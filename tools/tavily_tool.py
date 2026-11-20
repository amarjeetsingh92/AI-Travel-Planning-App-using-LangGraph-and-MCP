import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# https://www.tavily.com/ 
# Signup and login, On dashboard -> under api keys you will see the default key.
# Use that or click on + to create new one. Then save it in .env file

def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key.startswith("your_"):
        return None
    try:
        return TavilyClient(api_key=api_key)
    except Exception:
        return None

def tavily_search(query):
    client = get_tavily_client()
    if not client:
        return "⚠️ TAVILY_API_KEY is not configured in .env. Please provide a valid key from https://tavily.com."

    try:
        response = client.search(
            query=query,
            max_results=5
        )

        results = []
        for i, r in enumerate(response.get("results", []), 1):
            title   = r.get("title", "Unknown")
            url     = r.get("url", "")
            snippet = r.get("content", "").strip()
            # Keep only the first 300 characters to avoid wall-of-text
            if len(snippet) > 300:
                snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

            results.append(f"{i}. **{title}**\n   {url}\n   {snippet}")

        return "\n\n".join(results) if results else "No search results found."
    except Exception as e:
        return f"⚠️ Error fetching search results from Tavily: {str(e)}"
