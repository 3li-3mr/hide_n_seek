import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.ui_manger import UIManager
from PySide6.QtGui import QFontDatabase

def load_stylesheet(app: QApplication):
    """Reads the QSS file and applies it globally."""
    # Ensure the path resolves correctly regardless of where the script is run from
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(base_dir, "styles", "theme.qss")
    
    try:
        with open(qss_path, "r") as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print(f"Warning: Stylesheet not found at {qss_path}")

def load_custom_font():
    # Construct the path to your font file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "assets", "OrbitronBlack-n6dV.ttf")
    
    # Register the font with the OS memory for this app
    font_id = QFontDatabase.addApplicationFont(font_path)
    
    if font_id == -1:
        print(f"Warning: Failed to load font at {font_path}")
    else:
        # Get the exact family name to use in your QSS
        family_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        print(f"Successfully loaded font family: {family_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    load_custom_font()
    # Load CSS
    load_stylesheet(app)
    
    # Boot the UI Controller
    window = UIManager()
    window.show()
    
    sys.exit(app.exec())