import pandas as pd
import streamlit as st

from stadium_engine import (
    generate_fan_guidance,
    generate_volunteer_brief,
    rank_zones,
)


st.set_page_config(
    page_title="StadiumFlow AI",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded",
)


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

    .scenario-box {
        background: #111827;
        border: 1px solid #263244;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #cbd5e1;
    }

    .risk-low {
        background: #064e3b;
        color: #d1fae5;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
    }

    .risk-medium {
        background: #78350f;
        color: #fef3c7;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
    }

    .risk-high {
        background: #7c2d12;
        color: #ffedd5;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
    }

    .risk-critical {
        background: #7f1d1d;
        color: #fee2e2;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 800;
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

    div[data-testid="stSidebar"] .stRadio label {
        color: white;
    }

    .footer-note {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 2rem;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.55;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


FAN_SCENARIOS = {
    "Custom scenario": {
        "user_type": "General fan",
        "location": "",
        "need": "",
        "language": "English",
    },
    "Post-match exit surge": {
        "user_type": "General fan",
        "location": "Exit Tunnel near Gate C",
        "need": "I need the safest exit after the match because the main exit is crowded.",
        "language": "Simple English",
    },
    "Family looking for food": {
        "user_type": "Family with children",
        "location": "North Stand",
        "need": "We need a less crowded food area and a safe route with children.",
        "language": "Simple English",
    },
    "International visitor needs transport": {
        "user_type": "International visitor",
        "location": "Gate B",
        "need": "I need help finding transport after the match.",
        "language": "English",
    },
    "Medical help near seating area": {
        "user_type": "First-time visitor",
        "location": "Section 214",
        "need": "Someone nearby needs medical help.",
        "language": "Simple English",
    },
}

ACCESSIBILITY_SCENARIOS = {
    "Custom scenario": {
        "visitor_need": "Wheelchair access",
        "location": "",
        "destination": "",
        "crowd_condition": "Normal",
    },
    "Wheelchair route to seating": {
        "visitor_need": "Wheelchair access",
        "location": "Gate A",
        "destination": "Accessible seating area near Block 102",
        "crowd_condition": "Busy",
    },
    "Elderly visitor exit support": {
        "visitor_need": "Elderly support",
        "location": "South Stand",
        "destination": "Nearest calm exit",
        "crowd_condition": "High",
    },
    "Low vision visitor guidance": {
        "visitor_need": "Low vision support",
        "location": "Food Zone 1",
        "destination": "Information desk",
        "crowd_condition": "Busy",
    },
    "Lost child support": {
        "visitor_need": "Family with children",
        "location": "Parking Area",
        "destination": "Lost and found support desk",
        "crowd_condition": "Critical",
    },
}

VOLUNTEER_SCENARIOS = {
    "Custom scenario": {
        "zone": "",
        "issue_type": "Crowd buildup",
        "risk": "Low",
    },
    "Gate crowd buildup": {
        "zone": "Gate B",
        "issue_type": "Crowd buildup",
        "risk": "High",
    },
    "Lost fan near food zone": {
        "zone": "Food Zone 1",
        "issue_type": "Lost fan",
        "risk": "Medium",
    },
    "Accessibility request near exit": {
        "zone": "Exit Tunnel",
        "issue_type": "Accessibility request",
        "risk": "High",
    },
    "Medical support in stand": {
        "zone": "North Stand",
        "issue_type": "Medical support",
        "risk": "Critical",
    },
}


def render_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">🏟️ StadiumFlow AI</div>
            <div class="hero-subtitle">
                A GenAI-enabled stadium operations and fan-support assistant for large tournaments.
                It helps fans, volunteers, organizers, and venue staff with crowd awareness,
                accessibility support, multilingual-style guidance, and real-time decision support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_class(risk):
    return {
        "Low": "risk-low",
        "Medium": "risk-medium",
        "High": "risk-high",
        "Critical": "risk-critical",
    }.get(risk, "risk-low")


def render_reason(title, points):
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


render_hero()

st.sidebar.title("Control Center")
st.sidebar.caption("Choose the assistant workflow.")

mode = st.sidebar.radio(
    "Assistant Mode",
    [
        "Fan Assistant",
        "Crowd Intelligence Dashboard",
        "Volunteer Briefing Generator",
        "Accessibility Support",
    ],
)

st.sidebar.divider()
st.sidebar.markdown("### Live Prototype")
st.sidebar.markdown(
    """
Designed for stadium staff, volunteers, and fans during high-pressure tournament operations.
"""
)

if mode == "Fan Assistant":
    st.markdown('<span class="mode-pill">Fan Experience</span>', unsafe_allow_html=True)
    st.header("Fan Assistant")

    st.markdown(
        '<p class="small-note">Generate short, safe, context-aware guidance for fans inside or around the stadium.</p>',
        unsafe_allow_html=True,
    )

    selected_scenario = st.selectbox(
        "Quick test scenario",
        list(FAN_SCENARIOS.keys()),
        help="Use a sample scenario so reviewers can test the assistant quickly.",
    )

    scenario = FAN_SCENARIOS[selected_scenario]

    if selected_scenario != "Custom scenario":
        st.markdown(
            f"""
            <div class="scenario-box">
                Sample loaded: <b>{selected_scenario}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    left, right = st.columns([1, 1])

    with left:
        user_type = st.selectbox(
            "Fan type",
            [
                "General fan",
                "Family with children",
                "Elderly visitor",
                "International visitor",
                "First-time visitor",
            ],
            index=[
                "General fan",
                "Family with children",
                "Elderly visitor",
                "International visitor",
                "First-time visitor",
            ].index(scenario["user_type"]),
        )

        location = st.text_input(
            "Current location",
            value=scenario["location"],
            placeholder="Example: Gate C, North Stand, Food Zone 2",
        )

    with right:
        language = st.selectbox(
            "Guidance style",
            [
                "English",
                "Simple English",
                "Hindi-style English",
                "Spanish-style English",
            ],
            index=[
                "English",
                "Simple English",
                "Hindi-style English",
                "Spanish-style English",
            ].index(scenario["language"]),
        )

        need = st.text_area(
            "What does the fan need?",
            value=scenario["need"],
            placeholder="Example: I need the safest exit after the match.",
            height=120,
        )

    if st.button("Generate fan guidance"):
        if not location.strip() or not need.strip():
            st.error("Please enter both location and fan need.")
        else:
            guidance = generate_fan_guidance(user_type, location, need, language)
            st.success(guidance)

            render_reason(
                "Why this recommendation?",
                [
                    f"The user is classified as: {user_type}.",
                    f"The current location is: {location}.",
                    f"The request is interpreted as: {need}.",
                    f"The response style is adapted for: {language}.",
                ],
            )

elif mode == "Crowd Intelligence Dashboard":
    st.markdown('<span class="mode-pill">Operations Intelligence</span>', unsafe_allow_html=True)
    st.header("Crowd Intelligence Dashboard")

    st.markdown(
        '<p class="small-note">Enter live conditions for key stadium zones. The assistant ranks zones by operational risk.</p>',
        unsafe_allow_html=True,
    )

    scenario_mode = st.selectbox(
        "Crowd scenario",
        ["Balanced crowd", "Match entry rush", "Halftime food crowd", "Post-match exit surge"],
        help="Preset examples make the operational dashboard easier to test.",
    )

    if scenario_mode == "Match entry rush":
        default_zones = [
            {"zone": "Gate A", "crowd_level": 5, "wait_time": 35, "incident_count": 2},
            {"zone": "Gate B", "crowd_level": 4, "wait_time": 25, "incident_count": 1},
            {"zone": "Food Zone 1", "crowd_level": 2, "wait_time": 8, "incident_count": 0},
            {"zone": "Parking Area", "crowd_level": 4, "wait_time": 22, "incident_count": 1},
            {"zone": "Exit Tunnel", "crowd_level": 2, "wait_time": 5, "incident_count": 0},
        ]
    elif scenario_mode == "Halftime food crowd":
        default_zones = [
            {"zone": "Gate A", "crowd_level": 2, "wait_time": 5, "incident_count": 0},
            {"zone": "Gate B", "crowd_level": 2, "wait_time": 5, "incident_count": 0},
            {"zone": "Food Zone 1", "crowd_level": 5, "wait_time": 30, "incident_count": 2},
            {"zone": "Parking Area", "crowd_level": 1, "wait_time": 2, "incident_count": 0},
            {"zone": "Exit Tunnel", "crowd_level": 3, "wait_time": 8, "incident_count": 0},
        ]
    elif scenario_mode == "Post-match exit surge":
        default_zones = [
            {"zone": "Gate A", "crowd_level": 4, "wait_time": 20, "incident_count": 1},
            {"zone": "Gate B", "crowd_level": 5, "wait_time": 40, "incident_count": 3},
            {"zone": "Food Zone 1", "crowd_level": 2, "wait_time": 5, "incident_count": 0},
            {"zone": "Parking Area", "crowd_level": 5, "wait_time": 45, "incident_count": 2},
            {"zone": "Exit Tunnel", "crowd_level": 5, "wait_time": 38, "incident_count": 3},
        ]
    else:
        default_zones = [
            {"zone": "Gate A", "crowd_level": 3, "wait_time": 10, "incident_count": 0},
            {"zone": "Gate B", "crowd_level": 3, "wait_time": 10, "incident_count": 0},
            {"zone": "Food Zone 1", "crowd_level": 3, "wait_time": 10, "incident_count": 0},
            {"zone": "Parking Area", "crowd_level": 3, "wait_time": 10, "incident_count": 0},
            {"zone": "Exit Tunnel", "crowd_level": 3, "wait_time": 10, "incident_count": 0},
        ]

    zone_data = []
    cols = st.columns(2)

    for index, zone_item in enumerate(default_zones):
        zone = zone_item["zone"]

        with cols[index % 2]:
            with st.expander(f"📍 {zone}", expanded=index < 2):
                crowd_level = st.slider(
                    f"Crowd level at {zone}",
                    min_value=1,
                    max_value=5,
                    value=zone_item["crowd_level"],
                    key=f"crowd_{scenario_mode}_{zone}",
                    help="1 means light crowd, 5 means very dense crowd.",
                )

                wait_time = st.slider(
                    f"Estimated wait time at {zone} in minutes",
                    min_value=0,
                    max_value=60,
                    value=zone_item["wait_time"],
                    key=f"wait_{scenario_mode}_{zone}",
                )

                incident_count = st.number_input(
                    f"Reported incidents at {zone}",
                    min_value=0,
                    max_value=20,
                    value=zone_item["incident_count"],
                    key=f"incident_{scenario_mode}_{zone}",
                )

                zone_data.append(
                    {
                        "zone": zone,
                        "crowd_level": crowd_level,
                        "wait_time": wait_time,
                        "incident_count": incident_count,
                    }
                )

    if st.button("Analyze stadium risk"):
        ranked = rank_zones(zone_data)
        df = pd.DataFrame(ranked)

        top_zone = ranked[0]
        css_class = risk_class(top_zone["risk"])

        st.markdown(
            f"""
            <div class="result-card">
                <h3>Highest Attention Needed</h3>
                <p><b>{top_zone["zone"]}</b></p>
                <p>
                    <span class="{css_class}">{top_zone["risk"]}</span>
                    &nbsp; Risk Score: <b>{top_zone["risk_score"]}/100</b>
                </p>
                <p>{top_zone["recommendation"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_reason(
            "Why this zone is prioritized?",
            [
                f"Crowd level: {top_zone['crowd_level']} / 5.",
                f"Estimated wait time: {top_zone['wait_time']} minutes.",
                f"Reported incidents: {top_zone['incident_count']}.",
                "The assistant ranks zones by combined crowd pressure, delay, and incident risk.",
            ],
        )

        st.subheader("Ranked Risk Zones")
        st.dataframe(
            df[
                [
                    "zone",
                    "crowd_level",
                    "wait_time",
                    "incident_count",
                    "risk_score",
                    "risk",
                    "recommendation",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

elif mode == "Volunteer Briefing Generator":
    st.markdown('<span class="mode-pill">Volunteer Operations</span>', unsafe_allow_html=True)
    st.header("Volunteer Briefing Generator")

    st.markdown(
        '<p class="small-note">Create short operational instructions for volunteers based on zone, issue type, and risk level.</p>',
        unsafe_allow_html=True,
    )

    selected_scenario = st.selectbox(
        "Quick test scenario",
        list(VOLUNTEER_SCENARIOS.keys()),
    )

    scenario = VOLUNTEER_SCENARIOS[selected_scenario]

    col1, col2, col3 = st.columns(3)

    with col1:
        zone = st.text_input("Assigned zone", value=scenario["zone"], placeholder="Example: Gate B")

    with col2:
        issue_options = [
            "Crowd buildup",
            "Lost fan",
            "Medical support",
            "Transport confusion",
            "Accessibility request",
            "Queue management",
        ]
        issue_type = st.selectbox(
            "Issue type",
            issue_options,
            index=issue_options.index(scenario["issue_type"]),
        )

    with col3:
        risk_options = ["Low", "Medium", "High", "Critical"]
        risk = st.selectbox(
            "Risk level",
            risk_options,
            index=risk_options.index(scenario["risk"]),
        )

    if st.button("Generate volunteer brief"):
        if not zone.strip():
            st.error("Please enter the assigned zone.")
        else:
            brief = generate_volunteer_brief(issue_type, zone, risk)
            st.info(brief)

            render_reason(
                "Why this briefing?",
                [
                    f"The assigned zone is: {zone}.",
                    f"The active issue is: {issue_type}.",
                    f"The operational risk level is: {risk}.",
                    "The assistant keeps instructions short so volunteers can act quickly.",
                ],
            )

elif mode == "Accessibility Support":
    st.markdown('<span class="mode-pill">Inclusive Stadium Support</span>', unsafe_allow_html=True)
    st.header("Accessibility Support")

    st.markdown(
        '<p class="small-note">Generate accessibility-aware guidance for visitors who need safer, clearer movement support.</p>',
        unsafe_allow_html=True,
    )

    selected_scenario = st.selectbox(
        "Quick test scenario",
        list(ACCESSIBILITY_SCENARIOS.keys()),
    )

    scenario = ACCESSIBILITY_SCENARIOS[selected_scenario]

    col1, col2 = st.columns(2)

    with col1:
        visitor_options = [
            "Wheelchair access",
            "Elderly support",
            "Low vision support",
            "Hearing support",
            "Family with children",
            "Lost visitor support",
        ]

        visitor_need = st.selectbox(
            "Visitor need",
            visitor_options,
            index=visitor_options.index(scenario["visitor_need"]),
        )

        location = st.text_input(
            "Current location",
            value=scenario["location"],
            placeholder="Example: South Stand",
        )

    with col2:
        destination = st.text_input(
            "Destination",
            value=scenario["destination"],
            placeholder="Example: Accessible seating area",
        )

        crowd_options = ["Normal", "Busy", "High", "Critical"]

        crowd_condition = st.selectbox(
            "Nearby crowd condition",
            crowd_options,
            index=crowd_options.index(scenario["crowd_condition"]),
        )

    if st.button("Create accessible guidance"):
        if not location.strip() or not destination.strip():
            st.error("Please enter both current location and destination.")
        else:
            if crowd_condition in ["High", "Critical"]:
                route_note = "Avoid the nearest crowded route and assign volunteer escort support."
            elif crowd_condition == "Busy":
                route_note = "Use a calmer accessible route, even if it takes slightly longer."
            else:
                route_note = "Use the shortest accessible route with clear signage."

            st.success(
                f"For {visitor_need.lower()}, guide the visitor from {location} to {destination}. "
                f"{route_note} Prefer ramps, elevators, staff-assisted lanes, calm instructions, "
                "and visible checkpoints."
            )

            render_reason(
                "Why this accessibility route?",
                [
                    f"The visitor need is: {visitor_need}.",
                    f"The current location is: {location}.",
                    f"The destination is: {destination}.",
                    f"The nearby crowd condition is: {crowd_condition}.",
                    "The assistant prioritizes safety, clarity, and staff support over speed.",
                ],
            )

st.markdown(
    """
    <div class="footer-note">
        Built with Python and Streamlit. This prototype uses transparent decision logic,
        does not store personal data, and is designed for the Smart Stadiums & Tournament Experience challenge.
    </div>
    """,
    unsafe_allow_html=True,
)