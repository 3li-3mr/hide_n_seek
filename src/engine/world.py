

import random
from typing import Optional

from .constants import PlaceType
from .models import WorldCell


# All possible place types, used for random assignment
_PLACE_TYPES: list[PlaceType] = ["hard", "neutral", "easy"]


def generate_world(
    N: int,
    grid_2d: bool = False,
    seed: Optional[int] = None,
) -> list[WorldCell]:

    rng = random.Random(seed)
    cells: list[WorldCell] = []

    if grid_2d:
        side = int(N ** 0.5)
        for row in range(side):
            for col in range(side):
                idx = row * side + col
                place_type: PlaceType = rng.choice(_PLACE_TYPES)
                cells.append(WorldCell(index=idx, row=row, col=col, place_type=place_type))
    else:
        for idx in range(N):
            place_type = rng.choice(_PLACE_TYPES)
            cells.append(WorldCell(index=idx, row=0, col=idx, place_type=place_type))

    return cells


def cell_distance(a: WorldCell, b: WorldCell, grid_2d: bool = False) -> int:

    if grid_2d:
        return abs(a.row - b.row) + abs(a.col - b.col)
    return abs(a.col - b.col)