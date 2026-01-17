"""Results screen for Campaign Manager 2026."""

from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models.game_state import GameState
from engine.electoral_calculator import ElectionResult
from .console import console, clear_screen, print_divider


VICTORY_BANNER = """
██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗██╗
██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██║
██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ ██║
╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  ╚═╝
 ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   ██╗
  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝
"""

DEFEAT_BANNER = """
██████╗ ███████╗███████╗███████╗ █████╗ ████████╗
██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗╚══██╔══╝
██║  ██║█████╗  █████╗  █████╗  ███████║   ██║
██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██║   ██║
██████╔╝███████╗██║     ███████╗██║  ██║   ██║
╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝
"""


class ResultsScreen:
    """Displays the final election results."""

    def display_results(
        self,
        game_state: GameState,
        result: ElectionResult,
    ) -> None:
        """Display the full results screen."""
        clear_screen()

        # Determine if player won
        player_won = result.winner == "Incumbent"

        # Display banner
        self._display_banner(player_won, game_state)

        # Display electoral result
        self._display_electoral_summary(game_state, result)

        # Display state-by-state results
        self._display_state_results(game_state, result)

        # Display final message
        self._display_final_message(player_won, result, game_state)

    def _display_banner(self, player_won: bool, game_state: GameState) -> None:
        """Display victory or defeat banner."""
        if player_won:
            banner = VICTORY_BANNER
            style = "bold green"
            message = f"President {game_state.incumbent.name} wins re-election!"
        else:
            banner = DEFEAT_BANNER
            style = "bold red"
            message = f"{game_state.challenger.name} wins the presidency!"

        console.print()
        console.print(Align.center(Text(banner, style=style)))
        console.print()
        console.print(Align.center(Text(message, style="heading")))
        console.print()

    def _display_electoral_summary(
        self,
        game_state: GameState,
        result: ElectionResult,
    ) -> None:
        """Display the electoral vote summary."""
        # Create visual bar
        width = 60
        total = result.incumbent_evs + result.challenger_evs

        if total > 0:
            inc_width = int((result.incumbent_evs / total) * width)
        else:
            inc_width = width // 2
        chl_width = width - inc_width

        bar = Text()
        bar.append("█" * inc_width, style="blue")
        bar.append("█" * chl_width, style="red")

        # Electoral vote counts
        ev_text = Text()
        ev_text.append(f"{game_state.incumbent.name}: ", style="incumbent")
        ev_text.append(f"{result.incumbent_evs}", style="bold")
        ev_text.append(" | 270 NEEDED | ", style="dim")
        ev_text.append(f"{game_state.challenger.name}: ", style="challenger")
        ev_text.append(f"{result.challenger_evs}", style="bold")

        # Popular vote
        pop_text = Text()
        pop_text.append("Popular Vote: ", style="heading")
        pop_text.append(f"{result.incumbent_popular:.1f}%", style="incumbent")
        pop_text.append(" - ", style="dim")
        pop_text.append(f"{result.challenger_popular:.1f}%", style="challenger")

        panel = Panel(
            Align.center(
                Text.assemble(
                    bar, "\n\n",
                    ev_text, "\n",
                    pop_text,
                )
            ),
            title="[title] FINAL RESULTS [/title]",
            border_style="white",
        )

        console.print(panel)

        if result.is_landslide:
            console.print(
                Align.center(
                    Text("LANDSLIDE VICTORY!", style="bold yellow")
                )
            )

    def _display_state_results(
        self,
        game_state: GameState,
        result: ElectionResult,
    ) -> None:
        """Display state-by-state results."""
        table = Table(
            title="State-by-State Results",
            show_header=True,
            header_style="bold white",
            border_style="dim",
        )

        table.add_column("State", width=18)
        table.add_column("EVs", justify="center", width=5)
        table.add_column("Winner", justify="center", width=12)
        table.add_column("Inc %", justify="right", width=7)
        table.add_column("Chl %", justify="right", width=7)
        table.add_column("Margin", justify="right", width=8)

        # Sort by EVs (largest first)
        sorted_states = sorted(
            game_state.states.items(),
            key=lambda x: x[1].electoral_votes,
            reverse=True,
        )

        for abbrev, state in sorted_states:
            winner = result.state_results.get(abbrev, "?")
            winner_style = "incumbent" if winner == "Incumbent" else "challenger"

            margin = state.incumbent_support - state.challenger_support
            if margin > 0:
                margin_str = f"+{margin:.1f} Inc"
            elif margin < 0:
                margin_str = f"+{abs(margin):.1f} Chl"
            else:
                margin_str = "Tie"

            table.add_row(
                state.name,
                str(state.electoral_votes),
                f"[{winner_style}]{winner}[/{winner_style}]",
                f"[incumbent]{state.incumbent_support:.1f}%[/incumbent]",
                f"[challenger]{state.challenger_support:.1f}%[/challenger]",
                margin_str,
            )

        console.print()
        console.print(table)

    def _display_final_message(
        self,
        player_won: bool,
        result: ElectionResult,
        game_state: GameState,
    ) -> None:
        """Display the final message."""
        console.print()
        print_divider()
        console.print()

        if player_won:
            messages = [
                f"Congratulations, President {game_state.incumbent.name}!",
                "You have successfully defended your re-election bid.",
                f"Final margin: {result.margin} electoral votes.",
                "",
                "Thank you for playing Campaign Manager 2026!",
            ]
            style = "success"
        else:
            messages = [
                f"The voters have spoken.",
                f"{game_state.challenger.name} will be the next President.",
                f"Final margin: {abs(result.margin)} electoral votes.",
                "",
                "Better luck next campaign! Thank you for playing.",
            ]
            style = "error"

        for msg in messages:
            console.print(Align.center(Text(msg, style=style if msg else "dim")))

    def prompt_play_again(self) -> bool:
        """Ask if player wants to play again."""
        console.print()
        console.print(
            Align.center(
                Text("Play again? (y/n)", style="heading")
            )
        )
        response = console.input("> ").strip().lower()
        return response in ('y', 'yes')
