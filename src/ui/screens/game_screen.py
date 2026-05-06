
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QGridLayout ,QFrame, QScrollArea)
from PySide6.QtCore import Qt
from src.ui.components.confirm_dialog import ConfirmDialog
from src.core.contracts import PlaceType, StrategyDetails
from typing import List

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
        left_layout.addSpacing(30)
        left_layout.addLayout(self._build_legend())
        self.left_container.setLayout(left_layout)

        # 2. Right Half (The Details Panel)
        self.right_container = QWidget()
        right_layout = QVBoxLayout()
        # REMOVED AlignHCenter so the panel can stretch to fill the right half
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 
        
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

        # --- NEW: Round Counter ---
        self.lbl_round = QLabel("Round: 1")
        self.lbl_round.setStyleSheet("font-size: 16px; font-weight: bold; color: #8b949e; margin-right: 15px;")
        
        top_bar.addWidget(self.btn_reset)
        top_bar.addWidget(self.btn_menu)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_hider_name)
        top_bar.addWidget(self.lbl_score_hider)
        top_bar.addWidget(self.lbl_score_seeker)
        top_bar.addWidget(self.lbl_seeker_name)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_round)
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
        self.cell_buttons = {}

        self.human_role = config["role"].lower()
        self.lbl_player_role.setText(f"( You are playing as the {self.human_role} )")
        
        if config["mode"] == "simulation":
            self.lbl_turn.setText("Simulation Complete")
            self.lbl_player_role.setText("( CPU vs CPU )")
            return

        self.board_rows = config["rows"] if config["is_2d"] else 1
        self.board_cols = config["cols"] if config["is_2d"] else config["size_n"]
        total_cells = self.board_rows * self.board_cols
        
        type_to_css = {
            PlaceType.HARD: "CellHard",
            PlaceType.NEUTRAL: "CellNeutral",
            PlaceType.EASY: "CellEasy"
        }

        if "strategy" in config:
            self.update_details(config["strategy"])

        cells = config.get("cells", [])
        for r in range(self.board_rows):
            for c in range(self.board_cols):
                btn = QPushButton()
                btn.setFixedSize(60, 60)
                btn.setStyleSheet("font-size: 24px; font-weight: bold;")

                cell_idx = r * self.board_cols + c
                if cell_idx < len(cells):
                    place_type = cells[cell_idx]["place_type"]
                else:
                    place_type = PlaceType.NEUTRAL
                css_class = type_to_css[place_type]
                btn.setProperty("class", css_class)

                btn.clicked.connect(lambda checked=False, r=r, c=c: self._handle_grid_click(r, c))
                self.grid_layout.addWidget(btn, r, c)
                self.cell_buttons[(r, c)] = btn
        self.update_turn(self.human_role)

    def show_round_outcome(self, message: str, color_hex: str):
        """Temporarily overrides the turn text to show who won the round."""
        self.lbl_turn.setText(message)
        self.lbl_turn.setStyleSheet(f"font-weight: bold; font-size: 20px; color: {color_hex};")

    # may notify game class
    def update_turn(self, current_turn: str):
        self.lbl_turn.setText(f"{current_turn.capitalize()}'s Turn")
        self.lbl_turn.setStyleSheet("")
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
            self.lbl_score_hider.setText("0")
            self.lbl_score_seeker.setText("0")
            # NOTIFY BACKEND: Tell it to reset internal memory
            self.action_callback({"action": "reset_game"})
            self.window().setProperty("active_turn", "neutral")
            self.window().style().unpolish(self.window())
            self.window().style().polish(self.window())
            self.right_container.setVisible(False)
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
        # Scrapped the "FloatingCard" frame. It's now a clean, expansive widget.
        self.details_panel = QWidget()
        
        panel_layout = QVBoxLayout()
        # Add side margins so it doesn't touch the center split or right edge
        panel_layout.setContentsMargins(40, 0, 40, 0) 
        self.details_panel.setLayout(panel_layout)
        
        title = QLabel("Optimal Strategy Breakdown")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #58a6ff; margin-bottom: 25px;")
        
        # Changed to a VBox for cleaner vertical stacking
        self.details_content_layout = QVBoxLayout()
        self.details_content_layout.setSpacing(25) # More breathing room between sections
        
        panel_layout.addWidget(title)
        panel_layout.addLayout(self.details_content_layout)
        panel_layout.addStretch()

    def update_details(self, details: 'StrategyDetails'):
        while self.details_content_layout.count():
            item = self.details_content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

        # --- SECTION 1: THE SCROLLABLE PAYOFF MATRIX ---
        if details.payoff_matrix:
            lbl_matrix_title = QLabel("Initial Payoff Matrix")
            lbl_matrix_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
            lbl_matrix_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.details_content_layout.addWidget(lbl_matrix_title)
            
            matrix_scroll = QScrollArea()
            # WidgetResizable must be True so it fills the area, but the fixed size labels 
            # will force the scrollbars to appear when it gets too large
            matrix_scroll.setWidgetResizable(True)
            matrix_scroll.setStyleSheet("QScrollArea { border: 1px solid #30363d; border-radius: 8px; background-color: #161b22; }")
            
            matrix_content = QWidget()
            matrix_content.setStyleSheet("background-color: transparent;")
            
            matrix_grid = QGridLayout(matrix_content)
            matrix_grid.setSpacing(8)
            # This safely centers small grids (like 2x2) but allows big grids to scroll properly
            matrix_grid.setAlignment(Qt.AlignmentFlag.AlignCenter) 
            
            for r, row_data in enumerate(details.payoff_matrix):
                for c, val in enumerate(row_data):
                    lbl_val = QLabel(str(val))
                    lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl_val.setFixedSize(60, 60) # Forces Qt to expand the grid and trigger scrolling
                    lbl_val.setStyleSheet("background-color: #21262d; border: 2px solid #30363d; border-radius: 6px; font-size: 18px; font-weight: bold;")
                    matrix_grid.addWidget(lbl_val, r, c)
            
            matrix_scroll.setWidget(matrix_content)
            self.details_content_layout.addWidget(matrix_scroll, 3)

        # --- SECTION 2: PROBABILITIES ---
        lbl_prob_title = QLabel("Optimal Probabilities")
        lbl_prob_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        lbl_prob_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_content_layout.addWidget(lbl_prob_title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #30363d; border-radius: 8px; background-color: #161b22; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        prob_grid = QGridLayout(scroll_content)
        prob_grid.setSpacing(10)
        
        # Headers
        h1 = QLabel("Grid Coord")
        h2 = QLabel("Probability")
        for h in [h1, h2]:
            h.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
            h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        prob_grid.addWidget(h1, 0, 0)
        prob_grid.addWidget(h2, 0, 1)

        for i, prob in enumerate(details.probabilities):
            row_idx = (i // self.board_cols) + 1
            col_idx = (i % self.board_cols) + 1
            
            lbl_move = QLabel(f"({row_idx}, {col_idx})")
            lbl_prob = QLabel(f"{prob:.3f}")
            
            for lbl in [lbl_move, lbl_prob]:
                lbl.setStyleSheet("font-size: 16px; color: #8b949e;")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            prob_grid.addWidget(lbl_move, i+1, 0)
            prob_grid.addWidget(lbl_prob, i+1, 1)
            
        scroll_area.setWidget(scroll_content)
        self.details_content_layout.addWidget(scroll_area, 1)

        # --- SECTION 3: GAME VALUE ---
        val_lbl = QLabel(f"Expected Game Value: {details.game_value:.2f}")
        val_lbl.setStyleSheet("color: #ff7b72; font-weight: bold; font-size: 22px;")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_content_layout.addWidget(val_lbl)

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

    def set_round(self, round_num: int):
        self.lbl_round.setText(f"Round: {round_num}")

    def reveal_choices(self, hider_r: int, hider_c: int, seeker_r: int, seeker_c: int):
        """Displays markers on the grid showing where both players went."""
        self.clear_markers()
        
        hider_pos = (hider_r, hider_c)
        seeker_pos = (seeker_r, seeker_c)
        
        if hider_pos == seeker_pos:
            # They chose the exact same spot
            btn = self.cell_buttons.get(hider_pos)
            if btn:
                btn.setText("💥") # Collision/Found
        else:
            # Different spots
            btn_h = self.cell_buttons.get(hider_pos)
            if btn_h:
                btn_h.setText("H")
                
            btn_s = self.cell_buttons.get(seeker_pos)
            if btn_s:
                btn_s.setText("S")

    def clear_markers(self):
        """Removes all text markers from the grid."""
        for btn in self.cell_buttons.values():
            btn.setText("")

    def show_simulation_results(self, hider_wins: int, seeker_wins: int, hider_score: int, seeker_score: int, payoff: list):
        """Builds a beautiful summary card and updates the details panel for simulation."""
        self._clear_grid()
        
        # ---------------------------------------------------------
        # 1. BUILD THE RESULTS DASHBOARD (LEFT SIDE)
        # ---------------------------------------------------------
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Simulation Complete")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #58a6ff; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        score_box = QFrame()
        score_box.setStyleSheet("background-color: #21262d; border: 2px solid #30363d; border-radius: 10px;")
        score_layout = QGridLayout(score_box)
        score_layout.setContentsMargins(40, 30, 40, 30)
        score_layout.setSpacing(20)
        
        # --- Hider Stats ---
        lbl_h_title = QLabel("Hider Score")
        lbl_h_title.setStyleSheet("font-size: 18px; color: #8b949e;")
        lbl_h_score = QLabel(str(hider_score))
        lbl_h_score.setStyleSheet("font-size: 48px; font-weight: bold; color: #ffffff;")
        lbl_h_wins = QLabel(f"{hider_wins} Wins")
        lbl_h_wins.setStyleSheet("font-size: 14px; font-weight: bold; color: #79c0ff;") 
        
        # --- Seeker Stats ---
        lbl_s_title = QLabel("Seeker Score")
        lbl_s_title.setStyleSheet("font-size: 18px; color: #8b949e;")
        lbl_s_score = QLabel(str(seeker_score))
        lbl_s_score.setStyleSheet("font-size: 48px; font-weight: bold; color: #ffffff;")
        lbl_s_wins = QLabel(f"{seeker_wins} Wins")
        lbl_s_wins.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff7b72;")
        
        # Add to grid
        score_layout.addWidget(lbl_h_title, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(lbl_h_score, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(lbl_h_wins, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        
        score_layout.addWidget(lbl_s_title, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(lbl_s_score, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(lbl_s_wins, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        results_layout.addWidget(title)
        results_layout.addWidget(score_box)
        results_widget.setLayout(results_layout)

        self.grid_layout.addWidget(results_widget, 0, 0)

        # ---------------------------------------------------------
        # 2. UPDATE THE DETAILS PANEL (RIGHT SIDE - MATRIX ONLY)
        # ---------------------------------------------------------
        # Clear anything currently in the details panel
        while self.details_content_layout.count():
            item = self.details_content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

        if payoff:
            lbl_matrix_title = QLabel("Initial Payoff Matrix")
            lbl_matrix_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
            lbl_matrix_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.details_content_layout.addWidget(lbl_matrix_title)
            
            matrix_scroll = QScrollArea()
            matrix_scroll.setWidgetResizable(True)
            matrix_scroll.setStyleSheet("QScrollArea { border: 1px solid #30363d; border-radius: 8px; background-color: #161b22; }")
            
            matrix_content = QWidget()
            matrix_content.setStyleSheet("background-color: transparent;")
            
            matrix_grid = QGridLayout(matrix_content)
            matrix_grid.setSpacing(8)
            matrix_grid.setAlignment(Qt.AlignmentFlag.AlignCenter) 
            
            for r, row_data in enumerate(payoff):
                for c, val in enumerate(row_data):
                    lbl_val = QLabel(str(val))
                    lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl_val.setFixedSize(60, 60)
                    lbl_val.setStyleSheet("background-color: #21262d; border: 2px solid #30363d; border-radius: 6px; font-size: 18px; font-weight: bold;")
                    matrix_grid.addWidget(lbl_val, r, c)
            
            matrix_scroll.setWidget(matrix_content)
            # Give it a stretch of 1 so it fills the panel completely
            self.details_content_layout.addWidget(matrix_scroll, 1)

    def _build_legend(self):
        legend_layout = QHBoxLayout()
        legend_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legend_layout.setSpacing(25)

        # Helper function to generate a legend item
        def create_legend_item(text: str, color_hex: str):
            item_layout = QHBoxLayout()
            item_layout.setSpacing(8)
            
            color_box = QLabel()
            color_box.setFixedSize(16, 16)
            color_box.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px; border: 1px solid #30363d;")
            
            label = QLabel(text)
            label.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: bold;")
            
            item_layout.addWidget(color_box)
            item_layout.addWidget(label)
            return item_layout

        # Replace these hex values with the actual colors from your theme.qss
        legend_layout.addLayout(create_legend_item("Hard", "#ff7b72"))     # Example: Red
        legend_layout.addLayout(create_legend_item("Neutral", "#8b949e"))  # Example: Dark Grey
        legend_layout.addLayout(create_legend_item("Easy", "#58a6ff"))     # Example: Blue

        return legend_layout