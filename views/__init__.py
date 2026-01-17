"""Views package for Campaign Manager 2026."""

from .console import console, THEME
from .setup_screen import SetupScreen
from .game_screen import GameScreen
from .map_view import MapView
from .actions_view import ActionsView
from .events_view import EventsView
from .results_screen import ResultsScreen

__all__ = [
    "console",
    "THEME",
    "SetupScreen",
    "GameScreen",
    "MapView",
    "ActionsView",
    "EventsView",
    "ResultsScreen",
]
