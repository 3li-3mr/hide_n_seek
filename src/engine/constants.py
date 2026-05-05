"""
constants.py
------------
All scoring rules, proximity multipliers, and shared type aliases.
Edit this file to tune the game balance without touching any logic.
"""

from typing import Literal


PlaceType = Literal["hard", "neutral", "easy"]


HIDER_WIN_SCORE: dict[str, int] = {
    "hard":    1,
    "neutral": 2,
    "easy":    3,
}

HIDER_LOSE_SCORE: dict[str, int] = {
    "hard":    -3,
    "neutral": -1,
    "easy":    -1,
}

PROXIMITY_MULTIPLIER: dict[int, float] = {
    1: 0.5,
    2: 0.75,
}
PROXIMITY_DEFAULT_MULTIPLIER: float = 1.0