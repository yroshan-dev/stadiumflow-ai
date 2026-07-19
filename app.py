"""
StadiumFlow AI
v0.2.1 – Football Fan Ticket Assistant

A Streamlit prototype for football match fans.

Core flow:
1. Fan enters a ticket number.
2. App loads ticket details from default CSV data or reviewer-uploaded CSV files.
3. App filters facilities based on the fan's ticket zone.
4. MyZone AI answers match-day questions using ticket-specific context.

Security note:
- No personal data is stored.
- Default ticket data is mock data for prototype demonstration.
- Reviewer-uploaded CSV data is only used during the active Streamlit session.
- Gemini API key should be stored in Streamlit Secrets, not committed to GitHub.
"""

from __future__ import annotations

import os
import re
from typing import Optional

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="StadiumFlow AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------

CUSTOM_CSS = """
<style>
    .main {
        background: #0b0f17;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero-card {
        background: linear-gradient(135deg, #111827 0%, #1e3a8a 55%, #2563eb 100%);
        padding: 2.2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 18px 45px rgba(37, 99, 235, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 850;
        margin-bottom: 0.4rem;
        letter-spacing: -0.04em;
    }

    .hero-subtitle {
        font-size: 1.12rem;
        color: #dbeafe;
        max-width: 900px;
        line-height: 1.65;
    }

    .mode-pill {
        display: inline-block;
        background: #dbeafe;
        color: #1e3a8a;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .result-card {
        background: #111827;
        border: 1px solid #263244;
        border-radius: 20px;
        padding: 1.35rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.25);
    }

    .result-card h3 {
        color: #f8fafc;
        margin-bottom: 0.4rem;
    }

    .result-card p {
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.55;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .reason-box {
        background: #0f172a;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .stButton > button {
        border-radius: 12px;
        border: 0;
        background: #2563eb;
        color: white;
        font-weight: 750;
        padding: 0.7rem 1.2rem;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }

    div[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }

    div[data-testid="stSidebar"] * {
        color: white;
    }

    .footer-note {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 2rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Required data schema
# ---------------------------------------------------------------------

REQUIRED_TICKET_COLUMNS = [
    "ticket_id",
    "fan_name",
    "match",
    "home_team",
    "away_team",
    "kickoff_time",
    "gate",
    "zone",
    "stand",
    "block",
    "row",
    "seat",
    "preferred_language",
]

REQUIRED_FACILITY_COLUMNS = [
    "facility_id",
    "type",
    "name",
    "zone",
    "stand",
    "near_block",
    "level",
    "distance_minutes",
    "status",
]


# ---------------------------------------------------------------------
# Data loading and validation
# ---------------------------------------------------------------------

@st.cache_data
def load_default_tickets() -> pd.DataFrame:
    """Load default mock football match ticket data."""
    return pd.read_csv("data/tickets.csv")


@st.cache_data
def load_default_facilities() -> pd.DataFrame:
    """Load default mock stadium facility data."""
    return pd.read_csv("data/facilities.csv")


def validate_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> tuple[bool, list[str]]:
    """Check whether uploaded/default data has the required columns."""
    missing_columns = [
        column for column in required_columns if column not in dataframe.columns
    ]

    if missing_columns:
        return False, missing_columns

    return True, []


def load_demo_or_uploaded_data() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Load default sample data or reviewer-uploaded CSV files.

    Reviewers can upload their own football match tickets and facilities without
    editing the GitHub repository.
    """
    st.sidebar.markdown("### Optional Reviewer Data Upload")

    with st.sidebar.expander("Required CSV format", expanded=False):
        st.markdown("**tickets.csv columns**")
        st.code(", ".join(REQUIRED_TICKET_COLUMNS))

        st.markdown("**facilities.csv columns**")
        st.code(", ".join(REQUIRED_FACILITY_COLUMNS))

    uploaded_tickets = st.sidebar.file_uploader(
        "Upload custom tickets.csv",
        type=["csv"],
        help="Optional. Must follow the same columns as the sample tickets.csv file.",
    )

    uploaded_facilities = st.sidebar.file_uploader(
        "Upload custom facilities.csv",
        type=["csv"],
        help="Optional. Must follow the same columns as the sample facilities.csv file.",
    )

    if uploaded_tickets is not None or uploaded_facilities is not None:
        if uploaded_tickets is None or uploaded_facilities is None:
            st.sidebar.warning("Upload both CSV files to use custom reviewer data.")
            tickets_df = load_default_tickets()
            facilities_df = load_default_facilities()
            return tickets_df, facilities_df, "sample"

        tickets_df = pd.read_csv(uploaded_tickets)
        facilities_df = pd.read_csv(uploaded_facilities)

        tickets_valid, missing_ticket_columns = validate_columns(
            tickets_df,
            REQUIRED_TICKET_COLUMNS,
        )

        facilities_valid, missing_facility_columns = validate_columns(
            facilities_df,
            REQUIRED_FACILITY_COLUMNS,
        )

        if not tickets_valid:
            st.sidebar.error(
                "Uploaded tickets.csv is missing: "
                + ", ".join(missing_ticket_columns)
            )
            tickets_df = load_default_tickets()
            facilities_df = load_default_facilities()
            return tickets_df, facilities_df, "sample"

        if not facilities_valid:
            st.sidebar.error(
                "Uploaded facilities.csv is missing: "
                + ", ".join(missing_facility_columns)
            )
            tickets_df = load_default_tickets()
            facilities_df = load_default_facilities()
            return tickets_df, facilities_df, "sample"

        st.sidebar.success("Using uploaded reviewer data.")
        return tickets_df, facilities_df, "uploaded"

    tickets_df = load_default_tickets()
    facilities_df = load_default_facilities()

    st.sidebar.info("Using built-in sample data.")
    return tickets_df, facilities_df, "sample"


