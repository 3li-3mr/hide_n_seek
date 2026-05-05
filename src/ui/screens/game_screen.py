import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QGridLayout ,QFrame, QScrollArea)
from PySide6.QtCore import Qt
from src.ui.components.confirm_dialog import ConfirmDialog
from src.core.contracts import PlaceType, StrategyDetails

class GameScreen(QWidget):
    def __init__(self, menu_callback, action_callback):
        super().__init__()
        self.menu_callback = menu_callback
        self.action_callback = action_callback
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20) 
        self.setLayout(self.main_layout)

        self._build_top_bar()

        self.main_layout.addStretch(1)

        self._build_turn_indicator()

        # --- THE NEW 50/50 SPLIT SCREEN ---
        self.middle_area = QHBoxLayout()

        # 1. Left Half (The Game Board)
        self.left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centers grid in the left half
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5) 
        self.grid_container.setLayout(self.grid_layout)
        
        left_layout.addWidget(self.grid_container)
        self.left_container.setLayout(left_layout)

        # 2. Right Half (The Details Panel)
        self.right_container = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self._build_details_panel() 
        right_layout.addWidget(self.details_panel)
        self.right_container.setLayout(right_layout)

        # 3. Add to middle area with equal stretch weights (1 and 1)
        self.middle_area.addWidget(self.left_container, 1)
        self.middle_area.addWidget(self.right_container, 1)

        self.main_layout.addLayout(self.middle_area)
        self.main_layout.addStretch(2)
        self.right_container.setVisible(False)

    def _build_top_bar(self):
        top_bar = QHBoxLayout()
        
        self.btn_reset = QPushButton("↺")
        self.btn_reset.setObjectName("BtnBlue")
        self.btn_reset.clicked.connect(self._handle_reset)
        
        self.btn_details = QPushButton("Show Details")
        self.btn_details.setObjectName("BtnStart")
        self.btn_details.clicked.connect(self._toggle_details)
        
        self.lbl_hider_name = QLabel("Hider")
        self.lbl_score_hider = QLabel("0")
        self.lbl_score_hider.setObjectName("ScoreHider")
        
        self.lbl_score_seeker = QLabel("0")
        self.lbl_score_seeker.setObjectName("ScoreSeeker")
        self.lbl_seeker_name = QLabel("Seeker")
        
        self.btn_menu = QPushButton("Main Menu")
        self.btn_menu.setObjectName("BtnRed")
        self.btn_menu.clicked.connect(self._handle_main_menu)
        
        top_bar.addWidget(self.btn_reset)
        top_bar.addWidget(self.btn_menu)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_hider_name)
        top_bar.addWidget(self.lbl_score_hider)
        top_bar.addWidget(self.lbl_score_seeker)
        top_bar.addWidget(self.lbl_seeker_name)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_details)
        
        self.main_layout.addLayout(top_bar)

    def _build_turn_indicator(self):
        self.lbl_turn = QLabel("Waiting for game to start...")
        self.lbl_turn.setObjectName("TurnText")
        self.lbl_turn.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_player_role = QLabel("")
        self.lbl_player_role.setObjectName("PlayerRoleText")
        self.lbl_player_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(self.lbl_turn)
        self.main_layout.addWidget(self.lbl_player_role)

    def _handle_grid_click(self, row: int, col: int):
        self.action_callback({
            "action": "human_move",
            "row": row,
            "col": col
        })

    def setup_board(self, config: dict):
        self._clear_grid()

        human_role = config["role"]
        self.lbl_player_role.setText(f"( You are playing as the {human_role} )")
        
        if config["mode"] == "simulation":
            self.lbl_turn.setText("SIMULATING 100 ROUNDS...")
            self.lbl_player_role.setText("( CPU vs CPU )")
            
            # TEMPORARY MOCK: Trigger the simulation results popup immediately for testing
            # In the final version, the backend will run a loop and then call this.
            self.window().show_simulation_results(45, 55, 120, 150)
            return

        self.board_rows = config["rows"] if config["is_2d"] else 1
        self.board_cols = config["cols"] if config["is_2d"] else config["size_n"]
        total_cells = self.board_rows * self.board_cols
        
        type_to_css = {
            PlaceType.HARD: "CellHard",
            PlaceType.NEUTRAL: "CellNeutral",
            PlaceType.EASY: "CellEasy"
        }

        # --- MOCK STRATEGY DETAILS GENERATION (Inside setup_board) ---
        raw_probs = [random.random() for _ in range(total_cells)]
        total_prob = sum(raw_probs)
        normalized_probs = [p / total_prob for p in raw_probs]
        
        # NEW: Generate a fake 2D payoff matrix matching the grid dimensions
        mock_matrix = [[random.randint(-10, 10) for _ in range(self.board_cols)] for _ in range(self.board_rows)]
        
        mock_details = StrategyDetails(
            payoff_matrix=mock_matrix,
            probabilities=normalized_probs,
            game_value=random.uniform(-5.0, 5.0)
        )
        self.update_details(mock_details)
        # ----------------------------------------

        for r in range(self.board_rows):
            for c in range(self.board_cols):
                btn = QPushButton()
                btn.setFixedSize(60, 60)
                
                # Mock a random difficulty for testing the CSS
                mock_place_type = random.choice(list(PlaceType)) 
                css_class = type_to_css[mock_place_type]
                btn.setProperty("class", css_class) 
                
                btn.clicked.connect(lambda checked=False, r=r, c=c: self._handle_grid_click(r, c))
                self.grid_layout.addWidget(btn, r, c)

        self.update_turn("hider")

    # may notify game class
    def update_turn(self, current_turn: str):
        self.lbl_turn.setText(f"{current_turn.capitalize()}'s Turn")

        self.lbl_turn.setProperty("active_turn", current_turn)
        self.lbl_turn.style().unpolish(self.lbl_turn)
        self.lbl_turn.style().polish(self.lbl_turn)

        main_window = self.window()
        main_window.setProperty("active_turn", current_turn)
        main_window.style().unpolish(main_window)
        main_window.style().polish(main_window)

    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # notify game class
    def _handle_main_menu(self):
        dialog = ConfirmDialog("Main Menu", "End current game and return to menu?")
        if dialog.exec():
            self.window().setProperty("active_turn", "neutral")
            self.window().style().unpolish(self.window())
            self.window().style().polish(self.window())
            self.menu_callback()

    # notify game class
    def _handle_reset(self):
        dialog = ConfirmDialog("Reset Game", "Are you sure you want to reset the scores to 0?")
        if dialog.exec():
            self.lbl_score_hider.setText("0")
            self.lbl_score_seeker.setText("0")
            # NOTIFY BACKEND: Tell it to reset internal memory
            self.action_callback({"action": "reset_game"})

    def _build_details_panel(self):        
        self.details_panel = QFrame()
        self.details_panel.setObjectName("FloatingCard")
        # REMOVED setFixedWidth(300) so it expands nicely into its half
        
        panel_layout = QVBoxLayout()
        self.details_panel.setLayout(panel_layout)
        
        title = QLabel("Optimal Strategy")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #58a6ff; margin-bottom: 10px;")
        
        self.details_matrix_layout = QGridLayout()
        
        panel_layout.addWidget(title)
        panel_layout.addLayout(self.details_matrix_layout)
        panel_layout.addStretch()

    def update_details(self, details: 'StrategyDetails'):
        while self.details_matrix_layout.count():
            item = self.details_matrix_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

        current_row = 0

        # --- SECTION 1: THE SCALED PAYOFF MATRIX ---
        if details.payoff_matrix:
            lbl_matrix_title = QLabel("Initial Payoff Matrix")
            lbl_matrix_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #cdd6f4; margin-bottom: 10px;")
            self.details_matrix_layout.addWidget(lbl_matrix_title, current_row, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            current_row += 1
            
            matrix_grid = QGridLayout()
            matrix_grid.setSpacing(5) # Match the game board spacing
            for r, row_data in enumerate(details.payoff_matrix):
                for c, val in enumerate(row_data):
                    lbl_val = QLabel(str(val))
                    lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    # Force the labels to be large squares (50x50 or 60x60 to match board)
                    lbl_val.setFixedSize(55, 55) 
                    lbl_val.setStyleSheet("background-color: #21262d; border: 2px solid #30363d; border-radius: 4px; font-size: 16px; font-weight: bold;")
                    matrix_grid.addWidget(lbl_val, r, c)
            
            # Wrap the grid in a container to center it perfectly
            matrix_container = QWidget()
            matrix_container.setLayout(matrix_grid)
            self.details_matrix_layout.addWidget(matrix_container, current_row, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            current_row += 1

        # --- SECTION 2: THE SCROLLABLE PROBABILITIES ---
        lbl_prob_title = QLabel("Optimal Probabilities")
        lbl_prob_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #cdd6f4; margin-top: 20px; margin-bottom: 5px;")
        self.details_matrix_layout.addWidget(lbl_prob_title, current_row, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        current_row += 1

        # Create the Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Remove ugly borders and make the background transparent to match the card
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Create a container widget to sit inside the scroll area
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        # The grid layout goes ON the scroll_content, not the main panel
        prob_grid = QGridLayout(scroll_content)
        prob_grid.addWidget(QLabel("<b>Grid Coord</b>"), 0, 0)
        prob_grid.addWidget(QLabel("<b>Probability</b>"), 0, 1)

        for i, prob in enumerate(details.probabilities):
            # --- THE 1D TO 2D MATH ---
            # Using 1-based indexing (e.g., Row 1, Col 1)
            row_idx = (i // self.board_cols) + 1
            col_idx = (i % self.board_cols) + 1
            
            lbl_move = QLabel(f"({row_idx}, {col_idx})")
            lbl_prob = QLabel(f"{prob:.3f}")
            lbl_move.setStyleSheet("font-size: 14px; color: #8b949e;")
            lbl_prob.setStyleSheet("font-size: 14px; color: #8b949e;")
            
            prob_grid.addWidget(lbl_move, i+1, 0)
            prob_grid.addWidget(lbl_prob, i+1, 1)
            
        # Put the populated container into the scroll area
        scroll_area.setWidget(scroll_content)
        
        # Add the entire scroll area to the main details layout
        self.details_matrix_layout.addWidget(scroll_area, current_row, 0, 1, 2)
        current_row += 1

        # --- SECTION 3: GAME VALUE ---
        val_lbl = QLabel(f"Expected Game Value: {details.game_value:.2f}")
        val_lbl.setStyleSheet("color: #ff7b72; margin-top: 20px; font-weight: bold; font-size: 16px;")
        self.details_matrix_layout.addWidget(val_lbl, current_row, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

    def _clear_layout(self, layout):
        """Helper method to safely destroy nested layouts."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())
        layout.deleteLater()

    def _toggle_details(self):
        is_visible = self.right_container.isVisible()
        self.right_container.setVisible(not is_visible)
        if is_visible:
            self.btn_details.setText("Show Details")
        else:
            self.btn_details.setText("Hide Details")