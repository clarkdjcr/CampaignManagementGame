"""State model for tracking electoral state data."""

from dataclasses import dataclass


@dataclass
class State:
    """Represents a US state in the election."""
    name: str
    abbreviation: str
    electoral_votes: int
    incumbent_support: float  # 0-100 percentage
    challenger_support: float  # 0-100 percentage
    lean: str  # "Safe D", "Lean D", "Tossup", "Lean R", "Safe R"
    region: str  # "Northeast", "South", "Midwest", "West"

    @property
    def undecided(self) -> float:
        """Calculate undecided voters."""
        return max(0.0, 100.0 - self.incumbent_support - self.challenger_support)

    @property
    def margin(self) -> float:
        """Calculate margin (positive = incumbent leads)."""
        return self.incumbent_support - self.challenger_support

    @property
    def leader(self) -> str:
        """Get current leader."""
        if self.margin > 0:
            return "Incumbent"
        elif self.margin < 0:
            return "Challenger"
        return "Tied"

    @property
    def competitive(self) -> bool:
        """Check if state is competitive (within 10 points)."""
        return abs(self.margin) <= 10.0

    def apply_support_change(
        self,
        incumbent_change: float = 0.0,
        challenger_change: float = 0.0
    ) -> "State":
        """Apply support changes and return new state."""
        new_incumbent = max(0.0, min(100.0, self.incumbent_support + incumbent_change))
        new_challenger = max(0.0, min(100.0, self.challenger_support + challenger_change))

        # Ensure total doesn't exceed 100
        total = new_incumbent + new_challenger
        if total > 100.0:
            ratio = 100.0 / total
            new_incumbent *= ratio
            new_challenger *= ratio

        return State(
            name=self.name,
            abbreviation=self.abbreviation,
            electoral_votes=self.electoral_votes,
            incumbent_support=round(new_incumbent, 1),
            challenger_support=round(new_challenger, 1),
            lean=self._calculate_lean(new_incumbent - new_challenger),
            region=self.region,
        )

    def _calculate_lean(self, margin: float) -> str:
        """Calculate lean based on margin."""
        if margin >= 15:
            return "Safe Inc"
        elif margin >= 5:
            return "Lean Inc"
        elif margin > -5:
            return "Tossup"
        elif margin > -15:
            return "Lean Chl"
        else:
            return "Safe Chl"

    def __str__(self) -> str:
        return f"{self.name} ({self.electoral_votes} EV): {self.incumbent_support:.1f}% - {self.challenger_support:.1f}%"
