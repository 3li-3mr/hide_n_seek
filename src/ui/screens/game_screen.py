from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from src.ui.components.details_dialog import DetailsDialog

class GameScreen(QWidget):
    def __init__(self, menu_callback):
        super().__init__()
        self.setLayout(QVBoxLayout())
        
        self.menu_btn = QPushButton("Main Menu")
        self.menu_btn.clicked.connect(menu_callback)
        
        self.details_btn = QPushButton("Show Details")
        self.details_btn.clicked.connect(self.show_details)

        self.layout().addWidget(self.menu_btn)
        self.layout().addWidget(self.details_btn)
        # TODO: Add the grid layout
        
    def show_details(self):
        dialog = DetailsDialog(self)
        dialog.exec()