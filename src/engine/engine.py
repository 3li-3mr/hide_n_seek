import math
from typing import Literal, Optional
from .models import SolverResult, WorldCell
from .world import generate_world
from .payoff import build_payoff_matrix
from .lp_solver import solve_game


class GameEngine:
    def __init__(
        self,
        N: int,
        rows: int = 1,
        cols: Optional[int] = None,
        proximity: bool = False,
        grid_2d: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        if N < 2:
            raise ValueError("N must be at least 2.")
        if grid_2d:
            _cols = cols or int(math.isqrt(N))
            _rows = rows if cols else _cols
            if _rows * _cols != N:
                raise ValueError(
                    f"rows ({_rows}) × cols ({_cols}) = {_rows * _cols} ≠ N ({N})."
                )
        self.N = N
        if grid_2d:
            self.cols = cols or int(math.isqrt(N))
            self.rows = rows if cols else self.cols
        else:
            self.rows = 1
            self.cols = N
        self.proximity = proximity
        self.grid_2d = grid_2d
        self._cells = generate_world(
            N=N, rows=self.rows, cols=self.cols, grid_2d=grid_2d, seed=seed
        )

    @property
    def cells(self):
        return self._cells

    def regenerate_world(self, seed: Optional[int] = None) -> None:
        self._cells = generate_world(
            N=self.N, rows=self.rows, cols=self.cols,
            grid_2d=self.grid_2d, seed=seed
        )

    def solve(self, computer_role: Literal["hider", "seeker"]) -> SolverResult:
        # Always build BOTH perspective matrices.
        hider_payoff = build_payoff_matrix(
            cells=self._cells,
            proximity=self.proximity,
            grid_2d=self.grid_2d,
            perspective="hider",
        )
        seeker_payoff = build_payoff_matrix(
            cells=self._cells,
            proximity=self.proximity,
            grid_2d=self.grid_2d,
            perspective="seeker",
        )

        # The LP is always solved on the hider-perspective matrix.
        # computer_role tells the solver whether to maximin or minimax.
        probs, value, c, A_ub, b_ub = solve_game(
            payoff=hider_payoff,
            computer_role=computer_role,
            matrix_perspective="hider",
        )

        grid_rows = self.rows if self.grid_2d else 1
        grid_cols = self.cols if self.grid_2d else self.N

        return SolverResult(
            N=self.N,
            grid_rows=grid_rows,
            grid_cols=grid_cols,
            cells=list(self._cells),
            hider_payoff_matrix=hider_payoff,
            seeker_payoff_matrix=seeker_payoff,
            computer_role=computer_role,
            computer_probabilities=probs,
            game_value=value,
            lp_objective=c,
            lp_A_ub=A_ub,
            lp_b_ub=b_ub,
            proximity_enabled=self.proximity,
            grid_2d_enabled=self.grid_2d,
        )