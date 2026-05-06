
import math
from typing import Literal, Optional

from .constants import PlaceType
from .models import SolverResult, WorldCell
from .world import generate_world
from .payoff import build_payoff_matrix
from .lp_solver import solve_game


class GameEngine:


    def __init__(
        self,
        N: int,
        rows: int = 1,
        cols: int = None,
        proximity: bool = False,
        grid_2d: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        if N < 2:
            raise ValueError(f"N must be >= 2, got {N}.")

        if grid_2d:
            # Auto-compute rows/cols from sqrt(N) when not explicitly provided
            if rows == 1 and cols is None:
                sqrt_n = int(math.isqrt(N))
                if sqrt_n * sqrt_n != N:
                    raise ValueError(
                        f"For a 2-D world N must be a perfect square when rows/cols "
                        f"are not specified, got N={N}."
                    )
                rows = sqrt_n
                cols = sqrt_n
            else:
                cols = cols or N
                if rows * cols != N:
                    raise ValueError(
                        f"For a 2-D world rows × cols must equal N, got {rows}×{cols}≠{N}."
                    )
        else:
            cols = cols or N

        self.N = N
        self.rows = rows
        self.cols = cols
        self.proximity = proximity
        self.grid_2d = grid_2d
        self.seed = seed

        self._cells: list[WorldCell] = generate_world(
            N=N, rows=rows, cols=cols, grid_2d=grid_2d, seed=seed
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def cells(self) -> list[WorldCell]:
        return list(self._cells)

    def regenerate_world(self, seed: Optional[int] = None) -> None:

        self.seed = seed
        self._cells = generate_world(
            N=self.N, rows=self.rows, cols=self.cols, grid_2d=self.grid_2d, seed=seed
        )

    def solve(
        self,
        computer_role: Literal["hider", "seeker"],
    ) -> SolverResult:

        # 1. Build payoff matrix (always from the hider's perspective)
        payoff = build_payoff_matrix(
            cells=self._cells,
            proximity=self.proximity,
            grid_2d=self.grid_2d,
        )

        # 2. Solve the LP for the computer's role
        probs, value, c, A_ub, b_ub = solve_game(
            payoff=payoff,
            computer_role=computer_role,
        )

        # 3. Determine grid dimensions for the result
        if self.grid_2d:
            grid_rows = self.rows
            grid_cols = self.cols
        else:
            grid_rows = 1
            grid_cols = self.N

        return SolverResult(
            N=self.N,
            grid_rows=grid_rows,
            grid_cols=grid_cols,
            cells=list(self._cells),
            payoff_matrix=payoff,
            computer_role=computer_role,
            computer_probabilities=probs,
            game_value=value,
            lp_objective=c,
            lp_A_ub=A_ub,
            lp_b_ub=b_ub,
            proximity_enabled=self.proximity,
            grid_2d_enabled=self.grid_2d,
        )