import os
import requests
from dotenv import load_dotenv
from tools.tavily_tool import tavily_search

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def search_flights(query):
    # Try AviationStack API if configured
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    if api_key and not api_key.startswith("your_"):
        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": api_key,
            "limit": 5
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"]:
                    flights = []
                    for flight in data["data"][:5]:
                        airline = flight.get("airline", {}).get("name", "Unknown")
                        departure = flight.get("departure", {}).get("airport", "Unknown")
                        arrival = flight.get("arrival", {}).get("airport", "Unknown")
                        status = flight.get("flight_status", "Unknown")

                        flights.append(
                            f"Airline: {airline}\nDeparture: {departure}\nArrival: {arrival}\nStatus: {status}\n"
                        )
                    if flights:
                        return "\n".join(flights)
        except Exception:
            pass  # Fall back to web search

    # Fallback: Search relevant flight options using Tavily search
    fallback_query = f"flights options routes and airlines for {query}"
    search_res = tavily_search(fallback_query)
    if "⚠️" not in search_res:
        return f"✈️ Flight Information via Web Search:\n\n{search_res}"

    return "⚠️ AviationStack API key is not configured or limit reached. You can add AVIATIONSTACK_API_KEY or TAVILY_API_KEY in .env to get live flight data."
