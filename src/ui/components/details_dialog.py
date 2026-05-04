from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

class DetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Matrix Details")
        self.setLayout(QVBoxLayout())
        # TODO: Add grid layout for probabilities