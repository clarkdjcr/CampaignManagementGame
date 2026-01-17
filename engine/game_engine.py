"""Main game engine orchestrator for Campaign Manager 2026."""

from typing import Callable, Optional

from models.actions import ActionType, ActionResult
from models.events import GameEvent
from models.game_state import GameState
from models.player import Player
from data.states_data import create_initial_states
from .action_processor import ActionProcessor
from .event_generator import EventGenerator
from .electoral_calculator import ElectoralCalculator, ElectionResult


# Callback types
OnTurnStartCallback = Callable[[GameState, int], None]
OnTurnEndCallback = Callable[[GameState, int], None]
OnEventCallback = Callable[[GameState, GameEvent], None]
OnActionCallback = Callable[[GameState, ActionResult, bool], None]
OnGameEndCallback = Callable[[GameState, ElectionResult], None]


class GameEngine:
    """Main game engine orchestrating all game components."""

    def __init__(self, seed: Optional[int] = None):
        self.action_processor = ActionProcessor()
        self.event_generator = EventGenerator()
        self.electoral_calculator = ElectoralCalculator()

        if seed is not None:
            self.action_processor.seed(seed)
            self.event_generator.seed(seed)

        # Callbacks
        self._on_turn_start: Optional[OnTurnStartCallback] = None
        self._on_turn_end: Optional[OnTurnEndCallback] = None
        self._on_event: Optional[OnEventCallback] = None
        self._on_action: Optional[OnActionCallback] = None
        self._on_game_end: Optional[OnGameEndCallback] = None

        # Game state
        self._game_state: Optional[GameState] = None

    @property
    def game_state(self) -> Optional[GameState]:
        """Get current game state."""
        return self._game_state

    def set_callbacks(
        self,
        on_turn_start: Optional[OnTurnStartCallback] = None,
        on_turn_end: Optional[OnTurnEndCallback] = None,
        on_event: Optional[OnEventCallback] = None,
        on_action: Optional[OnActionCallback] = None,
        on_game_end: Optional[OnGameEndCallback] = None,
    ) -> None:
        """Set callback functions for game events."""
        if on_turn_start:
            self._on_turn_start = on_turn_start
        if on_turn_end:
            self._on_turn_end = on_turn_end
        if on_event:
            self._on_event = on_event
        if on_action:
            self._on_action = on_action
        if on_game_end:
            self._on_game_end = on_game_end

    def new_game(
        self,
        player_name: str,
        challenger_name: str = "The Challenger",
    ) -> GameState:
        """Initialize a new game."""
        incumbent = Player(
            name=player_name,
            is_incumbent=True,
            funds=15,
            momentum=0,
            is_human=True,
        )

        challenger = Player(
            name=challenger_name,
            is_incumbent=False,
            funds=15,
            momentum=0,
            is_human=False,
        )

        self._game_state = GameState(
            incumbent=incumbent,
            challenger=challenger,
            states=create_initial_states(),
            current_turn=1,
            max_turns=20,
            events_log=[],
            game_over=False,
            winner=None,
        )

        return self._game_state

    def start_turn(self) -> GameState:
        """Start a new turn and possibly generate an event."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized. Call new_game() first.")

        if self._game_state.game_over:
            raise RuntimeError("Game is already over.")

        # Trigger turn start callback
        if self._on_turn_start:
            self._on_turn_start(self._game_state, self._game_state.current_turn)

        # Maybe generate a random event
        event = self.event_generator.maybe_generate_event(self._game_state)
        if event:
            self._game_state = self.event_generator.apply_event(self._game_state, event)
            if self._on_event:
                self._on_event(self._game_state, event)

        return self._game_state

    def execute_player_action(
        self,
        action_type: ActionType,
        target_states: Optional[list[str]] = None,
    ) -> tuple[GameState, ActionResult]:
        """Execute the human player's (incumbent's) action."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized.")

        self._game_state, result = self.action_processor.execute_action(
            self._game_state,
            action_type,
            is_incumbent=True,
            target_states=target_states,
        )

        if self._on_action:
            self._on_action(self._game_state, result, True)

        return self._game_state, result

    def execute_ai_action(
        self,
        action_type: ActionType,
        target_states: Optional[list[str]] = None,
    ) -> tuple[GameState, ActionResult]:
        """Execute the AI's (challenger's) action."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized.")

        self._game_state, result = self.action_processor.execute_action(
            self._game_state,
            action_type,
            is_incumbent=False,
            target_states=target_states,
        )

        if self._on_action:
            self._on_action(self._game_state, result, False)

        return self._game_state, result

    def end_turn(self) -> GameState:
        """End the current turn and advance to next."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized.")

        # Trigger turn end callback
        if self._on_turn_end:
            self._on_turn_end(self._game_state, self._game_state.current_turn)

        # Check if game should end
        if self._game_state.current_turn >= self._game_state.max_turns:
            return self.end_game()

        # Advance turn
        self._game_state = self._game_state.advance_turn()

        return self._game_state

    def end_game(self) -> GameState:
        """End the game and determine winner."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized.")

        # Calculate final result
        result = self.electoral_calculator.calculate_final_result(self._game_state)

        # Update game state
        self._game_state = self._game_state.end_game(result.winner)

        # Trigger callback
        if self._on_game_end:
            self._on_game_end(self._game_state, result)

        return self._game_state

    def get_current_evs(self) -> tuple[int, int, int]:
        """Get current electoral vote counts."""
        if self._game_state is None:
            return 0, 0, 0
        return self.electoral_calculator.calculate_current_evs(self._game_state)

    def get_election_result(self) -> Optional[ElectionResult]:
        """Get the final election result (only valid after game ends)."""
        if self._game_state is None or not self._game_state.game_over:
            return None
        return self.electoral_calculator.calculate_final_result(self._game_state)

    def get_affordable_actions(self, for_incumbent: bool = True) -> list:
        """Get actions the specified player can afford."""
        if self._game_state is None:
            return []

        player = (
            self._game_state.incumbent if for_incumbent
            else self._game_state.challenger
        )
        return self.action_processor.get_affordable_actions(player)

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self._game_state is not None and self._game_state.game_over

    def get_turn_info(self) -> tuple[int, int, int]:
        """Get current turn, max turns, and turns remaining."""
        if self._game_state is None:
            return 0, 0, 0
        return (
            self._game_state.current_turn,
            self._game_state.max_turns,
            self._game_state.turns_remaining,
        )
