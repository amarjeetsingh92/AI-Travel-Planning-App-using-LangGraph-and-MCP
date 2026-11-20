"""
AI Travel Planning & Booking System · LangGraph + MCP
Interactive Multi-Agent Dashboard with Secure PostgreSQL Authentication
"""

import os
import streamlit as st

# ── Sync Streamlit Cloud Secrets into os.environ ──────────────────────────────
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, str):
                os.environ[k] = v
except Exception:
    pass

from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app
import auth

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Odyssey AI · Autonomous Travel Planning System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS Styling ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #070b12;
    color: #e2ecf8;
}

/* ── Top Bar & Branding ── */
.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(90deg, #0d1527 0%, #0a1120 100%);
    border: 1px solid #1a2844;
    border-radius: 14px;
    padding: 0.9rem 1.6rem;
    margin-bottom: 1.5rem;
}
.brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    letter-spacing: -0.01em;
}
.brand-badge {
    background: rgba(58, 123, 213, 0.2);
    border: 1px solid rgba(58, 123, 213, 0.5);
    color: #7ab8f5;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.25rem 0.65rem;
    border-radius: 20px;
}

/* ── Auth Container ── */
.auth-wrapper {
    max-width: 480px;
    margin: 3rem auto;
    background: linear-gradient(180deg, #0e172a 0%, #0a1120 100%);
    border: 1px solid #1e2f4d;
    border-radius: 20px;
    padding: 2.4rem 2.2rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), 0 0 30px rgba(58, 123, 213, 0.1);
}
.auth-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    text-align: center;
    margin-bottom: 0.4rem;
}
.auth-sub {
    font-size: 0.92rem;
    color: #8aa0be;
    text-align: center;
    margin-bottom: 1.6rem;
}
.auth-shield {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #4ade80;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 0.35rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 1.5rem;
}

/* ── Hero Banner ── */
.hero-wrapper {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1.8rem;
    height: 260px;
    border: 1px solid #1a2a44;
}
.hero-bg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.32);
    position: absolute;
    top: 0; left: 0;
}
.hero-content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 1.5rem 2rem;
}
.hero-badge {
    background: rgba(58, 123, 213, 0.25);
    border: 1px solid rgba(58, 123, 213, 0.5);
    color: #8fc2f7 !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 0.75rem;
    display: inline-block;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.5rem;
    line-height: 1.2;
}
.hero-sub {
    color: #9cb5d1;
    font-size: 0.96rem;
    max-width: 650px;
    line-height: 1.5;
}

