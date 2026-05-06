import numpy as np
from PySide6.QtCore import QTimer
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
        self.hider_score = 0.0
        self.seeker_score = 0.0
        self.current_round = 1

    def start_game(self, config):
        is_2d = config["is_2d"]
        self.human_role = config["role"].lower()
        self.hider_score = 0.0
        self.seeker_score = 0.0
        self.current_round = 1

        if is_2d:
            N = config["rows"] * config["cols"]
        else:
            N = config["size_n"]

        # CPU plays the opposite role as human
        computer_role = "seeker" if self.human_role == "hider" else "hider"

        proximity = config.get("proximity", False)

        self.engine = GameEngine(
            N=N,
            rows=config["rows"] if is_2d else 1,
            cols=config["cols"] if is_2d else N,
            grid_2d=is_2d,
            proximity=proximity,
        )

        self.result = self.engine.solve(computer_role=computer_role)

        # Convert engine cells → format the UI understands
        config["cells"] = [
            {
                "row": cell.row,
                "col": cell.col,
                "place_type": PLACE_TYPE_MAP[cell.place_type],
            }
            for cell in self.result.cells
        ]

        # Show the matrix from the HUMAN's perspective in the UI.
        display_matrix = self.result.display_matrix(self.human_role)

        config["strategy"] = StrategyDetails(
            payoff_matrix=display_matrix.tolist(),
            probabilities=self.result.computer_probabilities.tolist(),
            game_value=self.result.game_value,
        )

        if config["mode"] == "simulation":
            self.ui.route_to_game(config)
            self._run_simulation()
        else:
            self.ui.route_to_game(config)

    # --- GAME LOOP HANDLERS ---
    def handle_action(self, payload):
        action = payload.get("action")
        if action == "human_move":
            self._handle_human_move(payload["row"], payload["col"])
        elif action == "reset_game":
            self._handle_reset()

    def _handle_human_move(self, human_row, human_col):
        # 1. Computer samples its optimal strategy
        comp_idx = int(np.random.choice(self.result.N, p=self.result.computer_probabilities))
        comp_cell = self.result.cells[comp_idx]

        # 2. Convert human's click to a flat index
        if self.result.grid_2d_enabled:
            human_idx = human_row * self.result.grid_cols + human_col
        else:
            human_idx = human_col

        # 3. Determine hider/seeker indices regardless of human role
        if self.human_role == "hider":
            hider_idx, seeker_idx = human_idx, comp_idx
            hider_r, hider_c = human_row, human_col
            seeker_r, seeker_c = comp_cell.row, comp_cell.col
        else:
            seeker_idx, hider_idx = human_idx, comp_idx
            seeker_r, seeker_c = human_row, human_col
            hider_r, hider_c = comp_cell.row, comp_cell.col

        # 4. Score is ALWAYS read from the hider-perspective matrix.
        #    hider_payoff_matrix[h, s] > 0 means hider escaped (hider gains).
        #    hider_payoff_matrix[h, s] < 0 means hider caught (seeker gains).
        #    Zero-sum: seeker_score is always the negative of hider_score.
        score = float(self.result.hider_payoff_matrix[hider_idx, seeker_idx])
        self.hider_score += score
        self.seeker_score -= score
        self.current_round += 1

        # 5. Tell UI to show "Computer thinking..." briefly
        self.ui.game_screen.lbl_turn.setText("Computer is thinking...")
        self.ui.game_screen.grid_container.setEnabled(False)

        # 6. Reveal after 1 second
        QTimer.singleShot(1000, lambda: self._reveal_result(
            hider_r, hider_c, seeker_r, seeker_c, hider_idx, seeker_idx
        ))

    def _reveal_result(self, hider_r, hider_c, seeker_r, seeker_c, hider_idx, seeker_idx):
        self.ui.reveal_turn_outcome(hider_r, hider_c, seeker_r, seeker_c)
        self.ui.update_scores(round(self.hider_score, 2), round(self.seeker_score, 2))
        self.ui.update_round(self.current_round)

        if hider_idx == seeker_idx:
            self.ui.game_screen.show_round_outcome("SEEKER FOUND HIDER!", "#ff7b72")
        else:
            self.ui.game_screen.show_round_outcome("HIDER ESCAPED!", "#58a6ff")

        QTimer.singleShot(2000, self._next_round)

    def _next_round(self):
        self.ui.set_turn(self.human_role)
        self.ui.game_screen.clear_markers()
        self.ui.game_screen.grid_container.setEnabled(True)

    def _handle_reset(self):
        self.hider_score = 0.0
        self.seeker_score = 0.0
        self.current_round = 1
        self.ui.update_scores(0, 0)
        self.ui.update_round(1)
        self.ui.set_turn(self.human_role)
        self.ui.game_screen.clear_markers()
        self.ui.game_screen.grid_container.setEnabled(True)

    def _run_simulation(self):
        # Solve for both roles — each gets its own optimal strategy
        hider_result = self.engine.solve(computer_role="hider")
        seeker_result = self.engine.solve(computer_role="seeker")

        # Always use the hider-perspective matrix for scoring
        payoff = self.result.hider_payoff_matrix

        hider_wins = 0
        seeker_wins = 0
        h_total = 0.0
        s_total = 0.0

        for _ in range(100):
            h_idx = int(np.random.choice(self.result.N, p=hider_result.computer_probabilities))
            s_idx = int(np.random.choice(self.result.N, p=seeker_result.computer_probabilities))
            score = float(payoff[h_idx, s_idx])
            h_total += score
            s_total -= score
            if h_idx == s_idx:
                seeker_wins += 1
            else:
                hider_wins += 1

        self.ui.show_simulation_results(
            hider_wins, seeker_wins, round(h_total, 2), round(s_total, 2),
            payoff.tolist()
        )