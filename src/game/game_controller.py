from src.engine import GameEngine
from src.core.contracts import PlaceType as UIPlaceType, StrategyDetails

# Mapping from engine format to UI format
PLACE_TYPE_MAP = {
    "hard": UIPlaceType.HARD,
    "neutral": UIPlaceType.NEUTRAL,
    "easy": UIPlaceType.EASY,
}

class GameController:

    def __init__(self, ui):
        self.ui = ui
        self.engine = None 
        self.result = None 
        self.human_role = None

    def start_game(self, config):
        #Called when the user clicks "Start Game" or "Start Sim" on the start screen.

        is_2d = config["is_2d"]
        self.human_role = config["role"].lower()

        if is_2d:
            N = config["rows"] * config["cols"]
        else:
            N = config["size_n"]

        # CPU plays the opposite role as human 
        computer_role = "seeker" if self.human_role == "hider" else "hider"

        # Create the engine and solve the LP
        # GameEngine generates a random world (random place types)
        self.engine = GameEngine(N=N, grid_2d=is_2d)

        #solve() returns a SolverResult containing:
        # -cells: the generated world (each cell has a place type)
        # -payoff_matrix: N×N matrix of hider payoffs
        # -computer_probabilities: optimal mixed strategy for the computer
        # -game_value: expected payoff at Nash equilibrium
        self.result = self.engine.solve(computer_role=computer_role)

        #Convert the config with REAL data for the UI
        #Convert engine cells → format the UI understands
        config["cells"] = [
            {
                "row": cell.row,
                "col": cell.col,
                "place_type": PLACE_TYPE_MAP[cell.place_type],
            }
            for cell in self.result.cells
        ]

        #Convert the solver result → StrategyDetails (the dataclass the UI expects)
        config["strategy"] = StrategyDetails(
            payoff_matrix=self.result.payoff_matrix.tolist(),
            probabilities=self.result.computer_probabilities.tolist(),
            game_value=self.result.game_value,
        )
        self.ui.route_to_game(config)
