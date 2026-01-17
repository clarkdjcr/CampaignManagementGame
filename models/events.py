"""Event types and game events for Campaign Manager 2026."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class EventType(Enum):
    """Types of random events that can occur."""
    SCANDAL = auto()
    ECONOMIC = auto()
    ENDORSEMENT = auto()
    GAFFE = auto()
    CRISIS = auto()
    VIRAL = auto()


@dataclass
class GameEvent:
    """A random event that affects the game state."""
    event_type: EventType
    title: str
    description: str
    affects_incumbent: bool  # True if affects incumbent, False if challenger
    support_change: float  # Polling change (positive = good for affected player)
    momentum_change: int
    affected_states: list[str] = field(default_factory=list)  # Empty = national
    turn_occurred: int = 0

    @property
    def is_national(self) -> bool:
        """Check if event affects all states."""
        return len(self.affected_states) == 0

    @property
    def impact_description(self) -> str:
        """Get a description of the event's impact."""
        target = "Incumbent" if self.affects_incumbent else "Challenger"
        if self.support_change > 0:
            return f"{target} gains support"
        elif self.support_change < 0:
            return f"{target} loses support"
        else:
            return f"Affects {target}'s momentum"


# Event templates for random generation
SCANDAL_EVENTS = [
    ("Campaign Finance Questions", "Irregularities discovered in campaign donations"),
    ("Staff Controversy", "Senior campaign staffer resigns amid allegations"),
    ("Past Statement Resurfaces", "Old social media posts cause controversy"),
]

ECONOMIC_EVENTS = [
    ("Jobs Report Released", "Monthly employment numbers shift the narrative"),
    ("Stock Market Swing", "Market volatility becomes campaign issue"),
    ("Inflation Data", "New inflation figures dominate headlines"),
]

ENDORSEMENT_EVENTS = [
    ("Celebrity Endorsement", "Major celebrity publicly backs candidate"),
    ("Union Endorsement", "Powerful labor union announces support"),
    ("Newspaper Endorsement", "Influential newspaper editorial board weighs in"),
    ("Former Rival Endorsement", "Primary opponent endorses candidate"),
]

GAFFE_EVENTS = [
    ("Hot Mic Moment", "Candidate caught saying something regrettable"),
    ("Debate Stumble", "Awkward moment goes viral from debate"),
    ("Geography Gaffe", "Candidate mixes up state facts"),
]

CRISIS_EVENTS = [
    ("Natural Disaster", "Hurricane/wildfire tests crisis leadership"),
    ("International Incident", "Foreign policy crisis emerges"),
    ("Public Health Issue", "Health emergency requires response"),
]

VIRAL_EVENTS = [
    ("Campaign Ad Goes Viral", "Ad resonates unexpectedly with voters"),
    ("Meme Magic", "Candidate becomes positive internet sensation"),
    ("Town Hall Moment", "Emotional exchange with voter spreads online"),
]

EVENT_TEMPLATES = {
    EventType.SCANDAL: SCANDAL_EVENTS,
    EventType.ECONOMIC: ECONOMIC_EVENTS,
    EventType.ENDORSEMENT: ENDORSEMENT_EVENTS,
    EventType.GAFFE: GAFFE_EVENTS,
    EventType.CRISIS: CRISIS_EVENTS,
    EventType.VIRAL: VIRAL_EVENTS,
}
