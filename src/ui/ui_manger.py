from PySide6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.screens.start_screen import StartScreen
from src.ui.screens.game_screen import GameScreen
from src.ui.components.confirm_dialog import ConfirmDialog
from src.game.game_controller import GameController
from typing import List

class UIManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hide 'n' Seek")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.controller = GameController(ui=self)

        self.start_screen = StartScreen(self.controller.start_game)
        self.game_screen = GameScreen(
            menu_callback=self.route_to_menu,
            action_callback=self.controller.handle_action,
        )

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.game_screen)

    # --- ROUTING METHODS ---
    def route_to_game(self, config_payload: dict):
        self.game_screen.setup_board(config_payload)
        self.stack.setCurrentIndex(1)

    def route_to_menu(self):
        self.stack.setCurrentIndex(0)

    # --- UI API METHODS (Backend will call these) ---
    def update_scores(self, hider_score: int, seeker_score: int):
        self.game_screen.lbl_score_hider.setText(str(hider_score))
        self.game_screen.lbl_score_seeker.setText(str(seeker_score))

    def set_turn(self, role: str):
        self.game_screen.update_turn(role)
        
    def update_payoff_details(self, details_object):
        self.game_screen.update_details(details_object)
        
    def update_round(self, round_num: int):
        self.game_screen.set_round(round_num)
        
    def reveal_turn_outcome(self, hider_r: int, hider_c: int, seeker_r: int, seeker_c: int):
        self.game_screen.reveal_choices(hider_r, hider_c, seeker_r, seeker_c)

    def show_simulation_results(self, hider_wins: int, seeker_wins: int, hider_score: int, seeker_score: int, payoff: List[List[float]]):
        self.game_screen.show_simulation_results(
            hider_wins, seeker_wins, hider_score, seeker_score, payoff
        )