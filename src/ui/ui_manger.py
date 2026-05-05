from PySide6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.screens.start_screen import StartScreen
from src.ui.screens.game_screen import GameScreen
# Import ConfirmDialog to act as a temporary simulation results popup
from src.ui.components.confirm_dialog import ConfirmDialog 

class UIManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hide 'n' Seek")
        self.setFixedSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_screen = StartScreen(self.route_to_game)
        
        # FIXED: Pass the mock_backend_receiver as the action_callback
        self.game_screen = GameScreen(
            menu_callback=self.route_to_menu,
            action_callback=self.mock_backend_receiver 
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

    def show_simulation_results(self, hider_wins: int, seeker_wins: int, hider_score: int, seeker_score: int):
        """Displays the final results after a 100-round simulation."""
        msg = f"Hider Wins: {hider_wins} (Score: {hider_score})\nSeeker Wins: {seeker_wins} (Score: {seeker_score})"
        dialog = ConfirmDialog("Simulation Complete", msg, self)
        dialog.exec()

    # --- MOCK BACKEND FOR TESTING ---
    def mock_backend_receiver(self, payload: dict):
        """
        TEMPORARY: This replaces Role 2's Game Controller.
        It intercepts the UI's messages and responds instantly so you can test visual changes.
        """
        action = payload.get("action")
        
        if action == "human_move":
            print(f"[MOCK BACKEND] Human clicked Row {payload['row']}, Col {payload['col']}")
            # Mock a score update
            self.update_scores(10, 5)
            # Mock a turn change
            self.set_turn("seeker")
            
        elif action == "reset_game":
            print("[MOCK BACKEND] Resetting game...")
            self.update_scores(0, 0)
            self.set_turn("hider")