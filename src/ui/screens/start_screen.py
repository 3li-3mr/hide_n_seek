from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class StartScreen(QWidget):
    def __init__(self, start_callback):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.start_btn = QPushButton("Start Game")
        self.start_btn.clicked.connect(start_callback)
        self.layout().addWidget(self.start_btn)
        # TODO: Add textboxes for dimensions and role selection