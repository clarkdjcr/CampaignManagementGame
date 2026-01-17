"""Main game screen for Campaign Manager 2026."""

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

from models.game_state import GameState
from models.player import Player
from .console import console, clear_screen, print_divider, format_money, format_momentum
from .map_view import MapView
from .actions_view import ActionsView
from .events_view import EventsView


class GameScreen:
    """Main game screen with all UI components."""

    def __init__(self):
        self.map_view = MapView()
        self.actions_view = ActionsView()
        self.events_view = EventsView()

    def create_header(self, game_state: GameState) -> Panel:
        """Create the game header with turn info."""
        turn_text = Text()
        turn_text.append("CAMPAIGN MANAGER 2026", style="title")
        turn_text.append(" | ", style="dim")
        turn_text.append(f"Turn {game_state.current_turn}", style="turn")
        turn_text.append(f"/{game_state.max_turns}", style="dim")
        turn_text.append(" | ", style="dim")
        turn_text.append(f"{game_state.turns_remaining} turns remaining", style="info")

        return Panel(
            Align.center(turn_text),
            border_style="blue",
        )

    def create_player_stats(self, player: Player, evs: int) -> Panel:
        """Create a panel showing player stats."""
        style = "incumbent" if player.is_incumbent else "challenger"
        role = "Incumbent" if player.is_incumbent else "Challenger"

        stats = Table.grid(padding=1)
        stats.add_column(justify="right")
        stats.add_column(justify="left")

        stats.add_row("Candidate:", f"[{style}]{player.name}[/{style}]")
        stats.add_row("Role:", f"[{style}]{role}[/{style}]")
        stats.add_row("Funds:", format_money(player.funds))
        stats.add_row("Momentum:", format_momentum(player.momentum))
        stats.add_row("Electoral Votes:", f"[ev_count]{evs}[/ev_count]")

        return Panel(
            stats,
            title=f"[{style}] {player.name} [/{style}]",
            border_style=style,
        )

    def create_ev_bar_footer(self, game_state: GameState) -> Panel:
        """Create the electoral vote bar footer."""
        inc_evs = game_state.incumbent_electoral_votes
        chl_evs = game_state.challenger_electoral_votes
        total = game_state.total_electoral_votes

        # Calculate bar widths
        width = 60
        inc_width = int((inc_evs / total) * width)
        chl_width = int((chl_evs / total) * width)
        tied_width = width - inc_width - chl_width

        # Build the bar
        bar = Text()
        bar.append("█" * inc_width, style="blue")
        bar.append("░" * tied_width, style="yellow")
        bar.append("█" * chl_width, style="red")

        # Add labels
        label = Text()
        label.append(f"{game_state.incumbent.name}: ", style="incumbent")
        label.append(f"{inc_evs} EV", style="ev_count")
        label.append("  |  ", style="dim")
        label.append("270 to win", style="heading")
        label.append("  |  ", style="dim")
        label.append(f"{game_state.challenger.name}: ", style="challenger")
        label.append(f"{chl_evs} EV", style="ev_count")

        content = Text()
        content.append_text(bar)
        content.append("\n")
        content.append_text(label)

        return Panel(
            Align.center(content),
            border_style="dim",
        )

    def display_full_screen(self, game_state: GameState) -> None:
        """Display the full game screen."""
        clear_screen()

        # Header
        console.print(self.create_header(game_state))

        # Player stats side by side
        inc_evs = game_state.incumbent_electoral_votes
        chl_evs = game_state.challenger_electoral_votes

        player_panels = Columns([
            self.create_player_stats(game_state.incumbent, inc_evs),
            self.create_player_stats(game_state.challenger, chl_evs),
        ], equal=True, expand=True)

        console.print(player_panels)

        # EV Bar
        console.print(self.create_ev_bar_footer(game_state))

        # Map
        self.map_view.display(game_state)

    def display_turn_start(self, game_state: GameState) -> None:
        """Display the turn start screen."""
        self.display_full_screen(game_state)
        print_divider()
        console.print(
            f"\n[turn]Turn {game_state.current_turn}[/turn] begins.\n",
            style="heading"
        )

    def display_action_phase(self, game_state: GameState) -> None:
        """Display the action selection phase."""
        console.print()
        console.print(
            f"[heading]Your campaign has [/heading][money]${game_state.incumbent.funds}M[/money]"
            f"[heading] available.[/heading]"
        )
        self.actions_view.display_actions(game_state.incumbent)

    def display_ai_turn(self, game_state: GameState) -> None:
        """Display AI turn indicator."""
        console.print()
        console.print(
            f"[challenger]{game_state.challenger.name}[/challenger] "
            f"[info]is making their move...[/info]"
        )

    def display_turn_summary(
        self,
        game_state: GameState,
        player_action_msg: str,
        ai_action_msg: str,
    ) -> None:
        """Display end of turn summary."""
        print_divider()
        console.print()
        console.print("[heading]Turn Summary[/heading]")
        console.print(f"  Your action: {player_action_msg}")
        console.print(f"  Opponent's action: {ai_action_msg}")

        # Show updated EV count
        inc_evs = game_state.incumbent_electoral_votes
        chl_evs = game_state.challenger_electoral_votes

        console.print()
        console.print(
            f"  Electoral Votes: "
            f"[incumbent]{inc_evs}[/incumbent] - "
            f"[challenger]{chl_evs}[/challenger]"
        )

    def prompt_continue(self) -> bool:
        """Prompt user to continue to next turn."""
        console.print()
        console.print("[info]Press Enter to continue (or 'q' to quit)...[/info]")
        response = console.input("> ").strip().lower()
        return response != 'q'

    def display_events_log(self, game_state: GameState) -> None:
        """Display the events log panel."""
        console.print()
        console.print(self.events_view.create_panel(game_state))
