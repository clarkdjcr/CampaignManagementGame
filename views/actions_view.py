"""Actions view for Campaign Manager 2026."""

from typing import Optional

from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from models.actions import (
    ActionType,
    ActionDefinition,
    ActionResult,
    get_all_actions,
    get_action_definition,
)
from models.game_state import GameState
from models.player import Player
from .console import console


class ActionsView:
    """Displays and handles action selection."""

    def create_actions_table(
        self,
        player: Player,
        numbered: bool = True,
    ) -> Table:
        """Create a table showing all available actions."""
        table = Table(
            title="Available Actions",
            show_header=True,
            header_style="bold white",
            border_style="dim",
        )

        if numbered:
            table.add_column("#", justify="center", width=3)
        table.add_column("Action", style="heading", width=22)
        table.add_column("Cost", justify="right", width=6)
        table.add_column("Effect", width=40)

        actions = get_all_actions()

        for i, action in enumerate(actions, 1):
            can_afford = player.can_afford(action.cost)
            style = "action_available" if can_afford else "action_unavailable"

            # Format cost
            if action.cost == 0:
                cost_str = "Free"
            else:
                cost_str = f"${action.cost}M"

            # Format effect description
            effect = self._format_effect(action)

            row = []
            if numbered:
                row.append(f"[{style}]{i}[/{style}]")
            row.extend([
                f"[{style}]{action.name}[/{style}]",
                f"[{style}]{cost_str}[/{style}]",
                f"[{style}]{effect}[/{style}]",
            ])

            table.add_row(*row)

        return table

    def _format_effect(self, action: ActionDefinition) -> str:
        """Format action effect description."""
        parts = []

        if action.action_type == ActionType.FUNDRAISER:
            parts.append("Raises $3-6M")
        elif action.base_support_change > 0:
            if action.target_states > 0:
                parts.append(f"+{action.base_support_change}% in {action.target_states} state(s)")
            else:
                parts.append(f"+{action.base_support_change}% national")
        elif action.base_support_change < 0:
            parts.append(f"{action.base_support_change}% to opponent")

        if action.momentum_change > 0:
            parts.append(f"+{action.momentum_change} momentum")
        elif action.momentum_change < 0:
            parts.append(f"{action.momentum_change} momentum")

        return ", ".join(parts)

    def display_actions(self, player: Player) -> None:
        """Display all actions with affordability."""
        table = self.create_actions_table(player)
        console.print()
        console.print(table)

    def prompt_action_selection(
        self,
        player: Player,
    ) -> Optional[ActionType]:
        """Prompt user to select an action."""
        actions = get_all_actions()

        console.print()
        console.print("[heading]Select an action (1-7):[/heading]")

        while True:
            try:
                choice = console.input("[incumbent]> [/incumbent]").strip()

                if choice.lower() == 'q':
                    return None

                num = int(choice)
                if 1 <= num <= len(actions):
                    selected = actions[num - 1]

                    if player.can_afford(selected.cost):
                        return selected.action_type
                    else:
                        console.print(
                            f"[error]Cannot afford {selected.name} "
                            f"(need ${selected.cost}M, have {player.funds_display})[/error]"
                        )
                else:
                    console.print(f"[warning]Please enter a number 1-{len(actions)}[/warning]")

            except ValueError:
                console.print("[warning]Please enter a valid number[/warning]")

    def prompt_target_states(
        self,
        game_state: GameState,
        num_targets: int,
    ) -> list[str]:
        """Prompt user to select target states."""
        console.print()
        console.print(
            f"[heading]Select {num_targets} state(s) to target:[/heading]"
        )

        # Show available states
        states = list(game_state.states.values())
        for i, state in enumerate(states, 1):
            margin = state.margin
            if margin > 0:
                status = f"+{margin:.1f} Inc"
            elif margin < 0:
                status = f"+{abs(margin):.1f} Chl"
            else:
                status = "TIED"

            console.print(
                f"  {i:2}. {state.abbreviation} - {state.name} "
                f"({state.electoral_votes} EV) [{status}]"
            )

        selected = []
        while len(selected) < num_targets:
            remaining = num_targets - len(selected)
            console.print(f"[info]Select {remaining} more state(s) (enter number):[/info]")

            try:
                choice = console.input("[incumbent]> [/incumbent]").strip()
                num = int(choice)

                if 1 <= num <= len(states):
                    abbrev = states[num - 1].abbreviation
                    if abbrev not in selected:
                        selected.append(abbrev)
                        console.print(f"[success]Selected: {abbrev}[/success]")
                    else:
                        console.print("[warning]Already selected[/warning]")
                else:
                    console.print(f"[warning]Enter 1-{len(states)}[/warning]")

            except ValueError:
                console.print("[warning]Please enter a valid number[/warning]")

        return selected

    def display_action_result(
        self,
        result: ActionResult,
        is_incumbent: bool,
    ) -> None:
        """Display the result of an action."""
        player_type = "[incumbent]Your[/incumbent]" if is_incumbent else "[challenger]Opponent's[/challenger]"
        action_def = get_action_definition(result.action_type)

        console.print()

        if result.success:
            console.print(
                f"{player_type} [heading]{action_def.name}[/heading]: "
                f"[success]{result.message}[/success]"
            )

            if result.momentum_change != 0:
                sign = "+" if result.momentum_change > 0 else ""
                console.print(
                    f"  Momentum: {sign}{result.momentum_change}"
                )
        else:
            console.print(
                f"{player_type} [heading]{action_def.name}[/heading]: "
                f"[error]{result.message}[/error]"
            )

    def create_panel(self, player: Player) -> Panel:
        """Create a panel containing the actions view."""
        table = self.create_actions_table(player, numbered=True)

        return Panel(
            table,
            title="[title] Campaign Actions [/title]",
            border_style="cyan",
        )
