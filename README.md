# Odyssey AI: Multi-Agent Travel Planning System using LangGraph & MCP

A full-stack, autonomous Multi-Agent Travel Planning & Booking application built with **LangGraph**, **Model Context Protocol (MCP)**, **Groq Cloud LLMs**, **PostgreSQL Memory & Bcrypt Authentication**, and a dark-theme **Streamlit** dashboard.

Developed and maintained by **Amarjeet Kumar**.

---

## 🌟 Key Capabilities

| Capability | Specification |
|---|---|
| **Multi-Agent Orchestration** | 5 Autonomous LangGraph Agents (Flight, Hotel, Weather, Itinerary, Concierge) |
| **Authentication & Security** | PostgreSQL User Database with salted **Bcrypt** password hashing (Cost factor 12) |
| **User Trip History** | Persistent per-user travel history stored in PostgreSQL (`user_trips`) |
| **Flight Intelligence** | **AviationStack MCP Server** (stdio FastMCP) |
| **Weather & Forecasts** | **OpenWeatherMap MCP Server** (stdio FastMCP) |
| **Hotel & Stay Research** | **Tavily MCP Server** (streamable HTTP) with AI synthesis |
| **Memory / Checkpointing** | PostgreSQL (`PostgresSaver`) with graceful In-Memory fallback (`MemorySaver`) |
| **Production Ready** | Fully containerized with `Dockerfile` and `docker-compose.yml` |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User["👤 User (Authenticated via Bcrypt)"] --> UI["💻 Streamlit Web UI (Odyssey AI)"]
    UI --> Graph["🔗 LangGraph Multi-Agent Workflow"]
    
    subgraph Agents["🤖 Specialized AI Agent Team"]
        A1["① ✈️ Flight Agent"]
        A2["② 🏨 Hotel Agent"]
        A3["③ ⛅ Weather Agent"]
        A4["④ 🗓️ Itinerary Agent"]
        A5["⑤ 🧠 Final Concierge Agent"]
    end
    
    Graph --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5
    
    subgraph MCPServers["⚡ Model Context Protocol (MCP) Infrastructure"]
        MCPAviation["✈️ AviationStack MCP Server (stdio FastMCP)"]
        MCPWeather["⛅ Weather MCP Server (stdio FastMCP)"]
        MCPTavily["🔍 Tavily MCP Server (streamable_http)"]
    end
    
    A1 <-->|"list_airports, list_airlines"| MCPAviation
    A2 <-->|"tavily_search"| MCPTavily
    A3 <-->|"get_current_weather, get_forecast"| MCPWeather
    
    A4 --> LLM["🧠 Groq Cloud LLM (openai/gpt-oss-120b)"]
    A5 --> LLM
    
    A5 --> Plan["📄 Complete Travel Proposal (Markdown & Export)"]
    Graph <--> DB[("🐘 PostgreSQL Checkpointer (PostgresSaver)")]
    UI <--> UserDB[("🔐 PostgreSQL User & Trip History (Bcrypt Auth)")]
```

---

## 🚀 Specialized Agent Team

1. **✈️ Flight Agent:** Discovers optimal departure and arrival hubs, carrier networks, layover guidance, and fare estimates via the AviationStack FastMCP server.
2. **🏨 Hotel Agent:** Identifies top luxury, boutique, and budget accommodations via Tavily MCP search, synthesizing amenities, pricing, transit proximity, and verified booking links.
3. **⛅ Weather Agent:** Evaluates destination climate and live 5-day forecasts via OpenWeather MCP to provide tailored packing advice and climate advisories.
4. **🗓️ Itinerary Agent:** Crafts an immersive day-by-day itinerary balancing cultural sightseeing, activities, and dining matching the user's travel style and dietary preferences.
5. **🧠 Chief Concierge Agent:** Assembles an executive-ready proposal with complete budget breakdowns and cost-saving tips.

---

## 📋 Prerequisites & APIs

Get your API keys:
- **Groq Cloud:** [https://console.groq.com](https://console.groq.com)
- **Tavily AI:** [https://tavily.com](https://tavily.com)
- **AviationStack:** [https://aviationstack.com](https://aviationstack.com)
- **OpenWeatherMap:** [https://openweathermap.org](https://openweathermap.org)
- **PostgreSQL Database** (Local or Cloud instance e.g., Supabase / Neon / RDS)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/amarjeetsingh92/AI-Travel-Planning-App-using-LangGraph-and-MCP.git
cd AI-Travel-Planning-App-using-LangGraph-and-MCP
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:
```env
# Groq LLM
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b

# Search & MCP Tools
TAVILY_API_KEY=tvly-...
AVIATIONSTACK_API_KEY=...
OPENWEATHER_API_KEY=...

# PostgreSQL Connection (URL-encode special characters in password e.g. @ as %40)
DATABASE_URL=postgresql://postgres:password@localhost:5432/langgraph_memory_demo
```

---

## 🖥️ Running the Application

### Launch the Streamlit Web UI
```bash
streamlit run frontend.py
```
Open your browser at `http://localhost:8501`.

1. Register a new user account on the **Create Account** tab (passwords are hashed with Bcrypt before saving to PostgreSQL).
2. Sign in with your username/email and password.
3. Customize your journey parameters (travel style, duration, budget currency) or click a quick preset.
4. View live agent coordination, synthesized proposals, and past saved journeys.

---

## 🐳 Docker & Cloud Deployment

### Run with Docker Compose
The project includes a multi-service `docker-compose.yml` with optional PostgreSQL service:
```bash
# Build and start services
docker compose up -d --build

# View logs
docker compose logs -f web
```
Access at `http://localhost:8501`.

### Deploy to Render / Railway / Cloud VM
1. Connect your GitHub repository to Render / Railway.
2. Select **Docker** environment.
3. Configure your environment variables (`GROQ_API_KEY`, `TAVILY_API_KEY`, `OPENWEATHER_API_KEY`, `AVIATIONSTACK_API_KEY`, `DATABASE_URL`).
4. Set port to `8501`.

---

## 📁 Directory Structure

```text
├── auth.py                       # PostgreSQL user registration, bcrypt hashing & trip history
├── custom_aviation_mcp_server.py # FastMCP Aviation server (airports, airlines, status)
├── custom_weather_mcp_server.py  # FastMCP Weather server (current conditions, forecasts)
├── mcp_client.py                 # MultiServerMCPClient manager & tool router
├── main.py                       # LangGraph StateGraph pipeline & 5 agent nodes
├── frontend.py                   # Modern Streamlit UI with Auth, Journey Planner & History
├── tools/                        # Fallback direct tools
│   ├── flight_tool.py            # AviationStack direct REST helper
│   └── tavily_tool.py            # Tavily direct search helper
├── .streamlit/
│   └── config.toml               # Streamlit server and theme configuration
├── Dockerfile                    # Production Docker container definition
├── docker-compose.yml            # Multi-container orchestration (App + PostgreSQL)
├── requirements.txt              # Project dependencies
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore rules (protects .env and venv)
└── README.md                     # Documentation
```

---

## 🛡️ Author & Attribution
Developed and maintained by **Amarjeet Kumar** ([GitHub: @amarjeetsingh92](https://github.com/amarjeetsingh92)).
Built with LangGraph, Model Context Protocol, and Groq Cloud.
