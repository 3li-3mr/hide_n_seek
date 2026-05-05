

from typing import Literal
import numpy as np
from scipy.optimize import linprog


def solve_game(
    payoff: np.ndarray,
    computer_role: Literal["hider", "seeker"],
) -> tuple[np.ndarray, float, np.ndarray, np.ndarray, np.ndarray]:

    N = payoff.shape[0]

    # Shift matrix so every entry is strictly positive
    K = float(-payoff.min() + 1.0)
    A = payoff + K

    if computer_role == "hider":
        c, A_ub, b_ub, A_eq, b_eq, bounds = _build_hider_lp(A, N)
    else:
        c, A_ub, b_ub, A_eq, b_eq, bounds = _build_seeker_lp(A, N)

    result = linprog(c, A_ub=A_ub, b_ub=b_ub,
                     A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method="highs")

    if not result.success:
        raise RuntimeError(
            f"LP solver failed: {result.message}\n"
            "Check that N ≥ 2 and the payoff matrix is valid."
        )

    probabilities = _normalise(result.x[:N])
    game_value = float(result.x[N] - K)   # undo the shift

    return probabilities, game_value, c, A_ub, b_ub


# ── LP builders ───────────────────────────────────────────────────────────────

def _build_hider_lp(A: np.ndarray, N: int):

    # Objective: minimise -v
    c = np.zeros(N + 1)
    c[-1] = -1.0

    # Inequality constraints (one per seeker column)
    A_ub = np.zeros((N, N + 1))
    for s in range(N):
        A_ub[s, :N] = -A[:, s]   # -column s
        A_ub[s,  N] = 1.0        # +v
    b_ub = np.zeros(N)

    # Equality: probabilities sum to 1
    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0.0, None)] * N + [(None, None)]   # p_h ≥ 0, v free

    return c, A_ub, b_ub, A_eq, b_eq, bounds


def _build_seeker_lp(A: np.ndarray, N: int):

    # Objective: minimise v
    c = np.zeros(N + 1)
    c[-1] = 1.0

    # Inequality constraints (one per hider row)
    A_ub = np.zeros((N, N + 1))
    for h in range(N):
        A_ub[h, :N] = A[h, :]   # row h
        A_ub[h,  N] = -1.0      # -v
    b_ub = np.zeros(N)

    # Equality: probabilities sum to 1
    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0.0, None)] * N + [(None, None)]

    return c, A_ub, b_ub, A_eq, b_eq, bounds


# ── Helper ────────────────────────────────────────────────────────────────────

def _normalise(probs: np.ndarray) -> np.ndarray:
    probs = np.clip(probs, 0.0, None)
    total = probs.sum()
    if total < 1e-10:
        # Degenerate fallback: uniform distribution
        return np.ones(len(probs)) / len(probs)
    return probs / total