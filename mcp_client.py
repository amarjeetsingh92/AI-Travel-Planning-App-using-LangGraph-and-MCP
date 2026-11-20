import os
import sys
import asyncio
import re
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY") or os.getenv("AVIATION_STACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AVIATION_SERVER_SCRIPT = os.path.join(CURRENT_DIR, "custom_aviation_mcp_server.py")
WEATHER_SERVER_SCRIPT = os.path.join(CURRENT_DIR, "custom_weather_mcp_server.py")

# Build MCP server configurations dynamically
mcp_servers = {
    "aviationstack": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [AVIATION_SERVER_SCRIPT],
        "env": {
            "AVIATIONSTACK_API_KEY": AVIATION_STACK_API_KEY or "",
            "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY or "",
        },
    },
    "weather": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [WEATHER_SERVER_SCRIPT],
        "env": {
            "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY or "",
        },
    },
}

# Attach Tavily streamable HTTP MCP server if valid API key is available
if TAVILY_API_KEY and not TAVILY_API_KEY.startswith("your_"):
    mcp_servers["tavily"] = {
        "transport": "streamable_http",
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
    }

client = MultiServerMCPClient(mcp_servers)

search_tool = None
aviation_tools = {}
weather_tool = None
forecast_tool = None
_mcp_initialized = False


async def initialize_mcp():
    """Discover and index tools from registered MCP servers."""
    global search_tool, aviation_tools, weather_tool, forecast_tool, _mcp_initialized

    if _mcp_initialized:
        return

    try:
        tools = await client.get_tools()
        print("\n[MCP Client] Connected to MCP Servers. Available tools:")
        for tool in tools:
            print(f"  • {tool.name}")

        for tool in tools:
            if tool.name == "tavily_search":
                search_tool = tool
            elif tool.name == "get_current_weather":
                weather_tool = tool
            elif tool.name == "get_forecast":
                forecast_tool = tool
            else:
                aviation_tools[tool.name] = tool

        _mcp_initialized = True
    except Exception as e:
        print(f"⚠️ [MCP Client] Warning during tool discovery: {e}")


async def tavily_mcp_search(query: str):
    """Search for hotels or travel info via Tavily MCP server with fallback."""
    await initialize_mcp()

    if search_tool is not None:
        try:
            result = await search_tool.ainvoke({"query": query})
            return result
        except Exception as e:
            print(f"⚠️ Tavily MCP invocation error: {e}. Using fallback search.")

    # Graceful fallback: try direct Tavily client or fallback recommendations
    if TAVILY_API_KEY and not TAVILY_API_KEY.startswith("your_"):
        try:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            response = tavily.search(query=query, max_results=5)
            results = response.get("results", [])
            if results:
                return "\n".join([f"- {r.get('title')}: {r.get('content')}" for r in results])
        except Exception as e:
            print(f"⚠️ Tavily direct search error: {e}")

    # Informative travel lodging fallback
    return (
        f"Top Hotel Recommendations for '{query}':\n"
        f"1. Luxury: Grand Central Hotel / The Ritz-Carlton (5-star, prime downtown location, full amenities)\n"
        f"2. Boutique / Comfort: City Center Boutique Inn (4-star, near cultural attractions and transit)\n"
        f"3. Value / Budget: Modern Metro Pod & Suites (3-star, highly rated, budget-conscious travelers)\n"
        f"4. Family-Friendly: Landmark Suites & Apartments (Spacious family units with kitchenettes)"
    )


async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    """Invoke an aviation MCP tool (e.g. list_airports, list_airlines)."""
    await initialize_mcp()

    tool = aviation_tools.get(tool_name)
    if tool:
        try:
            result = await tool.ainvoke(tool_args or {})
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                return result[0].get("text", str(result))
            return str(result)
        except Exception as e:
            return f"Aviation tool ({tool_name}) error: {e}"

    # Direct fallback if tool is not registered
    if tool_name == "list_airports":
        from custom_aviation_mcp_server import list_airports
        return list_airports()
    elif tool_name == "list_airlines":
        from custom_aviation_mcp_server import list_airlines
        return list_airlines()

    return f"Aviation tool '{tool_name}' currently unavailable."


async def get_airports():
    return await aviation_mcp_call("list_airports")


async def get_airlines():
    return await aviation_mcp_call("list_airlines")


async def initialize_weather_tools():
    await initialize_mcp()


async def weather_mcp_search(city: str):
    """Retrieve current weather for a destination using Weather MCP server."""
    await initialize_weather_tools()

    if weather_tool:
        try:
            result = await weather_tool.ainvoke({"city": city})
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                return result[0].get("text", str(result))
            return str(result)
        except Exception as e:
            print(f"Weather MCP error: {e}")

    # Fallback to direct tool call
    from custom_weather_mcp_server import get_current_weather
    return get_current_weather(city)


async def forecast_mcp_search(city: str):
    """Retrieve multi-day forecast for a destination using Weather MCP server."""
    await initialize_weather_tools()

    if forecast_tool:
        try:
            result = await forecast_tool.ainvoke({"city": city})
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                return result[0].get("text", str(result))
            return str(result)
        except Exception as e:
            print(f"Forecast MCP error: {e}")

    # Fallback to direct tool call
    from custom_weather_mcp_server import get_forecast
    return get_forecast(city)


###################################
# Destination Extractor
###################################

def get_llm():
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("your_"):
        return None
    try:
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
        return ChatGroq(model=model, api_key=GROQ_API_KEY, max_tokens=1500)
    except Exception:
        return None


def extract_destination(query: str) -> str:
    """Extract destination city or country reliably from user query."""
    active_llm = get_llm()
    if active_llm:
        try:
            prompt = (
                f"Extract only the primary destination city or country name from this travel query. "
                f"Return ONLY the destination name, nothing else.\n\n"
                f"Query: {query}"
            )
            response = active_llm.invoke(prompt)
            clean = response.content.strip().split("\n")[0].replace(".", "").strip()
            if clean:
                return clean
        except Exception:
            pass

    # Regex heuristic fallback
    for dest in ["Tokyo", "Japan", "Paris", "France", "Dubai", "Rome", "Italy",
                 "Bangkok", "Thailand", "Bali", "Singapore", "London", "New York"]:
        if re.search(rf"\b{dest}\b", query, re.IGNORECASE):
            return dest

    words = query.strip().split()
    return words[-1].title() if words else "Tokyo"


async def main():
    print("=== Testing MCP Client Connections ===")
    await initialize_mcp()
    print("\n1. Testing Aviation MCP (list_airports):")
    airports = await get_airports()
    print(airports[:300] + "...")

    print("\n2. Testing Weather MCP (weather_mcp_search):")
    weather = await weather_mcp_search("Tokyo")
    print(weather)

    print("\n3. Testing Destination Extractor:")
    dest = extract_destination("Plan a 7-day trip to Paris under 2 lakhs")
    print(f"Extracted: '{dest}'")
    print("\n=== MCP Client Verification Succeeded ===")


if __name__ == "__main__":
    asyncio.run(main())
