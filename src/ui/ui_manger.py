import random
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import QTimer
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
        
    def update_round(self, round_num: int):
        self.game_screen.set_round(round_num)
        
    def reveal_turn_outcome(self, hider_r: int, hider_c: int, seeker_r: int, seeker_c: int):
        self.game_screen.reveal_choices(hider_r, hider_c, seeker_r, seeker_c)

    def show_simulation_results(self, hider_wins: int, seeker_wins: int, hider_score: int, seeker_score: int):
        """Displays the final results after a 100-round simulation."""
        msg = f"Hider Wins: {hider_wins} (Score: {hider_score})\nSeeker Wins: {seeker_wins} (Score: {seeker_score})"
        dialog = ConfirmDialog("Simulation Complete", msg, self)
        dialog.exec()

    # --- MOCK BACKEND FOR TESTING ---
    def mock_backend_receiver(self, payload: dict):
        action = payload.get("action")
        
        if action == "human_move":
            human_r = payload['row']
            human_c = payload['col']
            human_role = self.game_screen.human_role
            
            self.set_turn("seeker" if human_role == "hider" else "hider")
            self.game_screen.lbl_turn.setText("Computer is thinking...")
            self.game_screen.grid_container.setEnabled(False)
            
            # Pass the human's coordinates to the timer callback
            QTimer.singleShot(1500, lambda: self._mock_apply_result(human_role, human_r, human_c))
            
        elif action == "reset_game":
            self.update_scores(0, 0)
            self.update_round(1)
            self.set_turn("hider")
            self.game_screen.clear_markers()
            self.game_screen.grid_container.setEnabled(True)

    def _mock_apply_result(self, human_role, human_r, human_c):
        # Mock computer coordinates
        comp_r = random.randint(0, self.game_screen.board_rows - 1)
        comp_c = random.randint(0, self.game_screen.board_cols - 1)
        
        # Determine who is who for the API call
        if human_role == "hider":
            hider_r, hider_c = human_r, human_c
            seeker_r, seeker_c = comp_r, comp_c
        else:
            seeker_r, seeker_c = human_r, human_c
            hider_r, hider_c = comp_r, comp_c

        # Reveal the choices on the grid
        self.reveal_turn_outcome(hider_r, hider_c, seeker_r, seeker_c)
        
        # Update UI feedback
        self.update_scores(10, 5)
        self.update_round(2) # Mocking round 2
        
        if hider_r == seeker_r and hider_c == seeker_c:
            self.game_screen.show_round_outcome("SEEKER FOUND HIDER!", "#ff7b72")
        else:
            self.game_screen.show_round_outcome("HIDER ESCAPED!", "#58a6ff")
        
        QTimer.singleShot(2000, lambda: self._mock_next_round())

    def _mock_next_round(self):
        self.set_turn("hider")
        self.game_screen.clear_markers()
        self.game_screen.grid_container.setEnabled(True)