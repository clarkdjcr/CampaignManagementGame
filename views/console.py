"""Rich console configuration and theme for Campaign Manager 2026."""

from rich.console import Console
from rich.theme import Theme

# Custom theme for the game
THEME = Theme({
    # Player colors
    "incumbent": "bold blue",
    "challenger": "bold red",

    # State lean colors
    "safe_inc": "blue",
    "lean_inc": "cyan",
    "tossup": "yellow",
    "lean_chl": "magenta",
    "safe_chl": "red",

    # UI elements
    "title": "bold white on blue",
    "subtitle": "bold cyan",
    "heading": "bold white",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "dim white",

    # Game elements
    "money": "bold green",
    "momentum_high": "bold green",
    "momentum_low": "bold red",
    "momentum_neutral": "yellow",
    "turn": "bold magenta",
    "ev_count": "bold white",

    # Events
    "event_good": "green",
    "event_bad": "red",
    "event_neutral": "yellow",

    # Actions
    "action_available": "green",
    "action_unavailable": "dim red",
})

# Global console instance
console = Console(theme=THEME)


def get_lean_style(lean: str) -> str:
    """Get the style for a state's lean."""
    lean_lower = lean.lower()
    if "safe" in lean_lower and "inc" in lean_lower:
        return "safe_inc"
    elif "lean" in lean_lower and "inc" in lean_lower:
        return "lean_inc"
    elif "safe" in lean_lower and "chl" in lean_lower:
        return "safe_chl"
    elif "lean" in lean_lower and "chl" in lean_lower:
        return "lean_chl"
    else:
        return "tossup"


def get_momentum_style(momentum: int) -> str:
    """Get the style for momentum display."""
    if momentum >= 20:
        return "momentum_high"
    elif momentum <= -20:
        return "momentum_low"
    else:
        return "momentum_neutral"


def format_money(amount: int) -> str:
    """Format money for display."""
    return f"[money]${amount}M[/money]"


def format_momentum(momentum: int) -> str:
    """Format momentum for display."""
    style = get_momentum_style(momentum)
    sign = "+" if momentum > 0 else ""
    return f"[{style}]{sign}{momentum}[/{style}]"


def format_ev_count(evs: int, total: int = 538) -> str:
    """Format electoral vote count."""
    return f"[ev_count]{evs}[/ev_count]/{total}"


def clear_screen() -> None:
    """Clear the console screen."""
    console.clear()


def print_divider(char: str = "─", style: str = "dim") -> None:
    """Print a horizontal divider."""
    width = console.width
    console.print(f"[{style}]{char * width}[/{style}]")
