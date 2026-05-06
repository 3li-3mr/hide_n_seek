from typing import Literal

PlaceType = Literal["hard", "neutral", "easy"]

# Hider's Perspective (Original)
HIDER_WIN_SCORE: dict[str, int] = {"hard": 1, "neutral": 1, "easy": 2}
HIDER_LOSE_SCORE: dict[str, int] = {"hard": -3, "neutral": -1, "easy": -1}

# Seeker's Perspective (New)
# Note: In a zero-sum game, Seeker Win = Hider Loss
SEEKER_WIN_SCORE: dict[str, int] = {"hard": 3, "neutral": 1, "easy": 1}
SEEKER_LOSE_SCORE: dict[str, int] = {"hard": -1, "neutral": -1, "easy": -2}

PROXIMITY_MULTIPLIER: dict[int, float] = {1: 0.5, 2: 0.75}
PROXIMITY_DEFAULT_MULTIPLIER: float = 1.0