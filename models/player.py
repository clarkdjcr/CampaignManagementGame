"""Player model for tracking campaign resources."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Player:
    """Represents a campaign (player or AI)."""
    name: str
    is_incumbent: bool
    funds: int = 15  # in millions
    momentum: int = 0  # -100 to +100
    is_human: bool = True

    # Constraints
    MIN_MOMENTUM: int = field(default=-100, repr=False)
    MAX_MOMENTUM: int = field(default=100, repr=False)

    @property
    def momentum_modifier(self) -> float:
        """
        Calculate momentum modifier for action effectiveness.
        Scales from 0.5x (at -100) to 1.5x (at +100).
        """
        # Linear scale: -100 -> 0.5, 0 -> 1.0, +100 -> 1.5
        return 1.0 + (self.momentum / 200.0)

    @property
    def momentum_description(self) -> str:
        """Get a description of current momentum."""
        if self.momentum >= 50:
            return "Surging"
        elif self.momentum >= 20:
            return "Rising"
        elif self.momentum >= -20:
            return "Steady"
        elif self.momentum >= -50:
            return "Falling"
        else:
            return "Collapsing"

    @property
    def funds_display(self) -> str:
        """Format funds for display."""
        return f"${self.funds}M"

    def can_afford(self, cost: int) -> bool:
        """Check if player can afford an action."""
        return self.funds >= cost

    def spend_funds(self, amount: int) -> "Player":
        """Spend funds and return new player state."""
        if amount > self.funds:
            raise ValueError(f"Cannot spend ${amount}M, only have ${self.funds}M")
        return Player(
            name=self.name,
            is_incumbent=self.is_incumbent,
            funds=self.funds - amount,
            momentum=self.momentum,
            is_human=self.is_human,
        )

    def add_funds(self, amount: int) -> "Player":
        """Add funds and return new player state."""
        return Player(
            name=self.name,
            is_incumbent=self.is_incumbent,
            funds=self.funds + amount,
            momentum=self.momentum,
            is_human=self.is_human,
        )

    def adjust_momentum(self, change: int) -> "Player":
        """Adjust momentum and return new player state."""
        new_momentum = max(
            self.MIN_MOMENTUM,
            min(self.MAX_MOMENTUM, self.momentum + change)
        )
        return Player(
            name=self.name,
            is_incumbent=self.is_incumbent,
            funds=self.funds,
            momentum=new_momentum,
            is_human=self.is_human,
        )

    def update(
        self,
        funds_change: int = 0,
        momentum_change: int = 0
    ) -> "Player":
        """Apply multiple changes and return new player state."""
        new_funds = max(0, self.funds + funds_change)
        new_momentum = max(
            self.MIN_MOMENTUM,
            min(self.MAX_MOMENTUM, self.momentum + momentum_change)
        )
        return Player(
            name=self.name,
            is_incumbent=self.is_incumbent,
            funds=new_funds,
            momentum=new_momentum,
            is_human=self.is_human,
        )

    def __str__(self) -> str:
        role = "Incumbent" if self.is_incumbent else "Challenger"
        return f"{self.name} ({role}): {self.funds_display}, Momentum: {self.momentum}"
