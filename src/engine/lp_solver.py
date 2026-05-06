from typing import Literal
import numpy as np

from scipy.optimize import linprog

def solve_game(
    payoff: np.ndarray,
    computer_role: Literal["hider", "seeker"],
    matrix_perspective: Literal["hider", "seeker"]
) -> tuple[np.ndarray, float, np.ndarray, np.ndarray, np.ndarray]:

    N = payoff.shape[0]

    # Shift matrix so every entry is strictly positive for the LP formulation
    K = float(-payoff.min() + 1.0)
    A = payoff + K

    # If the computer's role matches the matrix perspective, it wants to MAXIMIZE.
    # Otherwise, it wants to MINIMIZE the opponent's payoff.
    if computer_role == matrix_perspective:
        c, A_ub, b_ub, A_eq, b_eq, bounds = _build_maximizer_lp(A, N)
    else:
        c, A_ub, b_ub, A_eq, b_eq, bounds = _build_minimizer_lp(A, N)

    result = linprog(c, A_ub=A_ub, b_ub=b_ub,
                     A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method="highs")

    if not result.success:
        raise RuntimeError(f"LP solver failed: {result.message}")

    probabilities = _normalise(result.x[:N])
    # The value of the game needs the shift K removed
    game_value = float(result.x[N] - K)

    return probabilities, game_value, c, A_ub, b_ub

def _build_maximizer_lp(A: np.ndarray, N: int):
    # Standard Maximin: Objective is to maximize the minimum gain (v)
    # We use minimize -v for scipy
    c = np.zeros(N + 1)
    c[-1] = -1.0

    A_ub = np.zeros((N, N + 1))
    for col in range(N):
        A_ub[col, :N] = -A[:, col] # -Payoff for row strategies
        A_ub[col, N] = 1.0         # +v
    b_ub = np.zeros(N)

    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0.0, None)] * N + [(None, None)]
    return c, A_ub, b_ub, A_eq, b_eq, bounds

def _build_minimizer_lp(A: np.ndarray, N: int):
    # Standard Minimax: Objective is to minimize the maximum loss (v)
    c = np.zeros(N + 1)
    c[-1] = 1.0

    A_ub = np.zeros((N, N + 1))
    for row in range(N):
        A_ub[row, :N] = A[row, :] # Payoff for column strategies
        A_ub[row, N] = -1.0       # -v
    b_ub = np.zeros(N)

    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0.0, None)] * N + [(None, None)]
    return c, A_ub, b_ub, A_eq, b_eq, bounds

def _normalise(probs: np.ndarray) -> np.ndarray:
    probs = np.clip(probs, 0.0, None)
    total = probs.sum()
    if total < 1e-10:
        return np.ones(len(probs)) / len(probs)
    return probs / total