"""Initial state configurations for Campaign Manager 2026.

14 states/regions totaling 538 electoral votes.
Starting balance:
- ~101 Safe Incumbent EVs
- ~127 Lean Incumbent EVs
- ~101 Tossup EVs
- ~33 Lean Challenger EVs
- ~176 Safe Challenger EVs
"""

from models.state import State


# State configuration: (name, abbrev, evs, inc_support, chl_support, lean, region)
INITIAL_STATES_CONFIG = [
    # Safe Incumbent States
    ("California", "CA", 54, 58.0, 38.0, "Safe Inc", "West"),
    ("New York", "NY", 28, 56.0, 40.0, "Safe Inc", "Northeast"),
    ("Illinois", "IL", 19, 55.0, 41.0, "Safe Inc", "Midwest"),

    # Lean Incumbent
    ("Blue Coalition", "BC", 127, 52.0, 44.0, "Lean Inc", "Multiple"),

    # Tossup States - The Battlegrounds
    ("Florida", "FL", 30, 48.0, 48.0, "Tossup", "South"),
    ("Pennsylvania", "PA", 19, 49.0, 47.0, "Tossup", "Northeast"),
    ("Georgia", "GA", 16, 47.0, 49.0, "Tossup", "South"),
    ("Michigan", "MI", 15, 48.5, 47.5, "Tossup", "Midwest"),
    ("Arizona", "AZ", 11, 47.0, 48.0, "Tossup", "West"),
    ("Wisconsin", "WI", 10, 48.0, 48.0, "Tossup", "Midwest"),

    # Lean Challenger
    ("Ohio", "OH", 17, 44.0, 52.0, "Lean Chl", "Midwest"),
    ("North Carolina", "NC", 16, 45.0, 51.0, "Lean Chl", "South"),

    # Safe Challenger States
    ("Texas", "TX", 40, 42.0, 54.0, "Safe Chl", "South"),
    ("Red Coalition", "RC", 136, 38.0, 58.0, "Safe Chl", "Multiple"),
]


def create_initial_states() -> dict[str, State]:
    """Create the initial state dictionary for a new game."""
    states = {}
    for name, abbrev, evs, inc_sup, chl_sup, lean, region in INITIAL_STATES_CONFIG:
        states[abbrev] = State(
            name=name,
            abbreviation=abbrev,
            electoral_votes=evs,
            incumbent_support=inc_sup,
            challenger_support=chl_sup,
            lean=lean,
            region=region,
        )
    return states


# Pre-built initial states for quick access
INITIAL_STATES = create_initial_states()


def get_battleground_states() -> list[str]:
    """Get list of competitive battleground state abbreviations."""
    return ["FL", "PA", "GA", "MI", "AZ", "WI", "OH", "NC"]


def get_safe_incumbent_states() -> list[str]:
    """Get list of safe incumbent state abbreviations."""
    return ["CA", "NY", "IL", "BC"]


def get_safe_challenger_states() -> list[str]:
    """Get list of safe challenger state abbreviations."""
    return ["TX", "RC"]


def get_total_electoral_votes() -> int:
    """Get total electoral votes (should be 538)."""
    return sum(s.electoral_votes for s in INITIAL_STATES.values())