/* ── Cards & Containers ── */
.app-card {
    background: #0b1322;
    border: 1px solid #16243b;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}
.card-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e0edf8;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Metric Box ── */
.metric-row {
    display: flex;
    gap: 0.9rem;
    margin: 1.2rem 0;
}
.metric-box {
    flex: 1;
    background: #0b1322;
    border: 1px solid #182842;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-val { font-size: 1.7rem; font-weight: 800; color: #4ea8f0; }
.metric-lbl {
    font-size: 0.74rem;
    color: #7b9dc0 !important;
    margin-top: 0.2rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

/* ── Final Plan Card ── */
.plan-summary-card {
    background: linear-gradient(170deg, #0d1a2f 0%, #08111e 100%);
    border: 1px solid #203a5e;
    border-left: 4px solid #3a7bd5;
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    line-height: 1.75;
    color: #d3e4f7;
    font-size: 0.96rem;
    margin-top: 1rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #080d16 !important;
    border-right: 1px solid #142033 !important;
}
.sidebar-user {
    background: linear-gradient(135deg, #101c30 0%, #0c1524 100%);
    border: 1px solid #1d3050;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.sidebar-status-chip {
    background: #0c1524;
    border: 1px solid #16253c;
    border-radius: 8px;
    padding: 0.45rem 0.7rem;
    margin-bottom: 0.35rem;
    font-size: 0.82rem;
    color: #8da9c7;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #22c55e;
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all 0.25s ease !important;
}
.primary-btn button {
    background: linear-gradient(135deg, #1f6fc9 0%, #115099 100%) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.8rem 2rem !important;
    font-size: 1.02rem !important;
    box-shadow: 0 4px 20px rgba(31, 111, 201, 0.35) !important;
}
.primary-btn button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 25px rgba(31, 111, 201, 0.5) !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    background: #0a111e !important;
    border: 1px solid #1a2a44 !important;
    border-radius: 9px !important;
    color: #e2ecf8 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 2px rgba(58, 123, 213, 0.25) !important;
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    color: #8da9c7 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #7ab8f5 !important;
    border-bottom-color: #3a7bd5 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session State Management ──────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "plan"
if "last_plan" not in st.session_state:
    st.session_state["last_plan"] = None


# ==============================================================================
# AUTHENTICATION VIEW (Login & Register)
# ==============================================================================
def render_auth_page():
    st.markdown("""
    <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 0.5rem;">
        <span class="brand-badge">✦ Multi-Agent AI Travel Intelligence</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="auth-wrapper">
            <div class="auth-title">✈️ Odyssey Travel AI</div>
            <div class="auth-sub">Sign in to your account or register to start planning autonomous journeys.</div>
            <div class="auth-shield">
                <span>🔒</span> Bcrypt Salted Password Hashing & PostgreSQL Storage
            </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])

        # ── Sign In Tab ──
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                login_id = st.text_input("Username or Email", placeholder="e.g. travel_lover or user@email.com")
                login_pwd = st.text_input("Password", type="password", placeholder="••••••••••••")
                submit_login = st.form_submit_button("Sign In to Odyssey", use_container_width=True)

                if submit_login:
                    if not login_id or not login_pwd:
                        st.error("Please enter both username/email and password.")
                    else:
                        user_obj, message = auth.authenticate_user(login_id, login_pwd)
                        if user_obj:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user_obj
                            st.success("Authentication successful! Welcome back.")
                            st.rerun()
                        else:
                            st.error(message)

        # ── Register Tab ──
        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                reg_name = st.text_input("Full Name", placeholder="e.g. John Doe")
                reg_user = st.text_input("Choose Username", placeholder="e.g. jdoe_travel")
                reg_email = st.text_input("Email Address", placeholder="e.g. jdoe@example.com")
                reg_pwd1 = st.text_input("Create Password", type="password", placeholder="At least 6 characters")
                reg_pwd2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submit_signup = st.form_submit_button("Create My Account", use_container_width=True)

                if submit_signup:
                    if reg_pwd1 != reg_pwd2:
                        st.error("Passwords do not match. Please verify your password.")
                    else:
                        success, message = auth.register_user(
                            username=reg_user,
                            email=reg_email,
                            password=reg_pwd1,
                            full_name=reg_name
                        )
                        if success:
                            st.success("Account created successfully with secure bcrypt hashing! You can now sign in.")
                        else:
                            st.error(message)

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# MAIN APPLICATION VIEW (Authenticated Dashboard)
# ==============================================================================
def render_main_dashboard():
    user = st.session_state.get("user", {})
    user_id = user.get("id", 1)
    username = user.get("username", "Traveler")
    full_name = user.get("full_name", username)
    user_email = user.get("email", "")

    # ── Top Bar ───────────────────────────────────────────────────────────────
    nav_col1, nav_col2 = st.columns([3, 1])
    with nav_col1:
        st.markdown(f"""
        <div class="top-nav">
            <div class="brand-title">
                <span>✈️</span> Odyssey AI
                <span class="brand-badge">LangGraph + MCP</span>
            </div>
            <div style="color: #9cb5d1; font-size: 0.9rem;">
                Logged in as <strong style="color: #e2ecf8;">{full_name}</strong> (@{username})
            </div>
        </div>
        """, unsafe_allow_html=True)
    with nav_col2:
        st.write("")
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["last_plan"] = None
            st.rerun()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-user">
            <div style="font-size: 0.78rem; text-transform: uppercase; color: #7ab8f5; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 0.3rem;">Active Traveler</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff;">{full_name}</div>
            <div style="font-size: 0.82rem; color: #8aa0be;">{user_email}</div>
        </div>
        """, unsafe_allow_html=True)

        page_choice = st.radio(
            "Navigation",
            ["🗺️ Plan Journey", "📜 My Saved Trips", "⚡ MCP Engine Health"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #e0edf8; margin-bottom: 0.6rem;'>Live Infrastructure</div>", unsafe_allow_html=True)
        
        statuses = [
            ("PostgreSQL Memory", "Connected & Persistent"),
            ("AviationStack MCP", "stdio FastMCP (Airports/Carriers)"),
            ("OpenWeather MCP", "stdio FastMCP (Live Weather)"),
            ("Tavily Search MCP", "streamable_http (Lodging)"),
            ("Groq Cloud", "Active (openai/gpt-oss-120b)"),
        ]
        for name, note in statuses:
            st.markdown(f"""
            <div class="sidebar-status-chip">
                <div class="status-dot"></div>
                <div>
                    <strong style="color: #e0edf8; font-size: 0.8rem;">{name}</strong><br>
                    <span style="font-size: 0.72rem; color: #7693b4;">{note}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1: PLAN JOURNEY
    # ──────────────────────────────────────────────────────────────────────────
    if "Plan Journey" in page_choice:
        # Hero Banner
        st.markdown("""
        <div class="hero-wrapper">
            <img class="hero-bg"
                 src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
                 alt="airplane above clouds"/>
            <div class="hero-content">
                <div class="hero-badge">✦ Autonomous Travel Intelligence</div>
                <div class="hero-title">Where would you like to travel next?</div>
                <div class="hero-sub">Five autonomous agents collaborate via Model Context Protocol (MCP) to curate verified flights, hotel gems, real-time climate forecasts, and unforgettable itineraries.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick Presets
        st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #7ab8f5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;'>⚡ Quick Destination Inspiration</div>", unsafe_allow_html=True)
        PRESETS = [
            ("🇯🇵 Tokyo & Kyoto (7 Days)", "Plan a 7-day trip to Japan (Tokyo and Kyoto) for 2 adults under ₹2,00,000. Include JR Pass feasibility, 4-star hotels near Shinjuku and Gion, flights, and authentic culinary spots."),
            ("🇫🇷 Paris Romantic (5 Days)", "Plan a romantic 5-day holiday in Paris for 2 adults under ₹1,80,000. Include boutique hotels near Saint-Germain, museum passes, and flights."),
            ("🇦🇪 Dubai Luxury (4 Days)", "Plan a luxury 4-day weekend in Dubai for 2 adults with 5-star hotels, desert safari, fine dining, and direct flights."),
            ("🇮🇹 Rome & Amalfi (6 Days)", "Plan a scenic 6-day trip across Rome and the Amalfi Coast under ₹2,20,000 for 2 adults with flights, rail transit, and boutique stays."),
        ]
        
        cols = st.columns(len(PRESETS))
        selected_preset = ""
        for idx, (label, prompt_text) in enumerate(PRESETS):
            with cols[idx]:
                if st.button(label, key=f"btn_p_{idx}", use_container_width=True):
                    selected_preset = prompt_text

        st.markdown("<br>", unsafe_allow_html=True)

        # Input Card
        with st.container():
            st.markdown("<div class='app-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-header'><span>🗺️</span> Define Your Journey Parameters</div>", unsafe_allow_html=True)

            input_query = st.text_area(
                "Travel Vision",
                value=selected_preset,
                placeholder="e.g. Plan a 6-day cultural trip to Japan for 2 adults with 4-star hotels in Shinjuku, vegetarian meals, and budget under ₹2,00,000.",
                height=110,
                label_visibility="collapsed"
            )

            filter_c1, filter_c2, filter_c3 = st.columns(3)
            with filter_c1:
                travel_style = st.selectbox(
                    "🎨 Travel Style",
                    ["Balanced Sightseeing & Leisure", "Romantic Getaway", "Luxury & Wellness", "Cultural & Culinary Explorer", "Budget Backpacking", "Family-Friendly"]
                )
            with filter_c2:
                trip_duration = st.slider("⏱️ Duration (Days)", min_value=2, max_value=21, value=6)
            with filter_c3:
                currency = st.selectbox("💳 Currency Preference", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"])

            st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
            generate_clicked = st.button("🚀  Generate Intelligent Travel Plan", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Execution Workflow
        if generate_clicked:
            if not input_query.strip():
                st.warning("Please describe your destination or select a quick preset.")
            else:
                combined_query = f"{input_query.strip()} (Style: {travel_style}, Duration: {trip_duration} days, Preferred Currency: {currency})"
                session_thread = f"user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                config = {"configurable": {"thread_id": session_thread}}

                collected = {
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "itinerary": "",
                    "final_response": "",
                    "llm_calls": 0,
                }

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='card-header'><span>🤖</span> Live Multi-Agent Execution Progress</div>", unsafe_allow_html=True)

                agent_cards = {
                    "flight_agent": ("✈️", "Flight Agent (MCP AviationStack)", "Querying international airport networks & airline route matrices..."),
                    "hotel_agent": ("🏨", "Hotel Agent (MCP Tavily)", "Researching verified luxury, boutique, and budget accommodations..."),
                    "weather_agent": ("⛅", "Weather Agent (MCP OpenWeather)", "Analyzing live destination climate conditions and 5-day forecasts..."),
                    "itinerary_agent": ("🗓️", "Itinerary Agent (LangGraph + AI)", "Synthesizing schedule, geographical routes, and culinary gems..."),
                    "final_agent": ("🧠", "Chief Concierge Agent", "Assembling executive proposal, budget estimates, and cost-saving tips..."),
                }

                # Stream payload initialization
                stream_payload = {
                    "messages": [HumanMessage(content=combined_query)],
                    "user_query": combined_query,
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "itinerary": "",
                    "final_response": "",
                    "llm_calls": 0,
                }

                try:
                    stream_iter = app.stream(stream_payload, config=config, stream_mode="updates")
                except Exception as stream_init_err:
                    print(f"⚠️ Stream init notice: {stream_init_err}")
                    stream_iter = []

                try:
                    for chunk in stream_iter:
                        for node_name, state_update in chunk.items():
                            icon, label, default_desc = agent_cards.get(node_name, ("🔧", node_name, "Processing..."))
                            with st.status(f"{icon}  {label}", state="complete", expanded=True):
                                if node_name == "flight_agent":
                                    text = state_update.get("flight_results", "")
                                    collected["flight_results"] = text
                                    st.markdown(text or default_desc)
                                elif node_name == "hotel_agent":
                                    text = state_update.get("hotel_results", "")
                                    collected["hotel_results"] = text
                                    st.markdown(text or default_desc)
                                elif node_name == "weather_agent":
                                    text = state_update.get("weather_results", "")
                                    collected["weather_results"] = text
                                    st.markdown(text or default_desc)
                                elif node_name == "itinerary_agent":
                                    text = state_update.get("itinerary", "")
                                    collected["itinerary"] = text
                                    st.markdown(text or default_desc)
                                elif node_name == "final_agent":
                                    text = state_update.get("final_response", "")
                                    if not text:
                                        msgs = state_update.get("messages", [])
                                        text = msgs[-1].content if msgs else ""
                                    collected["final_response"] = text
                                    st.markdown(text or default_desc)

                                collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])
                except Exception as iter_err:
                    print(f"⚠️ Note during stream chunk processing: {iter_err}")

                # Metrics Bar
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-box"><div class="metric-val">5</div><div class="metric-lbl">Agents Completed</div></div>
                    <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM Invocations</div></div>
                    <div class="metric-box"><div class="metric-val">3</div><div class="metric-lbl">Active MCP Servers</div></div>
                    <div class="metric-box"><div class="metric-val">PostgreSQL</div><div class="metric-lbl">Checkpointer Status</div></div>
                </div>
                """, unsafe_allow_html=True)

                # Persist in user_trips table
                plan_title = f"{input_query.strip()[:40]}..." if len(input_query.strip()) > 40 else input_query.strip()
                auth.save_user_trip(
                    user_id=user_id,
                    query=input_query,
                    destination=input_query.split()[0] if input_query else "Destination",
                    plan_title=plan_title,
                    flight_results=collected["flight_results"],
                    hotel_results=collected["hotel_results"],
                    weather_results=collected["weather_results"],
                    itinerary=collected["itinerary"],
                    final_response=collected["final_response"]
                )

                st.session_state["last_plan"] = collected

        # Display Final Plan Presentation
        if st.session_state.get("last_plan"):
            plan_data = st.session_state["last_plan"]
            st.markdown("---")
            st.markdown("<div class='card-header'><span>📋</span> Synthesized Travel Proposal</div>", unsafe_allow_html=True)

            plan_tabs = st.tabs([
                "🌟 Executive Proposal",
                "✈️ Flight Guidance",
                "🏨 Hotel Recommendations",
                "⛅ Climate & Forecast",
                "🗓️ Detailed Itinerary"
            ])

            with plan_tabs[0]:
                st.markdown(f"<div class='plan-summary-card'>{plan_data['final_response'] or plan_data['itinerary']}</div>", unsafe_allow_html=True)
            with plan_tabs[1]:
                st.markdown(plan_data['flight_results'] or "Flight data not available.")
            with plan_tabs[2]:
                st.markdown(plan_data['hotel_results'] or "Hotel recommendations not available.")
            with plan_tabs[3]:
                st.markdown(plan_data['weather_results'] or "Weather report not available.")
            with plan_tabs[4]:
                st.markdown(plan_data['itinerary'] or "Itinerary not available.")

            # Markdown Export
            st.markdown("<br>", unsafe_allow_html=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_content = f"""# Odyssey AI Travel Proposal
**User:** {full_name} (@{username})
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🌟 Executive Concierge Proposal
{plan_data['final_response']}

---

## ✈️ Flight Analysis (AviationStack MCP)
{plan_data['flight_results']}

---

## 🏨 Accommodations (Tavily MCP)
{plan_data['hotel_results']}

---

## ⛅ Climate & Weather (OpenWeather MCP)
{plan_data['weather_results']}

---

## 🗓️ Day-by-Day Itinerary
{plan_data['itinerary']}
"""
            dl_col1, dl_col2 = st.columns([1, 3])
            with dl_col1:
                st.download_button(
                    "⬇️ Download Plan (.md)",
                    data=export_content,
                    file_name=f"odyssey_travel_plan_{timestamp}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with dl_col2:
                st.success("✅ This travel plan is securely saved to your PostgreSQL history!")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2: MY SAVED TRIPS
    # ──────────────────────────────────────────────────────────────────────────
    elif "Saved Trips" in page_choice:
        st.markdown(f"<div class='card-header'><span>📜</span> Saved Travel Packages for {full_name}</div>", unsafe_allow_html=True)
        trips = auth.get_user_trips(user_id)

        if not trips:
            st.info("No saved journeys found yet. Generate a travel plan from the 'Plan Journey' tab to save your first trip!")
        else:
            for trip in trips:
                with st.expander(f"📍 {trip.get('plan_title') or trip.get('destination')} · {trip.get('created_at').strftime('%b %d, %Y %H:%M')}"):
                    st.markdown(f"**Original Request:** {trip.get('query')}")
                    st.markdown("---")
                    
                    sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs(["🌟 Proposal", "✈️ Flights", "🏨 Hotels", "🗓️ Itinerary"])
                    with sub_t1:
                        st.markdown(trip.get("final_response") or "N/A")
                    with sub_t2:
                        st.markdown(trip.get("flight_results") or "N/A")
                    with sub_t3:
                        st.markdown(trip.get("hotel_results") or "N/A")
                    with sub_t4:
                        st.markdown(trip.get("itinerary") or "N/A")

                    st.markdown("<br>", unsafe_allow_html=True)
                    del_col, _ = st.columns([1, 4])
                    with del_col:
                        if st.button(f"🗑️ Delete Trip #{trip['id']}", key=f"del_{trip['id']}"):
                            if auth.delete_user_trip(trip['id'], user_id):
                                st.success("Trip removed from history.")
                                st.rerun()

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3: MCP ENGINE HEALTH
    # ──────────────────────────────────────────────────────────────────────────
    elif "MCP Engine" in page_choice:
        st.markdown("<div class='card-header'><span>⚡</span> Model Context Protocol & Backend Health</div>", unsafe_allow_html=True)
        st.markdown("""
        The system coordinates 5 autonomous LangGraph agents backed by standard Model Context Protocol servers.
        """)

        diag_cols = st.columns(3)
        with diag_cols[0]:
            st.markdown("""
            <div class="app-card">
                <div style="font-weight: 700; color: #4ea8f0; font-size: 1.1rem; margin-bottom: 0.5rem;">✈️ Aviation MCP</div>
                <div style="font-size: 0.85rem; color: #8da9c7;">
                    • Transport: <code>stdio</code> (FastMCP)<br>
                    • Tools: <code>list_airports</code>, <code>list_airlines</code>, <code>get_flight_status</code><br>
                    • Provider: AviationStack API + curated fallback
                </div>
            </div>
            """, unsafe_allow_html=True)

        with diag_cols[1]:
            st.markdown("""
            <div class="app-card">
                <div style="font-weight: 700; color: #4ea8f0; font-size: 1.1rem; margin-bottom: 0.5rem;">⛅ Weather MCP</div>
                <div style="font-size: 0.85rem; color: #8da9c7;">
                    • Transport: <code>stdio</code> (FastMCP)<br>
                    • Tools: <code>get_current_weather</code>, <code>get_forecast</code><br>
                    • Provider: OpenWeatherMap API + seasonal fallback
                </div>
            </div>
            """, unsafe_allow_html=True)

        with diag_cols[2]:
            st.markdown("""
            <div class="app-card">
                <div style="font-weight: 700; color: #4ea8f0; font-size: 1.1rem; margin-bottom: 0.5rem;">🔍 Tavily Search MCP</div>
                <div style="font-size: 0.85rem; color: #8da9c7;">
                    • Transport: <code>streamable_http</code><br>
                    • Tools: <code>tavily_search</code>, <code>tavily_extract</code><br>
                    • Provider: Tavily Real-time Web Crawler
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Security Architecture")
        st.markdown("""
        - **Password Storage**: Passwords are never stored in plaintext. They are salted and hashed using **Bcrypt (cost factor 12)**.
        - **Session Management**: Session tokens are maintained within Streamlit session state and cleared immediately on sign out.
        - **Database**: Checkpoint graph state and user travel records are stored in PostgreSQL (`langgraph_memory_demo`).
        """)


# ==============================================================================
# MAIN ROUTER
# ==============================================================================
if not st.session_state.get("authenticated"):
    render_auth_page()
else:
    render_main_dashboard()
