# stadium_engine.py

from typing import Dict, List


def crowd_risk_score(crowd_level: int, wait_time: int, incident_count: int) -> int:
    """
    Calculate crowd risk using crowd level, estimated wait time,
    and number of reported incidents.
    """

    score = (crowd_level * 12) + (wait_time * 2) + (incident_count * 10)
    return max(0, min(score, 100))


def risk_label(score: int) -> str:
    """Convert numeric score into a risk label."""

    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def zone_recommendation(zone: str, score: int) -> str:
    """Generate staff recommendation based on zone risk."""

    label = risk_label(score)

    if label == "Critical":
        return f"Redirect fans away from {zone}, send additional volunteers, and alert operations staff immediately."
    if label == "High":
        return f"Increase volunteer presence near {zone} and suggest alternate routes to fans."
    if label == "Medium":
        return f"Monitor {zone} closely and prepare backup routing if crowd levels rise."
    return f"{zone} is currently manageable. Continue normal monitoring."


def analyze_zone(zone: str, crowd_level: int, wait_time: int, incident_count: int) -> Dict[str, object]:
    """Analyze one stadium zone."""

    score = crowd_risk_score(crowd_level, wait_time, incident_count)

    return {
        "zone": zone,
        "crowd_level": crowd_level,
        "wait_time": wait_time,
        "incident_count": incident_count,
        "risk_score": score,
        "risk": risk_label(score),
        "recommendation": zone_recommendation(zone, score),
    }


def rank_zones(zones: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Rank stadium zones by risk score."""

    analyzed = [
        analyze_zone(
            zone=item["zone"],
            crowd_level=item["crowd_level"],
            wait_time=item["wait_time"],
            incident_count=item["incident_count"],
        )
        for item in zones
    ]

    return sorted(analyzed, key=lambda item: item["risk_score"], reverse=True)


def generate_fan_guidance(user_type: str, location: str, need: str, language: str) -> str:
    """Generate simple fan-facing guidance."""

    base_response = (
        f"For a {user_type.lower()} currently near {location}, the safest next step is to "
    )

    need_lower = need.lower()

    if "exit" in need_lower:
        advice = "move toward the nearest marked exit, avoid dense queues, and follow volunteer instructions."
    elif "food" in need_lower:
        advice = "choose the less crowded food zone and avoid peak halftime movement."
    elif "medical" in need_lower or "help" in need_lower:
        advice = "contact the nearest volunteer or medical desk immediately."
    elif "transport" in need_lower:
        advice = "leave through the recommended transport gate and avoid crowd-heavy exits."
    elif "accessibility" in need_lower or "wheelchair" in need_lower:
        advice = "use accessible routes, elevators, ramps, and staff-assisted lanes wherever available."
    else:
        advice = "follow the nearest official sign, avoid crowded areas, and ask a volunteer for support."

    return (
        base_response
        + advice
        + f" Guidance style selected: {language}. Keep the message short, clear, and easy to understand."
    )


def generate_volunteer_brief(issue_type: str, zone: str, risk: str) -> str:
    """Generate a short volunteer briefing."""

    if risk in ["Critical", "High"]:
        tone = "Act quickly and stay calm."
    else:
        tone = "Monitor the situation and assist fans politely."

    return (
        f"{tone} You are assigned to {zone}. Current issue: {issue_type}. "
        "Guide fans with short instructions, avoid panic, support elderly and disabled visitors, "
        "and report any escalation to venue operations."
    )