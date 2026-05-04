from PySide6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.screens.start_screen import StartScreen
from src.ui.screens.game_screen import GameScreen

class UIManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Operations Research: Hide & Seek")
        self.setFixedSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Instantiate screens and pass the routing methods
        self.start_screen = StartScreen(self.route_to_game)
        self.game_screen = GameScreen(self.route_to_menu)

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.game_screen)

    def route_to_game(self):
        self.stack.setCurrentIndex(1)

    def route_to_menu(self):
        self.stack.setCurrentIndex(0)