def get_ticket(ticket_id: str, tickets_df: pd.DataFrame) -> Optional[dict]:
    """Return a ticket record if the ticket number exists."""
    if not ticket_id:
        return None

    matched_ticket = tickets_df[
        tickets_df["ticket_id"].astype(str).str.upper() == ticket_id.strip().upper()
    ]

    if matched_ticket.empty:
        return None

    return matched_ticket.iloc[0].to_dict()


def get_zone_facilities(zone: str, facilities_df: pd.DataFrame) -> pd.DataFrame:
    """Return facilities that belong to the fan's ticket zone."""
    return facilities_df[facilities_df["zone"] == zone].copy()


# ---------------------------------------------------------------------
# GenAI helpers
# ---------------------------------------------------------------------

def get_gemini_api_key() -> Optional[str]:
    """
    Read Gemini API key from Streamlit Secrets or environment variable.

    Streamlit Cloud secret format:
    GEMINI_API_KEY = "your_api_key_here"
    """
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            return str(api_key).strip()
    except Exception:
        pass

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key.strip()

    return None


def build_fan_context(ticket: dict, zone_facilities: pd.DataFrame) -> str:
    """Create grounded context for the GenAI assistant."""
    facilities_text = "\n".join(
        [
            (
                f"- {row['type']}: {row['name']} near Block {row['near_block']}, "
                f"{row['level']}, {row['distance_minutes']} minutes away, "
                f"status: {row['status']}"
            )
            for _, row in zone_facilities.iterrows()
        ]
    )

    if not facilities_text:
        facilities_text = "No facilities are listed for this zone."

    return f"""
You are MyZone AI, a GenAI-powered football match-day assistant.

Fan ticket context:
- Fan name: {ticket["fan_name"]}
- Match: {ticket["match"]}
- Home team: {ticket["home_team"]}
- Away team: {ticket["away_team"]}
- Kickoff time: {ticket["kickoff_time"]}
- Recommended gate: {ticket["gate"]}
- Zone: {ticket["zone"]}
- Stand: {ticket["stand"]}
- Block: {ticket["block"]}
- Row: {ticket["row"]}
- Seat: {ticket["seat"]}
- Suggested language: {ticket["preferred_language"]}

Nearby facilities in this fan's zone:
{facilities_text}

Rules for your answer:
- Give short, clear, match-day guidance.
- Use only the fan's ticket zone unless the fan asks for wider stadium information.
- Mention the nearest relevant facility when possible.
- For emergencies, mention medical help, steward/security support, and nearest exit.
- Do not invent facilities, gates, exits, or policies.
- If information is missing, say what is missing and give the safest next step.
"""


