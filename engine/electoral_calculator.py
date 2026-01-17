"""Electoral vote calculator for Campaign Manager 2026."""

from dataclasses import dataclass
from typing import Optional

from models.game_state import GameState
from models.state import State


@dataclass
class ElectionResult:
    """Final election result."""
    winner: str
    incumbent_evs: int
    challenger_evs: int
    incumbent_popular: float
    challenger_popular: float
    state_results: dict[str, str]  # state abbrev -> winner
    margin: int  # EV margin (positive = incumbent win)
    is_landslide: bool  # Won by 100+ EVs


class ElectoralCalculator:
    """Calculates electoral votes and determines winner."""

    VOTES_TO_WIN = 270
    TOTAL_VOTES = 538
    LANDSLIDE_MARGIN = 100

    def calculate_current_evs(
        self,
        game_state: GameState,
    ) -> tuple[int, int, int]:
        """
        Calculate current electoral vote counts.

        Returns:
            Tuple of (incumbent_evs, challenger_evs, tied_evs)
        """
        incumbent_evs = 0
        challenger_evs = 0
        tied_evs = 0

        for state in game_state.states.values():
            if state.incumbent_support > state.challenger_support:
                incumbent_evs += state.electoral_votes
            elif state.challenger_support > state.incumbent_support:
                challenger_evs += state.electoral_votes
            else:
                tied_evs += state.electoral_votes

        return incumbent_evs, challenger_evs, tied_evs

    def get_state_winner(self, state: State) -> Optional[str]:
        """Determine winner of a state. Returns None if tied."""
        if state.incumbent_support > state.challenger_support:
            return "Incumbent"
        elif state.challenger_support > state.incumbent_support:
            return "Challenger"
        return None

    def calculate_final_result(
        self,
        game_state: GameState,
    ) -> ElectionResult:
        """
        Calculate the final election result.

        Tied states are resolved by coin flip.
        """
        import random

        incumbent_evs = 0
        challenger_evs = 0
        state_results = {}

        for abbrev, state in game_state.states.items():
            if state.incumbent_support > state.challenger_support:
                incumbent_evs += state.electoral_votes
                state_results[abbrev] = "Incumbent"
            elif state.challenger_support > state.incumbent_support:
                challenger_evs += state.electoral_votes
                state_results[abbrev] = "Challenger"
            else:
                # Coin flip for tied states
                if random.choice([True, False]):
                    incumbent_evs += state.electoral_votes
                    state_results[abbrev] = "Incumbent"
                else:
                    challenger_evs += state.electoral_votes
                    state_results[abbrev] = "Challenger"

        # Calculate popular vote (weighted by EVs)
        total_evs = sum(s.electoral_votes for s in game_state.states.values())
        incumbent_popular = sum(
            s.incumbent_support * s.electoral_votes
            for s in game_state.states.values()
        ) / total_evs

        challenger_popular = sum(
            s.challenger_support * s.electoral_votes
            for s in game_state.states.values()
        ) / total_evs

        # Determine winner
        margin = incumbent_evs - challenger_evs
        if incumbent_evs >= self.VOTES_TO_WIN:
            winner = "Incumbent"
        elif challenger_evs >= self.VOTES_TO_WIN:
            winner = "Challenger"
        elif incumbent_evs > challenger_evs:
            winner = "Incumbent"
        elif challenger_evs > incumbent_evs:
            winner = "Challenger"
        else:
            # True tie - incumbent advantage (House decides)
            winner = "Incumbent"

        return ElectionResult(
            winner=winner,
            incumbent_evs=incumbent_evs,
            challenger_evs=challenger_evs,
            incumbent_popular=round(incumbent_popular, 1),
            challenger_popular=round(challenger_popular, 1),
            state_results=state_results,
            margin=margin,
            is_landslide=abs(margin) >= self.LANDSLIDE_MARGIN,
        )

    def get_path_to_victory(
        self,
        game_state: GameState,
        for_incumbent: bool,
    ) -> list[str]:
        """
        Get the most efficient path to 270 EVs.

        Returns list of state abbreviations to win, prioritized by
        competitiveness and EV value.
        """
        current_evs = 0
        needed_states = []

        # Start with states already won
        for abbrev, state in game_state.states.items():
            if for_incumbent:
                if state.incumbent_support > state.challenger_support:
                    current_evs += state.electoral_votes
            else:
                if state.challenger_support > state.incumbent_support:
                    current_evs += state.electoral_votes

        if current_evs >= self.VOTES_TO_WIN:
            return []  # Already winning

        # Sort remaining states by efficiency (EVs / margin to flip)
        remaining = []
        for abbrev, state in game_state.states.items():
            if for_incumbent:
                if state.incumbent_support <= state.challenger_support:
                    margin = state.challenger_support - state.incumbent_support
                    efficiency = state.electoral_votes / max(margin, 0.1)
                    remaining.append((abbrev, state.electoral_votes, efficiency))
            else:
                if state.challenger_support <= state.incumbent_support:
                    margin = state.incumbent_support - state.challenger_support
                    efficiency = state.electoral_votes / max(margin, 0.1)
                    remaining.append((abbrev, state.electoral_votes, efficiency))

        # Sort by efficiency (higher is better)
        remaining.sort(key=lambda x: x[2], reverse=True)

        # Add states until we have enough EVs
        evs_needed = self.VOTES_TO_WIN - current_evs
        for abbrev, evs, _ in remaining:
            needed_states.append(abbrev)
            evs_needed -= evs
            if evs_needed <= 0:
                break

        return needed_states

    def is_mathematically_eliminated(
        self,
        game_state: GameState,
        for_incumbent: bool,
    ) -> bool:
        """Check if a candidate is mathematically eliminated."""
        if for_incumbent:
            # Incumbent is eliminated if challenger has 270+ locked
            challenger_locked = sum(
                s.electoral_votes
                for s in game_state.states.values()
                if s.challenger_support - s.incumbent_support > 15
            )
            return challenger_locked >= self.VOTES_TO_WIN
        else:
            incumbent_locked = sum(
                s.electoral_votes
                for s in game_state.states.values()
                if s.incumbent_support - s.challenger_support > 15
            )
            return incumbent_locked >= self.VOTES_TO_WIN

    def get_battleground_analysis(
        self,
        game_state: GameState,
    ) -> dict[str, dict]:
        """Get analysis of all competitive states."""
        analysis = {}

        for abbrev, state in game_state.states.items():
            if state.competitive:
                leader = state.leader
                margin = abs(state.margin)

                if margin < 2:
                    status = "Tossup"
                elif margin < 5:
                    status = f"Lean {leader}"
                else:
                    status = f"Likely {leader}"

                analysis[abbrev] = {
                    "name": state.name,
                    "evs": state.electoral_votes,
                    "leader": leader,
                    "margin": round(margin, 1),
                    "status": status,
                    "incumbent_support": state.incumbent_support,
                    "challenger_support": state.challenger_support,
                }

        return analysis
