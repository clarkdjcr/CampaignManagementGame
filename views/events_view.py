"""Events view for Campaign Manager 2026."""

from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from models.events import GameEvent, EventType
from models.game_state import GameState
from .console import console


class EventsView:
    """Displays game events and event log."""

    def get_event_style(self, event: GameEvent, for_incumbent: bool) -> str:
        """Get style for an event based on its effect on the player."""
        # Positive support change is good, negative is bad
        if event.affects_incumbent == for_incumbent:
            # Event affects the player we're viewing
            if event.support_change > 0:
                return "event_good"
            elif event.support_change < 0:
                return "event_bad"
        else:
            # Event affects opponent
            if event.support_change > 0:
                return "event_bad"  # Good for opponent = bad for player
            elif event.support_change < 0:
                return "event_good"  # Bad for opponent = good for player

        return "event_neutral"

    def get_event_icon(self, event_type: EventType) -> str:
        """Get an icon for the event type."""
        icons = {
            EventType.SCANDAL: "!",
            EventType.ECONOMIC: "$",
            EventType.ENDORSEMENT: "+",
            EventType.GAFFE: "?",
            EventType.CRISIS: "*",
            EventType.VIRAL: "@",
        }
        return icons.get(event_type, "·")

    def display_event(self, event: GameEvent) -> None:
        """Display a single event announcement."""
        # Determine who is affected
        affected = "Incumbent" if event.affects_incumbent else "Challenger"
        style = "incumbent" if event.affects_incumbent else "challenger"

        # Build effect description
        effects = []
        if event.support_change > 0:
            effects.append(f"+{event.support_change}% support")
        elif event.support_change < 0:
            effects.append(f"{event.support_change}% support")

        if event.momentum_change > 0:
            effects.append(f"+{event.momentum_change} momentum")
        elif event.momentum_change < 0:
            effects.append(f"{event.momentum_change} momentum")

        effect_str = ", ".join(effects) if effects else "No direct effect"

        # State targeting
        if event.affected_states:
            scope = f"in {', '.join(event.affected_states)}"
        else:
            scope = "nationally"

        console.print()
        console.print(
            Panel(
                f"[heading]{event.title}[/heading]\n\n"
                f"{event.description}\n\n"
                f"Affects: [{style}]{affected}[/{style}] {scope}\n"
                f"Impact: {effect_str}",
                title=f"[warning] BREAKING NEWS - Turn {event.turn_occurred} [/warning]",
                border_style="yellow",
            )
        )

    def create_events_table(
        self,
        events: list[GameEvent],
        max_events: int = 10,
    ) -> Table:
        """Create a table showing recent events."""
        table = Table(
            show_header=True,
            header_style="bold white",
            border_style="dim",
        )

        table.add_column("Turn", justify="center", width=5)
        table.add_column("Event", width=25)
        table.add_column("Target", justify="center", width=10)
        table.add_column("Effect", width=20)

        # Show most recent events first
        recent = events[-max_events:][::-1]

        for event in recent:
            icon = self.get_event_icon(event.event_type)
            target = "Inc" if event.affects_incumbent else "Chl"
            target_style = "incumbent" if event.affects_incumbent else "challenger"

            # Format effect
            effect_parts = []
            if event.support_change != 0:
                sign = "+" if event.support_change > 0 else ""
                effect_parts.append(f"{sign}{event.support_change}%")
            if event.momentum_change != 0:
                sign = "+" if event.momentum_change > 0 else ""
                effect_parts.append(f"{sign}{event.momentum_change}M")

            effect = " / ".join(effect_parts) if effect_parts else "-"

            # Style based on whether good or bad
            if event.support_change > 0:
                effect_style = "event_good" if event.affects_incumbent else "event_bad"
            elif event.support_change < 0:
                effect_style = "event_bad" if event.affects_incumbent else "event_good"
            else:
                effect_style = "event_neutral"

            table.add_row(
                str(event.turn_occurred),
                f"{icon} {event.title}",
                f"[{target_style}]{target}[/{target_style}]",
                f"[{effect_style}]{effect}[/{effect_style}]",
            )

        return table

    def display_events_log(self, game_state: GameState) -> None:
        """Display the recent events log."""
        if not game_state.events_log:
            console.print("[info]No events yet.[/info]")
            return

        table = self.create_events_table(game_state.events_log)
        console.print()
        console.print(table)

    def create_panel(self, game_state: GameState) -> Panel:
        """Create a panel containing the events log."""
        if not game_state.events_log:
            content = Text("No events yet.", style="info")
        else:
            content = self.create_events_table(game_state.events_log)

        return Panel(
            content,
            title="[title] Recent Events [/title]",
            border_style="yellow",
        )
