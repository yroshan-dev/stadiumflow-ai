import pandas as pd


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


def test_tickets_csv_has_required_columns():
    tickets = pd.read_csv("data/tickets.csv")

    for column in REQUIRED_TICKET_COLUMNS:
        assert column in tickets.columns


def test_facilities_csv_has_required_columns():
    facilities = pd.read_csv("data/facilities.csv")

    for column in REQUIRED_FACILITY_COLUMNS:
        assert column in facilities.columns


def test_demo_ticket_exists():
    tickets = pd.read_csv("data/tickets.csv")

    assert "WC26-FINAL-EAST-128-22-14" in tickets["ticket_id"].values


def test_ticket_zones_have_matching_facilities():
    tickets = pd.read_csv("data/tickets.csv")
    facilities = pd.read_csv("data/facilities.csv")

    ticket_zones = set(tickets["zone"].dropna().unique())
    facility_zones = set(facilities["zone"].dropna().unique())

    missing_zones = ticket_zones - facility_zones

    assert not missing_zones, f"Missing facility data for zones: {missing_zones}"


def test_facility_distance_minutes_is_numeric():
    facilities = pd.read_csv("data/facilities.csv")

    assert pd.api.types.is_numeric_dtype(facilities["distance_minutes"])


def test_each_zone_has_emergency_support():
    facilities = pd.read_csv("data/facilities.csv")

    required_types = {"Medical", "Security", "Exit"}

    for zone in facilities["zone"].dropna().unique():
        zone_types = set(facilities[facilities["zone"] == zone]["type"])
        missing_types = required_types - zone_types

        assert not missing_types, f"{zone} is missing emergency support: {missing_types}"
