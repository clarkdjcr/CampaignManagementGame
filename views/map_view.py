"""Electoral map view for Campaign Manager 2026."""

from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from models.game_state import GameState
from models.state import State
from .console import console, get_lean_style


class MapView:
    """Displays the electoral map as a table."""

    def create_polling_bar(
        self,
        incumbent: float,
        challenger: float,
        width: int = 20,
    ) -> Text:
        """Create a visual polling bar."""
        # Calculate proportions
        total = incumbent + challenger
        if total == 0:
            inc_width = width // 2
            chl_width = width // 2
        else:
            inc_width = int((incumbent / total) * width)
            chl_width = width - inc_width

        bar = Text()
        bar.append("█" * inc_width, style="blue")
        bar.append("█" * chl_width, style="red")

        return bar

    def create_map_table(self, game_state: GameState) -> Table:
        """Create the electoral map table."""
        table = Table(
            title="Electoral Map",
            show_header=True,
            header_style="bold white",
            border_style="dim",
        )

        table.add_column("State", style="heading", width=18)
        table.add_column("EVs", justify="center", width=5)
        table.add_column("Inc %", justify="right", width=6)
        table.add_column("Chl %", justify="right", width=6)
        table.add_column("Polling", justify="center", width=22)
        table.add_column("Status", justify="center", width=10)

        # Sort states by competitiveness (closest races first)
        sorted_states = sorted(
            game_state.states.values(),
            key=lambda s: abs(s.margin),
        )

        for state in sorted_states:
            lean_style = get_lean_style(state.lean)
            polling_bar = self.create_polling_bar(
                state.incumbent_support,
                state.challenger_support,
            )

            # Determine status text and style
            margin = state.margin
            if margin > 0:
                status = f"+{margin:.1f} Inc"
                status_style = "incumbent"
            elif margin < 0:
                status = f"+{abs(margin):.1f} Chl"
                status_style = "challenger"
            else:
                status = "TIED"
                status_style = "tossup"

            table.add_row(
                f"{state.name}",
                f"[{lean_style}]{state.electoral_votes}[/{lean_style}]",
                f"[incumbent]{state.incumbent_support:.1f}[/incumbent]",
                f"[challenger]{state.challenger_support:.1f}[/challenger]",
                polling_bar,
                f"[{status_style}]{status}[/{status_style}]",
            )

        return table

    def create_ev_summary(self, game_state: GameState) -> Text:
        """Create electoral vote summary bar."""
        inc_evs = game_state.incumbent_electoral_votes
        chl_evs = game_state.challenger_electoral_votes
        tied_evs = game_state.tied_electoral_votes
        total = game_state.total_electoral_votes

        text = Text()
        text.append("Electoral Votes: ", style="heading")
        text.append(f"{inc_evs}", style="incumbent")
        text.append(" - ", style="dim")
        text.append(f"{chl_evs}", style="challenger")

        if tied_evs > 0:
            text.append(f" ({tied_evs} tied)", style="tossup")

        text.append(f" | 270 needed to win", style="info")

        return text

    def create_ev_bar(self, game_state: GameState, width: int = 50) -> Text:
        """Create a visual electoral vote bar."""
        inc_evs = game_state.incumbent_electoral_votes
        chl_evs = game_state.challenger_electoral_votes
        total = game_state.total_electoral_votes

        # Calculate proportions
        inc_width = int((inc_evs / total) * width)
        chl_width = int((chl_evs / total) * width)
        tied_width = width - inc_width - chl_width

        # Calculate 270 marker position
        marker_pos = int((270 / total) * width)

        bar = Text()

        # Build the bar character by character
        for i in range(width):
            if i == marker_pos:
                bar.append("│", style="bold white")
            elif i < inc_width:
                bar.append("█", style="blue")
            elif i < inc_width + tied_width:
                bar.append("░", style="yellow")
            else:
                bar.append("█", style="red")

        return bar

    def display(self, game_state: GameState) -> None:
        """Display the full electoral map view."""
        console.print()

        # EV Summary
        console.print(self.create_ev_summary(game_state))

        # EV Bar
        console.print()
        console.print(self.create_ev_bar(game_state))
        console.print()

        # Map Table
        table = self.create_map_table(game_state)
        console.print(table)

    def create_panel(self, game_state: GameState) -> Panel:
        """Create a panel containing the map view."""
        table = self.create_map_table(game_state)

        return Panel(
            table,
            title="[title] Electoral Map [/title]",
            border_style="blue",
        )
