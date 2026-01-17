"""Campaign Manager 2026 - Presidential Election Strategy Game.

A terminal-based strategy game where you play as the incumbent president
seeking re-election against an AI challenger. Manage your campaign funds,
build momentum, and win 270 electoral votes to secure victory!
"""

from typing import Optional

from models.actions import ActionType, get_action_definition
from models.events import GameEvent
from models.game_state import GameState
from engine.game_engine import GameEngine
from engine.electoral_calculator import ElectionResult
from ai.ai_opponent import AIOpponent
from views.console import console
from views.setup_screen import SetupScreen
from views.game_screen import GameScreen
from views.actions_view import ActionsView
from views.events_view import EventsView
from views.results_screen import ResultsScreen


class CampaignManager:
    """Main game controller."""

    def __init__(self):
        self.engine = GameEngine()
        self.ai = AIOpponent()
        self.setup_screen = SetupScreen()
        self.game_screen = GameScreen()
        self.actions_view = ActionsView()
        self.events_view = EventsView()
        self.results_screen = ResultsScreen()

        self._last_event: Optional[GameEvent] = None
        self._player_action_msg: str = ""
        self._ai_action_msg: str = ""

    def run(self) -> None:
        """Run the main game loop."""
        while True:
            # Setup phase
            should_start, player_name = self.setup_screen.run()
            if not should_start:
                console.print("[info]Thanks for considering Campaign Manager 2026![/info]")
                break

            # Initialize game
            game_state = self.engine.new_game(player_name)

            # Main game loop
            game_over = False
            while not game_over:
                game_over = self._run_turn()

            # Show results
            result = self.engine.get_election_result()
            if result:
                self.results_screen.display_results(
                    self.engine.game_state,
                    result
                )

            # Play again?
            if not self.results_screen.prompt_play_again():
                console.print("\n[info]Thanks for playing Campaign Manager 2026![/info]")
                break

    def _run_turn(self) -> bool:
        """
        Run a single turn.

        Returns:
            True if game is over, False otherwise
        """
        game_state = self.engine.game_state

        # Start turn (may generate event)
        self._last_event = None
        old_events_count = len(game_state.events_log)

        game_state = self.engine.start_turn()

        # Check for new event
        if len(game_state.events_log) > old_events_count:
            self._last_event = game_state.events_log[-1]

        # Display turn start
        self.game_screen.display_turn_start(game_state)

        # Show event if one occurred
        if self._last_event:
            self.events_view.display_event(self._last_event)

        # Player action phase
        self.game_screen.display_action_phase(game_state)
        player_action = self.actions_view.prompt_action_selection(
            game_state.incumbent
        )

        if player_action is None:
            # Player quit
            return True

        # Get target states if needed
        action_def = get_action_definition(player_action)
        target_states = None

        if action_def.target_states > 0:
            target_states = self.actions_view.prompt_target_states(
                game_state,
                action_def.target_states
            )

        # Execute player action
        game_state, player_result = self.engine.execute_player_action(
            player_action,
            target_states
        )

        self.actions_view.display_action_result(player_result, is_incumbent=True)
        self._player_action_msg = player_result.message

        # AI turn
        self.game_screen.display_ai_turn(game_state)
        ai_action, ai_targets = self.ai.choose_action(game_state)

        game_state, ai_result = self.engine.execute_ai_action(
            ai_action,
            ai_targets
        )

        self.actions_view.display_action_result(ai_result, is_incumbent=False)
        self._ai_action_msg = ai_result.message

        # End turn
        game_state = self.engine.end_turn()

        # Show turn summary
        self.game_screen.display_turn_summary(
            game_state,
            self._player_action_msg,
            self._ai_action_msg
        )

        # Check if game over
        if self.engine.is_game_over():
            return True

        # Prompt to continue
        if not self.game_screen.prompt_continue():
            # End game early
            self.engine.end_game()
            return True

        return False


def main() -> None:
    """Entry point for the game."""
    try:
        game = CampaignManager()
        game.run()
    except KeyboardInterrupt:
        console.print("\n\n[warning]Campaign suspended. See you on the trail![/warning]")


if __name__ == "__main__":
    main()
