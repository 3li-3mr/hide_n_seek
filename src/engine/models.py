from dataclasses import dataclass, field
from typing import Literal
import numpy as np

from .constants import PlaceType


@dataclass
class WorldCell:
    index: int          # flat 0-based index  (unique identifier)
    row: int            # row in the grid  (always 0 for 1-D worlds)
    col: int            # column in the grid
    place_type: PlaceType


@dataclass
class SolverResult:

    N: int                      # total number of places
    grid_rows: int              # 1 for linear worlds, sqrt(N) for 2-D
    grid_cols: int              # N for linear worlds, sqrt(N) for 2-D
    cells: list[WorldCell]      # length N, ordered by flat index

    # Both perspective matrices are always stored.
    # hider_payoff_matrix[h, s] = hider's payoff when hider→h, seeker→s
    # seeker_payoff_matrix[h, s] = seeker's payoff (mirror of hider's)
    hider_payoff_matrix: np.ndarray
    seeker_payoff_matrix: np.ndarray

    computer_role: Literal["hider", "seeker"]
    computer_probabilities: np.ndarray  # shape (N,), sums to 1.0
    game_value: float                   # expected hider payoff at Nash equilibrium

    lp_objective: np.ndarray   # objective vector c passed to linprog
    lp_A_ub: np.ndarray        # inequality constraint matrix
    lp_b_ub: np.ndarray        # inequality RHS vector

    proximity_enabled: bool = False
    grid_2d_enabled: bool = False

    @property
    def payoff_matrix(self) -> np.ndarray:
        """Backward-compatible alias — always returns the hider-perspective matrix."""
        return self.hider_payoff_matrix

    def display_matrix(self, human_role: str) -> np.ndarray:
        """Returns the matrix from the human player's perspective for UI display."""
        if human_role == "hider":
            return self.hider_payoff_matrix
        return self.seeker_payoff_matrix