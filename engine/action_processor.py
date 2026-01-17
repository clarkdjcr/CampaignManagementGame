"""Action processor for executing player actions."""

import random
from typing import Optional

from models.actions import (
    ActionType,
    ActionDefinition,
    ActionResult,
    get_action_definition,
)
from models.game_state import GameState
from models.player import Player
from models.state import State


class ActionProcessor:
    """Processes and executes player actions."""

    # Fundraiser generates $3-6M
    FUNDRAISER_MIN = 3
    FUNDRAISER_MAX = 6

    def __init__(self):
        self._rng = random.Random()

    def seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        self._rng.seed(seed)

    def execute_action(
        self,
        game_state: GameState,
        action_type: ActionType,
        is_incumbent: bool,
        target_states: Optional[list[str]] = None,
    ) -> tuple[GameState, ActionResult]:
        """
        Execute an action and return updated game state and result.

        Args:
            game_state: Current game state
            action_type: Type of action to execute
            is_incumbent: True if incumbent is taking action
            target_states: Optional list of state abbreviations to target

        Returns:
            Tuple of (new_game_state, action_result)
        """
        definition = get_action_definition(action_type)
        player = game_state.incumbent if is_incumbent else game_state.challenger

        # Check if player can afford action
        if not player.can_afford(definition.cost):
            return game_state, ActionResult(
                action_type=action_type,
                success=False,
                message=f"Cannot afford {definition.name} (need ${definition.cost}M, have {player.funds_display})",
                funds_spent=0,
                funds_raised=0,
                support_changes={},
                momentum_change=0,
                affected_states=[],
            )

        # Handle fundraiser specially
        if action_type == ActionType.FUNDRAISER:
            return self._execute_fundraiser(game_state, is_incumbent, definition)

        # Handle opposition research (affects opponent)
        if action_type == ActionType.OPPOSITION_RESEARCH:
            return self._execute_opposition_research(game_state, is_incumbent, definition)

        # Handle targeted actions
        if definition.target_states > 0:
            return self._execute_targeted_action(
                game_state, is_incumbent, definition, target_states
            )

        # Handle national actions (media blitz, debate prep)
        return self._execute_national_action(game_state, is_incumbent, definition)

    def _execute_fundraiser(
        self,
        game_state: GameState,
        is_incumbent: bool,
        definition: ActionDefinition,
    ) -> tuple[GameState, ActionResult]:
        """Execute a fundraising action."""
        funds_raised = self._rng.randint(self.FUNDRAISER_MIN, self.FUNDRAISER_MAX)
        player = game_state.incumbent if is_incumbent else game_state.challenger

        new_player = player.update(
            funds_change=funds_raised,
            momentum_change=definition.momentum_change,
        )

        if is_incumbent:
            new_state = game_state.with_players(incumbent=new_player)
        else:
            new_state = game_state.with_players(challenger=new_player)

        return new_state, ActionResult(
            action_type=ActionType.FUNDRAISER,
            success=True,
            message=f"Fundraiser raised ${funds_raised}M!",
            funds_spent=0,
            funds_raised=funds_raised,
            support_changes={},
            momentum_change=definition.momentum_change,
            affected_states=[],
        )

    def _execute_opposition_research(
        self,
        game_state: GameState,
        is_incumbent: bool,
        definition: ActionDefinition,
    ) -> tuple[GameState, ActionResult]:
        """Execute opposition research (hurts opponent nationally)."""
        player = game_state.incumbent if is_incumbent else game_state.challenger
        new_player = player.update(
            funds_change=-definition.cost,
            momentum_change=definition.momentum_change,
        )

        # Apply negative effect to all states for opponent
        support_changes = {}
        new_states = game_state.states.copy()

        # Calculate effectiveness based on player's momentum
        effectiveness = player.momentum_modifier
        effect = definition.base_support_change * effectiveness

        for abbrev, state in new_states.items():
            if is_incumbent:
                # Hurt challenger support
                new_states[abbrev] = state.apply_support_change(
                    challenger_change=effect  # negative value hurts opponent
                )
            else:
                # Hurt incumbent support
                new_states[abbrev] = state.apply_support_change(
                    incumbent_change=effect
                )
            support_changes[abbrev] = effect

        if is_incumbent:
            new_game_state = GameState(
                incumbent=new_player,
                challenger=game_state.challenger,
                states=new_states,
                current_turn=game_state.current_turn,
                max_turns=game_state.max_turns,
                events_log=game_state.events_log,
                game_over=game_state.game_over,
                winner=game_state.winner,
            )
        else:
            new_game_state = GameState(
                incumbent=game_state.incumbent,
                challenger=new_player,
                states=new_states,
                current_turn=game_state.current_turn,
                max_turns=game_state.max_turns,
                events_log=game_state.events_log,
                game_over=game_state.game_over,
                winner=game_state.winner,
            )

        return new_game_state, ActionResult(
            action_type=ActionType.OPPOSITION_RESEARCH,
            success=True,
            message=f"Opposition research damages opponent by {abs(effect):.1f}% nationally",
            funds_spent=definition.cost,
            funds_raised=0,
            support_changes=support_changes,
            momentum_change=definition.momentum_change,
            affected_states=list(new_states.keys()),
        )

    def _execute_targeted_action(
        self,
        game_state: GameState,
        is_incumbent: bool,
        definition: ActionDefinition,
        target_states: Optional[list[str]],
    ) -> tuple[GameState, ActionResult]:
        """Execute an action targeting specific states."""
        player = game_state.incumbent if is_incumbent else game_state.challenger

        # Select target states if not provided
        if not target_states:
            target_states = self._select_target_states(
                game_state, is_incumbent, definition.target_states
            )

        # Limit to allowed number of targets
        target_states = target_states[: definition.target_states]

        new_player = player.update(
            funds_change=-definition.cost,
            momentum_change=definition.momentum_change,
        )

        # Apply effects to targeted states
        support_changes = {}
        new_states = game_state.states.copy()

        effectiveness = player.momentum_modifier
        effect = definition.base_support_change * effectiveness

        for abbrev in target_states:
            if abbrev in new_states:
                state = new_states[abbrev]
                if is_incumbent:
                    new_states[abbrev] = state.apply_support_change(
                        incumbent_change=effect
                    )
                else:
                    new_states[abbrev] = state.apply_support_change(
                        challenger_change=effect
                    )
                support_changes[abbrev] = effect

        if is_incumbent:
            new_game_state = GameState(
                incumbent=new_player,
                challenger=game_state.challenger,
                states=new_states,
                current_turn=game_state.current_turn,
                max_turns=game_state.max_turns,
                events_log=game_state.events_log,
                game_over=game_state.game_over,
                winner=game_state.winner,
            )
        else:
            new_game_state = GameState(
                incumbent=game_state.incumbent,
                challenger=new_player,
                states=new_states,
                current_turn=game_state.current_turn,
                max_turns=game_state.max_turns,
                events_log=game_state.events_log,
                game_over=game_state.game_over,
                winner=game_state.winner,
            )

        return new_game_state, ActionResult(
            action_type=definition.action_type,
            success=True,
            message=f"{definition.name} boosted support by {effect:.1f}% in {', '.join(target_states)}",
            funds_spent=definition.cost,
            funds_raised=0,
            support_changes=support_changes,
            momentum_change=definition.momentum_change,
            affected_states=target_states,
        )

    def _execute_national_action(
        self,
        game_state: GameState,
        is_incumbent: bool,
        definition: ActionDefinition,
    ) -> tuple[GameState, ActionResult]:
        """Execute a national action affecting all states."""
        player = game_state.incumbent if is_incumbent else game_state.challenger

        new_player = player.update(
            funds_change=-definition.cost,
            momentum_change=definition.momentum_change,
        )

        # Apply smaller effect to all states
        support_changes = {}
        new_states = game_state.states.copy()

        effectiveness = player.momentum_modifier
        # National actions have reduced per-state effect
        effect = (definition.base_support_change * effectiveness) * 0.5

        for abbrev, state in new_states.items():
            if is_incumbent:
                new_states[abbrev] = state.apply_support_change(
                    incumbent_change=effect
                )
            else:
                new_states[abbrev] = state.apply_support_change(
                    challenger_change=effect
                )
            support_changes[abbrev] = effect

        if is_incumbent:
            new_game_state = GameState(
                incumbent=new_player,
                challenger=game_state.challenger,
                states=new_states,
                current_turn=game_state.current_turn,
                max_turns=game_state.max_turns,
                events_log=game_state.events_log,
                game_over=game_state.game_over,
                winner=game_state.winner,
            )
        else:
            new_game_state = GameState(
                incumbent=game_state.incumbent,
                challenger=new_player,
                states=new_states,
                current_turn=game_state.current_turn,
                max_turns=game_state.max_turns,
                events_log=game_state.events_log,
                game_over=game_state.game_over,
                winner=game_state.winner,
            )

        return new_game_state, ActionResult(
            action_type=definition.action_type,
            success=True,
            message=f"{definition.name} boosted national support by {effect:.1f}%",
            funds_spent=definition.cost,
            funds_raised=0,
            support_changes=support_changes,
            momentum_change=definition.momentum_change,
            affected_states=list(new_states.keys()),
        )

    def _select_target_states(
        self,
        game_state: GameState,
        is_incumbent: bool,
        count: int,
    ) -> list[str]:
        """Select the best states to target based on competitiveness."""
        # Prioritize competitive states
        states_by_margin = sorted(
            game_state.states.items(),
            key=lambda x: abs(x[1].margin),
        )

        # Return closest races
        return [abbrev for abbrev, _ in states_by_margin[:count]]

    def get_affordable_actions(
        self,
        player: Player,
    ) -> list[ActionDefinition]:
        """Get list of actions the player can afford."""
        from models.actions import get_all_actions

        return [a for a in get_all_actions() if player.can_afford(a.cost)]
