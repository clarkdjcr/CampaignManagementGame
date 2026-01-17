"""AI opponent logic for Campaign Manager 2026."""

import random
from enum import Enum, auto
from typing import Optional

from models.actions import ActionType, get_action_definition
from models.game_state import GameState


class AIStrategy(Enum):
    """AI decision-making strategies."""
    AGGRESSIVE = auto()   # When losing badly - attack!
    DEFENSIVE = auto()    # When winning - protect lead
    BALANCED = auto()     # Close race - mix of approaches
    FUNDRAISING = auto()  # Low on funds - prioritize money


class AIOpponent:
    """AI opponent that makes strategic campaign decisions."""

    # Thresholds for strategy selection
    LOSING_THRESHOLD = 30    # EVs behind to trigger aggressive
    WINNING_THRESHOLD = 30   # EVs ahead to trigger defensive
    LOW_FUNDS_THRESHOLD = 2  # Million dollars to trigger fundraising

    # Action weights by strategy
    AGGRESSIVE_WEIGHTS = {
        ActionType.FUNDRAISER: 0.05,
        ActionType.RALLY: 0.15,
        ActionType.AD_CAMPAIGN: 0.25,
        ActionType.GRASSROOTS: 0.05,
        ActionType.DEBATE_PREP: 0.05,
        ActionType.OPPOSITION_RESEARCH: 0.30,
        ActionType.MEDIA_BLITZ: 0.15,
    }

    DEFENSIVE_WEIGHTS = {
        ActionType.FUNDRAISER: 0.10,
        ActionType.RALLY: 0.20,
        ActionType.AD_CAMPAIGN: 0.15,
        ActionType.GRASSROOTS: 0.25,
        ActionType.DEBATE_PREP: 0.20,
        ActionType.OPPOSITION_RESEARCH: 0.05,
        ActionType.MEDIA_BLITZ: 0.05,
    }

    BALANCED_WEIGHTS = {
        ActionType.FUNDRAISER: 0.10,
        ActionType.RALLY: 0.20,
        ActionType.AD_CAMPAIGN: 0.20,
        ActionType.GRASSROOTS: 0.15,
        ActionType.DEBATE_PREP: 0.10,
        ActionType.OPPOSITION_RESEARCH: 0.10,
        ActionType.MEDIA_BLITZ: 0.15,
    }

    FUNDRAISING_WEIGHTS = {
        ActionType.FUNDRAISER: 0.70,
        ActionType.RALLY: 0.05,
        ActionType.AD_CAMPAIGN: 0.05,
        ActionType.GRASSROOTS: 0.10,
        ActionType.DEBATE_PREP: 0.05,
        ActionType.OPPOSITION_RESEARCH: 0.0,
        ActionType.MEDIA_BLITZ: 0.05,
    }

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random()
        if seed is not None:
            self._rng.seed(seed)

    def seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        self._rng.seed(seed)

    def determine_strategy(self, game_state: GameState) -> AIStrategy:
        """Determine the best strategy based on current game state."""
        challenger = game_state.challenger

        # Check if low on funds first (highest priority)
        if challenger.funds < self.LOW_FUNDS_THRESHOLD:
            return AIStrategy.FUNDRAISING

        # Calculate EV difference
        inc_evs, chl_evs, _ = self._calculate_evs(game_state)
        ev_diff = chl_evs - inc_evs

        # Determine strategy based on electoral position
        if ev_diff <= -self.LOSING_THRESHOLD:
            return AIStrategy.AGGRESSIVE
        elif ev_diff >= self.WINNING_THRESHOLD:
            return AIStrategy.DEFENSIVE
        else:
            return AIStrategy.BALANCED

    def choose_action(
        self,
        game_state: GameState,
    ) -> tuple[ActionType, Optional[list[str]]]:
        """
        Choose an action for the AI to take.

        Returns:
            Tuple of (action_type, target_states)
        """
        strategy = self.determine_strategy(game_state)
        weights = self._get_weights_for_strategy(strategy)

        # Filter to affordable actions
        challenger = game_state.challenger
        affordable_weights = {}

        for action_type, weight in weights.items():
            definition = get_action_definition(action_type)
            if challenger.can_afford(definition.cost):
                affordable_weights[action_type] = weight

        # If nothing affordable, must fundraise
        if not affordable_weights:
            return ActionType.FUNDRAISER, None

        # Normalize weights
        total_weight = sum(affordable_weights.values())
        if total_weight == 0:
            # Fallback to fundraising
            return ActionType.FUNDRAISER, None

        # Random weighted selection
        roll = self._rng.random() * total_weight
        cumulative = 0.0

        for action_type, weight in affordable_weights.items():
            cumulative += weight
            if roll <= cumulative:
                target_states = self._select_target_states(
                    game_state, action_type
                )
                return action_type, target_states

        # Fallback (shouldn't reach here)
        return ActionType.FUNDRAISER, None

    def _get_weights_for_strategy(self, strategy: AIStrategy) -> dict:
        """Get action weights for a given strategy."""
        match strategy:
            case AIStrategy.AGGRESSIVE:
                return self.AGGRESSIVE_WEIGHTS
            case AIStrategy.DEFENSIVE:
                return self.DEFENSIVE_WEIGHTS
            case AIStrategy.BALANCED:
                return self.BALANCED_WEIGHTS
            case AIStrategy.FUNDRAISING:
                return self.FUNDRAISING_WEIGHTS

    def _select_target_states(
        self,
        game_state: GameState,
        action_type: ActionType,
    ) -> Optional[list[str]]:
        """Select target states for an action."""
        definition = get_action_definition(action_type)

        # Non-targeted actions
        if definition.target_states == 0:
            return None

        # Get competitive states sorted by closeness
        competitive = []
        for abbrev, state in game_state.states.items():
            margin = state.incumbent_support - state.challenger_support
            competitive.append((abbrev, abs(margin), state.electoral_votes))

        # Sort by closeness (prefer tighter races) then by EVs
        competitive.sort(key=lambda x: (x[1], -x[2]))

        # Take the closest races up to target count
        targets = [abbrev for abbrev, _, _ in competitive[:definition.target_states]]

        return targets

    def _calculate_evs(
        self,
        game_state: GameState,
    ) -> tuple[int, int, int]:
        """Calculate current electoral votes."""
        inc_evs = 0
        chl_evs = 0
        tied_evs = 0

        for state in game_state.states.values():
            if state.incumbent_support > state.challenger_support:
                inc_evs += state.electoral_votes
            elif state.challenger_support > state.incumbent_support:
                chl_evs += state.electoral_votes
            else:
                tied_evs += state.electoral_votes

        return inc_evs, chl_evs, tied_evs

    def get_strategy_description(self, strategy: AIStrategy) -> str:
        """Get a human-readable description of the strategy."""
        match strategy:
            case AIStrategy.AGGRESSIVE:
                return "Playing aggressively - focusing on attack ads and opposition research"
            case AIStrategy.DEFENSIVE:
                return "Playing defensively - building grassroots support and preparing for debates"
            case AIStrategy.BALANCED:
                return "Taking a balanced approach - mixing offense and defense"
            case AIStrategy.FUNDRAISING:
                return "Focusing on fundraising - campaign coffers are low"

    def evaluate_position(self, game_state: GameState) -> str:
        """Get AI's assessment of its position."""
        inc_evs, chl_evs, _ = self._calculate_evs(game_state)
        challenger = game_state.challenger

        if chl_evs >= 270:
            return "Victory is within reach!"
        elif chl_evs >= inc_evs + 50:
            return "Commanding lead - maintain pressure"
        elif chl_evs >= inc_evs + 20:
            return "Solid lead - stay focused"
        elif chl_evs >= inc_evs - 20:
            return "Race is tight - every vote matters"
        elif chl_evs >= inc_evs - 50:
            return "Trailing - need to change the narrative"
        else:
            return "Significant deficit - time for bold moves"
