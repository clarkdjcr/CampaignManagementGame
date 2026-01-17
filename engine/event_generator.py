"""Random event generator for Campaign Manager 2026."""

import random
from typing import Optional

from models.events import (
    EventType,
    GameEvent,
    EVENT_TEMPLATES,
)
from models.game_state import GameState


class EventGenerator:
    """Generates random events during the game."""

    # Probability of an event occurring each turn (40%)
    EVENT_PROBABILITY = 0.4

    # Effect ranges by event type
    EVENT_EFFECTS = {
        EventType.SCANDAL: {"support": (-4.0, -2.0), "momentum": (-15, -5)},
        EventType.ECONOMIC: {"support": (-2.0, 2.0), "momentum": (-10, 10)},
        EventType.ENDORSEMENT: {"support": (1.5, 3.5), "momentum": (5, 15)},
        EventType.GAFFE: {"support": (-3.0, -1.0), "momentum": (-10, -5)},
        EventType.CRISIS: {"support": (-3.0, 3.0), "momentum": (-5, 15)},
        EventType.VIRAL: {"support": (1.0, 3.0), "momentum": (5, 20)},
    }

    def __init__(self):
        self._rng = random.Random()

    def seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        self._rng.seed(seed)

    def maybe_generate_event(
        self,
        game_state: GameState,
    ) -> Optional[GameEvent]:
        """
        Possibly generate a random event.

        Returns None if no event occurs (60% of the time).
        """
        if self._rng.random() > self.EVENT_PROBABILITY:
            return None

        return self.generate_event(game_state)

    def generate_event(
        self,
        game_state: GameState,
    ) -> GameEvent:
        """Generate a random event."""
        # Select random event type
        event_type = self._rng.choice(list(EventType))

        # Get template for this event type
        templates = EVENT_TEMPLATES[event_type]
        title, description = self._rng.choice(templates)

        # Determine who is affected (50/50)
        affects_incumbent = self._rng.choice([True, False])

        # Get effect ranges
        effects = self.EVENT_EFFECTS[event_type]
        support_range = effects["support"]
        momentum_range = effects["momentum"]

        # Generate random effects within ranges
        support_change = self._rng.uniform(support_range[0], support_range[1])
        momentum_change = self._rng.randint(momentum_range[0], momentum_range[1])

        # Determine affected states (30% chance of being state-specific)
        affected_states = []
        if self._rng.random() < 0.3:
            # Pick 1-3 random states
            num_states = self._rng.randint(1, 3)
            state_abbrevs = list(game_state.states.keys())
            affected_states = self._rng.sample(
                state_abbrevs,
                min(num_states, len(state_abbrevs))
            )

        return GameEvent(
            event_type=event_type,
            title=title,
            description=description,
            affects_incumbent=affects_incumbent,
            support_change=round(support_change, 1),
            momentum_change=momentum_change,
            affected_states=affected_states,
            turn_occurred=game_state.current_turn,
        )

    def apply_event(
        self,
        game_state: GameState,
        event: GameEvent,
    ) -> GameState:
        """Apply an event's effects to the game state."""
        # Update player momentum
        if event.affects_incumbent:
            new_incumbent = game_state.incumbent.adjust_momentum(event.momentum_change)
            new_challenger = game_state.challenger
        else:
            new_incumbent = game_state.incumbent
            new_challenger = game_state.challenger.adjust_momentum(event.momentum_change)

        # Update state support
        new_states = game_state.states.copy()

        if event.is_national:
            # Apply to all states with reduced effect
            effect = event.support_change * 0.5
            for abbrev, state in new_states.items():
                if event.affects_incumbent:
                    new_states[abbrev] = state.apply_support_change(
                        incumbent_change=effect
                    )
                else:
                    new_states[abbrev] = state.apply_support_change(
                        challenger_change=effect
                    )
        else:
            # Apply full effect to specific states
            for abbrev in event.affected_states:
                if abbrev in new_states:
                    state = new_states[abbrev]
                    if event.affects_incumbent:
                        new_states[abbrev] = state.apply_support_change(
                            incumbent_change=event.support_change
                        )
                    else:
                        new_states[abbrev] = state.apply_support_change(
                            challenger_change=event.support_change
                        )

        # Add event to log
        new_events_log = game_state.events_log.copy()
        new_events_log.append(event)

        return GameState(
            incumbent=new_incumbent,
            challenger=new_challenger,
            states=new_states,
            current_turn=game_state.current_turn,
            max_turns=game_state.max_turns,
            events_log=new_events_log,
            game_over=game_state.game_over,
            winner=game_state.winner,
        )

    def generate_crisis_event(
        self,
        game_state: GameState,
        affects_incumbent: bool,
    ) -> GameEvent:
        """Generate a specific crisis event (for testing/special scenarios)."""
        templates = EVENT_TEMPLATES[EventType.CRISIS]
        title, description = self._rng.choice(templates)

        effects = self.EVENT_EFFECTS[EventType.CRISIS]
        support_change = self._rng.uniform(effects["support"][0], effects["support"][1])
        momentum_change = self._rng.randint(effects["momentum"][0], effects["momentum"][1])

        return GameEvent(
            event_type=EventType.CRISIS,
            title=title,
            description=description,
            affects_incumbent=affects_incumbent,
            support_change=round(support_change, 1),
            momentum_change=momentum_change,
            affected_states=[],
            turn_occurred=game_state.current_turn,
        )
