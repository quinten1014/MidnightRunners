"""
Midnight Runners - Board Game
Entry point for the game
"""

import sys
from PyQt6.QtWidgets import QApplication

from gui import MidnightRunnersMainWindow


def main():
    """Main entry point for the game."""
    app = QApplication(sys.argv)
    window = MidnightRunnersMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
