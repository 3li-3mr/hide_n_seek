from enum import Enum
from dataclasses import dataclass
from typing import List

class PlaceType(Enum):
    HARD = "HARD"       # Seeker gets higher points
    NEUTRAL = "NEUTRAL" # Equal points
    EASY = "EASY"       # Seeker gets lower points

@dataclass
class GridCell:
    index: int
    row: int
    col: int
    place_type: PlaceType
    hider_prob: float 
    seeker_prob: float 

@dataclass
class GameState:
    grid: List[GridCell]
    hider_score: float
    seeker_score: float
    current_round: int

@dataclass
class SimulationResult:
    hider_wins: int
    seeker_wins: int
    total_score_computer: float
    total_score_player: float