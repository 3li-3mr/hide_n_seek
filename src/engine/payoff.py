

import numpy as np

from .constants import (
    HIDER_WIN_SCORE,
    HIDER_LOSE_SCORE,
    PROXIMITY_MULTIPLIER,
    PROXIMITY_DEFAULT_MULTIPLIER,
)
from .models import WorldCell
from .world import cell_distance


def build_payoff_matrix(
    cells: list[WorldCell],
    proximity: bool = False,
    grid_2d: bool = False,
) -> np.ndarray:

    N = len(cells)
    matrix = np.zeros((N, N), dtype=float)

    for h, hider_cell in enumerate(cells):
        for s in range(N):

            if h == s:
                # Seeker found the hider
                matrix[h, s] = HIDER_LOSE_SCORE[hider_cell.place_type]

            else:
                # Hider is safe — start with the base win score
                score = float(HIDER_WIN_SCORE[hider_cell.place_type])

                if proximity:
                    dist = cell_distance(hider_cell, cells[s], grid_2d=grid_2d)
                    multiplier = PROXIMITY_MULTIPLIER.get(dist, PROXIMITY_DEFAULT_MULTIPLIER)
                    score *= multiplier

                matrix[h, s] = score

    return matrix