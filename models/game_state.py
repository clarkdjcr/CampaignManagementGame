"""Central game state container for Campaign Manager 2026."""

from dataclasses import dataclass, field
from typing import Optional

from .state import State
from .player import Player
from .events import GameEvent


@dataclass
class GameState:
    """Central container for all game state."""
    incumbent: Player
    challenger: Player
    states: dict[str, State]  # state abbreviation -> State
    current_turn: int = 1
    max_turns: int = 20
    events_log: list[GameEvent] = field(default_factory=list)
    game_over: bool = False
    winner: Optional[str] = None

    # Electoral vote threshold
    VOTES_TO_WIN: int = field(default=270, repr=False)

    @property
    def turns_remaining(self) -> int:
        """Calculate turns remaining."""
        return self.max_turns - self.current_turn + 1

    @property
    def incumbent_electoral_votes(self) -> int:
        """Calculate incumbent's current electoral vote count."""
        return sum(
            state.electoral_votes
            for state in self.states.values()
            if state.incumbent_support > state.challenger_support
        )

    @property
    def challenger_electoral_votes(self) -> int:
        """Calculate challenger's current electoral vote count."""
        return sum(
            state.electoral_votes
            for state in self.states.values()
            if state.challenger_support > state.incumbent_support
        )

    @property
    def tied_electoral_votes(self) -> int:
        """Calculate electoral votes in tied states."""
        return sum(
            state.electoral_votes
            for state in self.states.values()
            if state.incumbent_support == state.challenger_support
        )

    @property
    def total_electoral_votes(self) -> int:
        """Get total electoral votes."""
        return sum(state.electoral_votes for state in self.states.values())

    @property
    def incumbent_national_polling(self) -> float:
        """Calculate incumbent's national polling average."""
        if not self.states:
            return 0.0
        total_support = sum(
            state.incumbent_support * state.electoral_votes
            for state in self.states.values()
        )
        return total_support / self.total_electoral_votes

    @property
    def challenger_national_polling(self) -> float:
        """Calculate challenger's national polling average."""
        if not self.states:
            return 0.0
        total_support = sum(
            state.challenger_support * state.electoral_votes
            for state in self.states.values()
        )
        return total_support / self.total_electoral_votes

    @property
    def competitive_states(self) -> list[State]:
        """Get list of competitive states (within 10 points)."""
        return [s for s in self.states.values() if s.competitive]

    @property
    def recent_events(self) -> list[GameEvent]:
        """Get last 10 events."""
        return self.events_log[-10:]

    def get_state(self, abbreviation: str) -> Optional[State]:
        """Get a state by abbreviation."""
        return self.states.get(abbreviation.upper())

    def get_states_by_region(self, region: str) -> list[State]:
        """Get all states in a region."""
        return [s for s in self.states.values() if s.region == region]

    def update_state(self, state: State) -> "GameState":
        """Update a state and return new game state."""
        new_states = self.states.copy()
        new_states[state.abbreviation] = state
        return GameState(
            incumbent=self.incumbent,
            challenger=self.challenger,
            states=new_states,
            current_turn=self.current_turn,
            max_turns=self.max_turns,
            events_log=self.events_log.copy(),
            game_over=self.game_over,
            winner=self.winner,
        )

    def add_event(self, event: GameEvent) -> "GameState":
        """Add an event to the log."""
        new_log = self.events_log.copy()
        new_log.append(event)
        return GameState(
            incumbent=self.incumbent,
            challenger=self.challenger,
            states=self.states,
            current_turn=self.current_turn,
            max_turns=self.max_turns,
            events_log=new_log,
            game_over=self.game_over,
            winner=self.winner,
        )

    def advance_turn(self) -> "GameState":
        """Advance to next turn."""
        return GameState(
            incumbent=self.incumbent,
            challenger=self.challenger,
            states=self.states,
            current_turn=self.current_turn + 1,
            max_turns=self.max_turns,
            events_log=self.events_log,
            game_over=self.game_over,
            winner=self.winner,
        )

    def end_game(self, winner: str) -> "GameState":
        """End the game with a winner."""
        return GameState(
            incumbent=self.incumbent,
            challenger=self.challenger,
            states=self.states,
            current_turn=self.current_turn,
            max_turns=self.max_turns,
            events_log=self.events_log,
            game_over=True,
            winner=winner,
        )

    def with_players(
        self,
        incumbent: Optional[Player] = None,
        challenger: Optional[Player] = None
    ) -> "GameState":
        """Return new state with updated players."""
        return GameState(
            incumbent=incumbent if incumbent else self.incumbent,
            challenger=challenger if challenger else self.challenger,
            states=self.states,
            current_turn=self.current_turn,
            max_turns=self.max_turns,
            events_log=self.events_log,
            game_over=self.game_over,
            winner=self.winner,
        )
