from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QRadioButton, 
                               QFrame, QLineEdit, QButtonGroup, QCheckBox)
from PySide6.QtCore import Qt

class StartScreen(QWidget):
    def __init__(self, start_callback):
        super().__init__()

        master_layout = QVBoxLayout()
        master_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(master_layout)

        # title
        title = QLabel("Hide 'n' Seek")
        title.setObjectName("MainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        master_layout.addWidget(title)
        
        self.card = QFrame()
        self.card.setObjectName("FloatingCard")
        card_layout = QVBoxLayout()
        self.card.setLayout(card_layout)

        # dimension selection
        dim_layout = QHBoxLayout()
        self.radio_1d = QRadioButton("1D")
        self.radio_2d = QRadioButton("2D")
        self.dim_gp = QButtonGroup(self)
        self.dim_gp.addButton(self.radio_1d)
        self.dim_gp.addButton(self.radio_2d)

        dim_layout.addWidget(self.radio_1d)
        dim_layout.addWidget(self.radio_2d)
        card_layout.addLayout(dim_layout)

        # size input
        self.input_1d = QLineEdit()
        self.input_1d.setPlaceholderText("Enter World Size (N)")

        self.input_2d_container = QWidget()
        input_2d_layout = QHBoxLayout()
        input_2d_layout.setContentsMargins(0, 0, 0, 0)
        self.input_rows = QLineEdit()
        self.input_rows.setPlaceholderText("Rows")
        self.input_cols = QLineEdit()
        self.input_cols.setPlaceholderText("Cols")
        input_2d_layout.addWidget(self.input_rows)
        input_2d_layout.addWidget(self.input_cols)
        self.input_2d_container.setLayout(input_2d_layout)

        card_layout.addWidget(self.input_1d)
        card_layout.addWidget(self.input_2d_container)

        # role selection
        role_layout = QHBoxLayout()
        self.radio_hider = QRadioButton("Hider")
        self.radio_hider.setObjectName("RadioHider")
        self.radio_seeker = QRadioButton("Seeker")
        self.radio_seeker.setObjectName("RadioSeeker")
        
        self.role_group = QButtonGroup(self)
        self.role_group.addButton(self.radio_hider)
        self.role_group.addButton(self.radio_seeker)

        role_layout.addWidget(self.radio_hider)
        role_layout.addWidget(self.radio_seeker)
        card_layout.addLayout(role_layout)

        # proximity selection
        prox_layout = QHBoxLayout()
        prox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.check_proximity = QCheckBox("Enable Proximity Penalties")
        self.check_proximity.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_proximity.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Orbitron';
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #58a6ff;
                background-color: #21262d;
            }
            QCheckBox::indicator:checked {
                background-color: #58a6ff;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #79c0ff;
            }
        """)
        prox_layout.addWidget(self.check_proximity)
        
        card_layout.addSpacing(10)
        card_layout.addLayout(prox_layout)
        card_layout.addSpacing(15)

        # buttons
        self.btn_start = QPushButton("Start Game")
        self.btn_start.setObjectName("BtnStart")
        self.btn_start.clicked.connect(self._on_start_clicked)
        
        self.btn_sim = QPushButton("Start Sim")
        self.btn_sim.setObjectName("BtnSim")
        self.btn_sim.clicked.connect(self._on_sim_clicked)
        
        card_layout.addWidget(self.btn_start)
        card_layout.addWidget(self.btn_sim)
        self.start_callback = start_callback

        master_layout.addWidget(self.card)
        self.radio_1d.toggled.connect(self._toggle_dimension_inputs)
        self.radio_2d.toggled.connect(self._toggle_dimension_inputs)

        # initial State
        self.radio_1d.setChecked(True)
        self.radio_hider.setChecked(True)
        self._toggle_dimension_inputs()

    def _toggle_dimension_inputs(self):
        if self.radio_1d.isChecked():
            self.input_1d.setVisible(True)
            self.input_2d_container.setVisible(False)
        else:
            self.input_1d.setVisible(False)
            self.input_2d_container.setVisible(True)

    def _on_start_clicked(self):
        config = self._build_config("interactive")
        self.start_callback(config)

    def _on_sim_clicked(self):
        config = self._build_config("simulation")
        self.start_callback(config)

    def _build_config(self, mode: str):
        is_2d = self.radio_2d.isChecked()
        role = "Hider" if self.radio_hider.isChecked() else "Seeker"

        try:
            n = int(self.input_1d.text()) if self.input_1d.text() else 4
            rows = int(self.input_rows.text()) if self.input_rows.text() else 4
            cols = int(self.input_cols.text()) if self.input_cols.text() else 4
        except ValueError:
            n, rows, cols = 4, 4, 4

        return {
            "is_2d": is_2d,
            "size_n": n,
            "rows": rows,
            "cols": cols,
            "role": role,
            "mode": mode,
            "proximity": self.check_proximity.isChecked()
        }