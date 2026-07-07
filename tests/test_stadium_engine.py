# tests/test_stadium_engine.py

from stadium_engine import (
    analyze_zone,
    crowd_risk_score,
    generate_fan_guidance,
    generate_volunteer_brief,
    risk_label,
)


def test_crowd_risk_score_is_capped_at_100():
    assert crowd_risk_score(5, 60, 10) == 100


def test_low_risk_label():
    assert risk_label(20) == "Low"


def test_critical_risk_label():
    assert risk_label(90) == "Critical"


def test_analyze_zone_returns_expected_keys():
    result = analyze_zone("Gate A", 4, 20, 2)

    assert result["zone"] == "Gate A"
    assert "risk_score" in result
    assert "recommendation" in result


def test_fan_guidance_handles_accessibility():
    result = generate_fan_guidance(
        user_type="Elderly visitor",
        location="Gate C",
        need="wheelchair accessibility",
        language="Simple English",
    )

    assert "accessible routes" in result


def test_volunteer_brief_contains_zone():
    result = generate_volunteer_brief("Crowd buildup", "Gate B", "High")

    assert "Gate B" in result