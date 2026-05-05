from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 150)
        # Apply a specific ID so it matches your floating card CSS
        self.setObjectName("FloatingCard") 
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_label)
        
        btn_layout = QHBoxLayout()
        self.btn_yes = QPushButton("Yes")
        self.btn_yes.setObjectName("BtnRed") # Reuse your green button style
        
        self.btn_no = QPushButton("No")
        self.btn_no.setObjectName("BtnBlue") # Reuse your orange button style
        
        self.btn_yes.clicked.connect(self.accept)
        self.btn_no.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_yes)
        btn_layout.addWidget(self.btn_no)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)