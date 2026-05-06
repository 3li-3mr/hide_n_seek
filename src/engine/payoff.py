import numpy as np
from .constants import (
    HIDER_WIN_SCORE, HIDER_LOSE_SCORE,
    SEEKER_WIN_SCORE, SEEKER_LOSE_SCORE,
    PROXIMITY_MULTIPLIER, PROXIMITY_DEFAULT_MULTIPLIER,
)
from .world import cell_distance

def build_payoff_matrix(cells, proximity=False, grid_2d=False, perspective="hider"):
    N = len(cells)
    matrix = np.zeros((N, N), dtype=float)

    for h, hider_cell in enumerate(cells):
        for s in range(N):
            if h == s:
                # Caught!
                if perspective == "hider":
                    matrix[h, s] = HIDER_LOSE_SCORE[hider_cell.place_type]
                else:
                    matrix[h, s] = SEEKER_WIN_SCORE[hider_cell.place_type]
            else:
                # Hider is safe
                if perspective == "hider":
                    score = float(HIDER_WIN_SCORE[hider_cell.place_type])
                else:
                    score = float(SEEKER_LOSE_SCORE[hider_cell.place_type])

                if proximity:
                    dist = cell_distance(hider_cell, cells[s], grid_2d=grid_2d)
                    multiplier = PROXIMITY_MULTIPLIER.get(dist, PROXIMITY_DEFAULT_MULTIPLIER)
                    # For seeker perspective, failing to catch hider is worse if close?
                    # Usually, multipliers apply to the Hider's reward.
                    score *= multiplier

                matrix[h, s] = score
    return matrix