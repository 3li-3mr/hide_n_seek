

from .engine import GameEngine
from .models import SolverResult, WorldCell
from .constants import (
    PlaceType,
    HIDER_WIN_SCORE,
    HIDER_LOSE_SCORE,
    PROXIMITY_MULTIPLIER,
    PROXIMITY_DEFAULT_MULTIPLIER,
)

__all__ = [
    # Core classes
    "GameEngine",
    "SolverResult",
    "WorldCell",
    # Types & constants (useful for Role 3 labels / colour-coding)
    "PlaceType",
    "HIDER_WIN_SCORE",
    "HIDER_LOSE_SCORE",
    "PROXIMITY_MULTIPLIER",
    "PROXIMITY_DEFAULT_MULTIPLIER",
]