def generate_fallback_answer(
    question: str,
    ticket: dict,
    zone_facilities: pd.DataFrame,
) -> str:
    """
    Safe fallback when Gemini is not configured.

    This keeps the demo usable without exposing API keys.
    Whole-word matching avoids mistakes such as matching 'eat' inside 'seat'.
    """
    question_lower = question.lower()

    def has_any_word(words: list[str]) -> bool:
        """Return True if any whole word or phrase appears in the question."""
        for word in words:
            pattern = r"\b" + re.escape(word.lower()) + r"\b"
            if re.search(pattern, question_lower):
                return True
        return False

    def nearest_facility(facility_type: str) -> Optional[pd.Series]:
        matches = zone_facilities[
            zone_facilities["type"].str.lower() == facility_type.lower()
        ]

        if matches.empty:
            return None

        return matches.sort_values("distance_minutes").iloc[0]

    if has_any_word(["seat", "seating", "gate", "block", "row"]):
        return (
            f"Use {ticket['gate']} and go to {ticket['stand']}, Block {ticket['block']}, "
            f"Row {ticket['row']}, Seat {ticket['seat']}."
        )

    if has_any_word(["toilet", "bathroom", "restroom", "washroom"]):
        item = nearest_facility("Toilet")
        if item is not None:
            return (
                f"The nearest toilet is {item['name']} near Block {item['near_block']}. "
                f"It is about {item['distance_minutes']} minutes from your zone."
            )

    if has_any_word(["food", "snack", "eat", "meal", "stall"]):
        item = nearest_facility("Food")
        if item is not None:
            return (
                f"The nearest food stall is {item['name']} near Block {item['near_block']}. "
                f"It is about {item['distance_minutes']} minutes away."
            )

    if has_any_word(["water", "drink", "refill"]):
        item = nearest_facility("Water")
        if item is not None:
            return (
                f"The nearest water point is {item['name']} near Block {item['near_block']}. "
                f"It is about {item['distance_minutes']} minutes away."
            )

    if has_any_word(["medical", "hurt", "injury", "emergency", "doctor", "first aid"]):
        medical = nearest_facility("Medical")
        security = nearest_facility("Security")
        exit_point = nearest_facility("Exit")

        parts = []

        if medical is not None:
            parts.append(f"Go to {medical['name']} near Block {medical['near_block']}.")

        if security is not None:
            parts.append(
                f"Ask for help at {security['name']} near Block {security['near_block']}."
            )

        if exit_point is not None:
            parts.append(
                f"The nearest emergency exit is {exit_point['name']} near Block {exit_point['near_block']}."
            )

        return " ".join(parts) if parts else "Ask the nearest steward for immediate help."

    if has_any_word(["exit", "leave", "leaving"]):
        item = nearest_facility("Exit")
        if item is not None:
            return (
                f"The nearest exit is {item['name']} near Block {item['near_block']}. "
                f"It is about {item['distance_minutes']} minutes away."
            )

    return (
        f"You are in {ticket['zone']} at {ticket['stand']}, Block {ticket['block']}. "
        "Ask about your seat, toilets, food, water, medical help, or exits."
    )


def generate_myzone_ai_answer(
    question: str,
    ticket: dict,
    zone_facilities: pd.DataFrame,
) -> tuple[str, bool]:
    """
    Generate a MyZone AI answer.

    Returns:
        answer: The response text.
        used_genai: True when Gemini generated the response, False for fallback.
    """
    api_key = get_gemini_api_key()

    if not api_key:
        st.sidebar.error("Gemini API key not found.")
        st.sidebar.caption("Add GEMINI_API_KEY in Streamlit Secrets, then reboot the app.")
        return generate_fallback_answer(question, ticket, zone_facilities), False

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
{build_fan_context(ticket, zone_facilities)}

