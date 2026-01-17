"""Setup screen for Campaign Manager 2026."""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from .console import console, clear_screen, print_divider


ASCII_TITLE = """
   ____                            _               __  __
  / ___|__ _ _ __ ___  _ __   __ _(_) __ _ _ __   |  \\/  | __ _ _ __   __ _  __ _  ___ _ __
 | |   / _` | '_ ` _ \\| '_ \\ / _` | |/ _` | '_ \\  | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|
 | |__| (_| | | | | | | |_) | (_| | | (_| | | | | | |  | | (_| | | | | (_| | (_| |  __/ |
  \\____\\__,_|_| |_| |_| .__/ \\__,_|_|\\__, |_| |_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|
                      |_|            |___/                                  |___/
                                      ___   ___ ___   __
                                     |__ \\ / _ \\__ \\ / /_
                                        ) | | | | ) | '_ \\
                                       / /| |_| |/ /| (_) |
                                      |____\\___/____\\___/
"""


class SetupScreen:
    """Welcome and configuration screen."""

    def display_title(self) -> None:
        """Display the game title."""
        clear_screen()
        console.print()
        console.print(
            Align.center(
                Text(ASCII_TITLE, style="bold blue")
            )
        )
        console.print()

    def display_rules(self) -> None:
        """Display the game rules."""
        rules_text = """
[heading]OBJECTIVE[/heading]
Win the presidential election by securing [ev_count]270[/ev_count] electoral votes.
You are the [incumbent]INCUMBENT[/incumbent] facing a [challenger]CHALLENGER[/challenger].

[heading]GAMEPLAY[/heading]
- The campaign runs for [turn]20 turns[/turn]
- Each turn, you take one action to influence the race
- Random events may occur, affecting polling and momentum
- The AI opponent will counter your moves strategically

[heading]RESOURCES[/heading]
- [money]Campaign Funds[/money]: Spend wisely on rallies, ads, and research
- [momentum_high]Momentum[/momentum_high]: Affects the power of your actions (-100 to +100)

[heading]ACTIONS[/heading]
- [heading]Fundraiser[/heading]: Raise $3-6M (slight momentum loss)
- [heading]Rally[/heading]: +3% support in 1 state ($2M)
- [heading]Ad Campaign[/heading]: +2% support in 3 states ($4M)
- [heading]Grassroots[/heading]: +1.5% support in 2 states ($1M)
- [heading]Debate Prep[/heading]: +10 momentum ($1M)
- [heading]Opposition Research[/heading]: -2.5% opponent support nationally ($3M)
- [heading]Media Blitz[/heading]: +1.5% support nationally, +8 momentum ($3M)

[heading]WINNING[/heading]
After 20 turns, electoral votes are tallied. Win 270+ to secure victory!
"""
        panel = Panel(
            rules_text,
            title="[title] HOW TO PLAY [/title]",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(Align.center(panel))

    def get_player_name(self) -> str:
        """Prompt for and return the player's name."""
        print_divider()
        console.print()
        console.print(
            Align.center("[heading]Enter your candidate's name:[/heading]")
        )
        console.print()

        while True:
            name = console.input("[incumbent]> [/incumbent]").strip()
            if name:
                return name
            console.print("[warning]Please enter a name.[/warning]")

    def confirm_start(self) -> bool:
        """Confirm the player wants to start the game."""
        console.print()
        console.print(
            Align.center("[info]Press Enter to start the campaign, or 'q' to quit[/info]")
        )
        response = console.input("> ").strip().lower()
        return response != 'q'

    def run(self) -> tuple[bool, str]:
        """
        Run the setup screen flow.

        Returns:
            Tuple of (should_start, player_name)
        """
        self.display_title()
        self.display_rules()

        player_name = self.get_player_name()

        console.print()
        console.print(
            Align.center(
                f"[success]Welcome, President {player_name}![/success]"
            )
        )
        console.print(
            Align.center(
                "[info]Your re-election campaign begins now.[/info]"
            )
        )

        if self.confirm_start():
            return True, player_name
        return False, player_name
