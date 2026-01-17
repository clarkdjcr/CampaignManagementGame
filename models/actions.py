"""Action types, definitions, and results for Campaign Manager 2026."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class ActionType(Enum):
    """Types of actions a player can take."""
    FUNDRAISER = auto()
    RALLY = auto()
    AD_CAMPAIGN = auto()
    GRASSROOTS = auto()
    DEBATE_PREP = auto()
    OPPOSITION_RESEARCH = auto()
    MEDIA_BLITZ = auto()


@dataclass(frozen=True)
class ActionDefinition:
    """Definition of an action with its costs and effects."""
    action_type: ActionType
    name: str
    description: str
    cost: int  # in millions
    base_support_change: float  # base polling change
    momentum_change: int  # change to momentum
    target_states: int  # number of states affected (0 = national)

    @property
    def display_cost(self) -> str:
        """Format cost for display."""
        return f"${self.cost}M"


# Define all 7 action types with their effects
ACTION_DEFINITIONS: dict[ActionType, ActionDefinition] = {
    ActionType.FUNDRAISER: ActionDefinition(
        action_type=ActionType.FUNDRAISER,
        name="Fundraiser",
        description="Host a fundraising event to replenish campaign funds",
        cost=0,
        base_support_change=0.0,
        momentum_change=-5,
        target_states=0,
    ),
    ActionType.RALLY: ActionDefinition(
        action_type=ActionType.RALLY,
        name="Campaign Rally",
        description="Hold a rally in a target state to boost support",
        cost=2,
        base_support_change=3.0,
        momentum_change=5,
        target_states=1,
    ),
    ActionType.AD_CAMPAIGN: ActionDefinition(
        action_type=ActionType.AD_CAMPAIGN,
        name="Ad Campaign",
        description="Run targeted TV and digital ads in multiple states",
        cost=4,
        base_support_change=2.0,
        momentum_change=3,
        target_states=3,
    ),
    ActionType.GRASSROOTS: ActionDefinition(
        action_type=ActionType.GRASSROOTS,
        name="Grassroots Organizing",
        description="Deploy volunteers for door-to-door canvassing",
        cost=1,
        base_support_change=1.5,
        momentum_change=2,
        target_states=2,
    ),
    ActionType.DEBATE_PREP: ActionDefinition(
        action_type=ActionType.DEBATE_PREP,
        name="Debate Preparation",
        description="Prepare for upcoming debates with policy briefings",
        cost=1,
        base_support_change=0.0,
        momentum_change=10,
        target_states=0,
    ),
    ActionType.OPPOSITION_RESEARCH: ActionDefinition(
        action_type=ActionType.OPPOSITION_RESEARCH,
        name="Opposition Research",
        description="Investigate opponent's record for attack ads",
        cost=3,
        base_support_change=-2.5,  # Negative effect on opponent
        momentum_change=0,
        target_states=0,  # National effect
    ),
    ActionType.MEDIA_BLITZ: ActionDefinition(
        action_type=ActionType.MEDIA_BLITZ,
        name="Media Blitz",
        description="Intensive media appearances across networks",
        cost=3,
        base_support_change=1.5,
        momentum_change=8,
        target_states=0,  # National effect
    ),
}


@dataclass
class ActionResult:
    """Result of executing an action."""
    action_type: ActionType
    success: bool
    message: str
    funds_spent: int
    funds_raised: int  # For fundraisers
    support_changes: dict[str, float]  # state_name -> change
    momentum_change: int
    affected_states: list[str]

    @property
    def net_funds_change(self) -> int:
        """Calculate net change in funds."""
        return self.funds_raised - self.funds_spent


def get_action_definition(action_type: ActionType) -> ActionDefinition:
    """Get the definition for an action type."""
    return ACTION_DEFINITIONS[action_type]


def get_all_actions() -> list[ActionDefinition]:
    """Get all action definitions."""
    return list(ACTION_DEFINITIONS.values())