Fan question:
{question}
"""

        response = model.generate_content(prompt)

        if not response.text:
            st.sidebar.error("Gemini returned an empty response.")
            return generate_fallback_answer(question, ticket, zone_facilities), False

        return response.text.strip(), True

    except Exception as error:
        st.sidebar.error("Gemini call failed.")
        st.sidebar.code(str(error))
        return generate_fallback_answer(question, ticket, zone_facilities), False


# ---------------------------------------------------------------------
# UI rendering helpers
# ---------------------------------------------------------------------

def render_hero() -> None:
    """Render the product hero section."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">⚽ StadiumFlow AI</div>
            <div class="hero-subtitle">
                A GenAI-powered football match assistant for ticketed fans.
                Enter a ticket number to get personalised seat guidance, nearby toilets,
                food stalls, water points, medical help, steward support, emergency exits,
                and match-day assistance based on your exact stadium zone.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reason(title: str, points: list[str]) -> None:
    """Render a short explanation box for reviewers."""
    joined_points = "<br>".join([f"• {point}" for point in points])

    st.markdown(
        f"""
        <div class="reason-box">
            <b>{title}</b><br>
            {joined_points}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render sidebar information for reviewers."""
    st.sidebar.title("StadiumFlow AI")
    st.sidebar.caption("v0.2.1 – Football Fan Ticket Assistant")

    st.sidebar.divider()

    st.sidebar.markdown("### Demo Tickets")
    st.sidebar.code("WC26-FINAL-EAST-128-22-14")
    st.sidebar.code("WC26-FINAL-WEST-139-18-08")
    st.sidebar.code("WC26-FINAL-NORTH-203-11-21")

    st.sidebar.divider()

    st.sidebar.markdown("### Scope")
    st.sidebar.markdown(
        """
        Built only for football match fans.

        The app uses ticket data to personalise:
        - Gate and seat guidance
        - Zone-specific facilities
        - Emergency help
        - GenAI match-day support
        """
    )

    st.sidebar.divider()


def render_data_status(
    data_source: str,
    tickets_df: pd.DataFrame,
    facilities_df: pd.DataFrame,
) -> None:
    """Show which data source is currently active."""
    if data_source == "uploaded":
        st.success("Reviewer-uploaded CSV data is active for this session.")
    else:
        st.info("Using built-in sample football ticket and facility data.")

    st.markdown(
        f"""
        <p class="small-note">
            Current loaded data: <b>{len(tickets_df)}</b> tickets and
            <b>{len(facilities_df)}</b> facilities.
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_ticket_login(tickets_df: pd.DataFrame) -> None:
    """Render ticket login screen."""
    st.markdown(
        '<span class="mode-pill">Football Fan Ticket Login</span>',
        unsafe_allow_html=True,
    )

    st.header("Enter Your Football Match Ticket")

    st.markdown(
        """
        <p class="small-note">
            This prototype simulates ticket login using football ticket data.
            Reviewers may use the built-in sample tickets or upload their own CSV files from the sidebar.
        </p>
        """,
        unsafe_allow_html=True,
    )

    demo_ticket = "WC26-FINAL-EAST-128-22-14"

    with st.form("ticket_login_form"):
        ticket_id = st.text_input(
            "Ticket number",
            placeholder=demo_ticket,
        )

        submitted = st.form_submit_button("Login with Ticket")

    if submitted:
        ticket = get_ticket(ticket_id, tickets_df)

        if ticket is None:
            st.error(
                "Invalid ticket number. Try a demo ticket or check the uploaded tickets.csv file."
            )
        else:
            st.session_state.ticket = ticket
            st.rerun()

    st.info(f"Fast demo: use ticket number `{demo_ticket}`.")


def render_match_dashboard(ticket: dict) -> None:
    """Render personalised football match details."""
    st.markdown(
        f"""
        <div class="result-card">
            <h3>⚽ {ticket["match"]}</h3>
            <p>
                <b>Kickoff:</b> {ticket["kickoff_time"]}<br>
                <b>Recommended gate:</b> {ticket["gate"]}<br>
                <b>Zone:</b> {ticket["zone"]}<br>
                <b>Seat:</b> {ticket["stand"]}, Block {ticket["block"]}, Row {ticket["row"]}, Seat {ticket["seat"]}<br>
                <b>Suggested language:</b> {ticket["preferred_language"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    cols[0].metric("Gate", ticket["gate"])
    cols[1].metric("Stand", ticket["stand"])
    cols[2].metric("Block", ticket["block"])
    cols[3].metric("Seat", f"Row {ticket['row']} / Seat {ticket['seat']}")


def render_zone_facilities(ticket: dict, zone_facilities: pd.DataFrame) -> None:
    """Render ticket-zone-specific facilities."""
    st.subheader("My Zone Facilities")

    st.markdown(
        f"""
        <p class="small-note">
            Showing only facilities near <b>{ticket["zone"]}</b> and <b>{ticket["stand"]}</b>.
            The fan does not need the whole stadium map during a live football match.
        </p>
        """,
        unsafe_allow_html=True,
    )

    display_columns = [
        "type",
        "name",
        "near_block",
        "level",
        "distance_minutes",
        "status",
    ]

    if zone_facilities.empty:
        st.warning("No facilities are listed for this ticket zone.")
    else:
        st.dataframe(
            zone_facilities[display_columns],
            use_container_width=True,
            hide_index=True,
        )

    render_reason(
        "Why this is personalised",
        [
            f"The ticket places the fan in {ticket['zone']}.",
            "The app filters facilities using the fan's zone instead of showing the full stadium.",
            "The same ticket context is passed to MyZone AI for grounded answers.",
        ],
    )


def render_emergency_help(zone_facilities: pd.DataFrame) -> None:
    """Render emergency support cards for the fan's zone."""
    st.subheader("Emergency Help")

    medical = zone_facilities[zone_facilities["type"] == "Medical"]
    security = zone_facilities[zone_facilities["type"] == "Security"]
    exit_point = zone_facilities[zone_facilities["type"] == "Exit"]

    e1, e2, e3 = st.columns(3)

    with e1:
        if not medical.empty:
            item = medical.iloc[0]
            st.error(f"Medical: {item['name']} near Block {item['near_block']}")
        else:
            st.error("Medical: Ask nearest steward")

    with e2:
        if not security.empty:
            item = security.iloc[0]
            st.warning(f"Steward: {item['name']} near Block {item['near_block']}")
        else:
            st.warning("Steward: Ask visible stadium staff")

    with e3:
        if not exit_point.empty:
            item = exit_point.iloc[0]
            st.info(f"Exit: {item['name']} near Block {item['near_block']}")
        else:
            st.info("Exit: Follow emergency signage")


def render_myzone_ai(ticket: dict, zone_facilities: pd.DataFrame) -> None:
    """Render GenAI assistant section."""
    st.subheader("Ask MyZone AI")

    st.markdown(
        """
        <p class="small-note">
            MyZone AI uses the fan's ticket, seat, gate, zone, and nearby facilities as context.
            It answers football match-day questions without exposing the full stadium dataset.
        </p>
        """,
        unsafe_allow_html=True,
    )

    example_questions = [
        "Where is the nearest toilet?",
        "How do I reach my seat?",
        "Where can I get water?",
        "Someone needs medical help near me. What should I do?",
        "Where is the nearest exit after the match?",
    ]

    selected_question = st.selectbox(
        "Try a sample question",
        ["Write my own question"] + example_questions,
    )

    default_question = "" if selected_question == "Write my own question" else selected_question

    user_question = st.text_area(
        "Your question",
        value=default_question,
        placeholder="Example: Where is the nearest toilet?",
        height=100,
    )

    if st.button("Ask MyZone AI"):
        if not user_question.strip():
            st.error("Please enter a question.")
            return

        answer, used_genai = generate_myzone_ai_answer(
            question=user_question,
            ticket=ticket,
            zone_facilities=zone_facilities,
        )

        if used_genai:
            st.success(answer)
            st.caption("Generated using Gemini with ticket-zone context.")
        else:
            st.warning(answer)
            st.caption(
                "Fallback response shown because Gemini API key is not configured or the GenAI call failed."
            )


def render_app(
    tickets_df: pd.DataFrame,
    facilities_df: pd.DataFrame,
    data_source: str,
) -> None:
    """Render the main app flow."""
    if "ticket" not in st.session_state:
        st.session_state.ticket = None

    render_hero()
    render_data_status(data_source, tickets_df, facilities_df)

    if st.session_state.ticket is None:
        render_ticket_login(tickets_df)
        return

    ticket = st.session_state.ticket
    zone_facilities = get_zone_facilities(ticket["zone"], facilities_df)

    top_left, top_right = st.columns([3, 1])

    with top_left:
        st.markdown(
            '<span class="mode-pill">My Match Assistant</span>',
            unsafe_allow_html=True,
        )
        st.header(f"Welcome, {ticket['fan_name']}")

    with top_right:
        if st.button("Logout"):
            st.session_state.ticket = None
            st.rerun()

    render_match_dashboard(ticket)
    render_zone_facilities(ticket, zone_facilities)
    render_emergency_help(zone_facilities)
    render_myzone_ai(ticket, zone_facilities)

    st.markdown(
        """
        <div class="footer-note">
            Built with Python and Streamlit. This prototype uses football ticket and facility data,
            avoids storing personal data, and demonstrates ticket-aware GenAI support for football match fans.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------

try:
    render_sidebar()

    tickets, facilities, active_data_source = load_demo_or_uploaded_data()

    render_app(tickets, facilities, active_data_source)

except FileNotFoundError as missing_file_error:
    st.error("Required data file is missing.")
    st.code(str(missing_file_error))
    st.info("Check that data/tickets.csv and data/facilities.csv exist in the repo.")

except Exception as app_error:
    st.error("Something went wrong while loading StadiumFlow AI.")
    st.code(str(app_error))
