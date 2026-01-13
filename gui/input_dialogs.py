"""
Input dialogs for game interactions
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QSpinBox, QApplication)
from PyQt6.QtCore import Qt


class DiceRollInputDialog(QDialog):
    """Dialog for manually entering dice roll values."""

    def __init__(self, racer_name, min_value=1, max_value=6, parent=None):
        super().__init__(parent)
        self.racer_name = racer_name
        self.roll_value = None

        self.setWindowTitle("Enter Dice Roll")
        self.setModal(True)
        self.setMinimumWidth(350)

        self._setup_ui(min_value, max_value)

    def _setup_ui(self, min_value, max_value):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(f"Enter the main move roll for {self.racer_name}:")
        info_label.setStyleSheet("font-size: 13px; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Spinbox for roll value
        spinbox_layout = QHBoxLayout()
        spinbox_label = QLabel("Roll Value:")
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(min_value)
        self.spinbox.setMaximum(max_value)
        self.spinbox.setValue(min_value)
        self.spinbox.setStyleSheet("font-size: 14px; padding: 5px;")
        self.spinbox.setMinimumWidth(80)
        spinbox_layout.addWidget(spinbox_label)
        spinbox_layout.addWidget(self.spinbox)
        spinbox_layout.addStretch()
        layout.addLayout(spinbox_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        confirm_button = QPushButton("Confirm")
        confirm_button.setStyleSheet("font-size: 12px; padding: 8px 20px;")
        confirm_button.clicked.connect(self._on_confirm)
        confirm_button.setDefault(True)
        button_layout.addWidget(confirm_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Allow Enter key to confirm
        self.spinbox.setFocus()

    def _on_confirm(self):
        """Handle confirm button click."""
        self.roll_value = self.spinbox.value()
        self.accept()

    @staticmethod
    def get_roll_value(racer_name, min_value=1, max_value=6, parent=None):
        """
        Static method to show dialog and get roll value.
        Returns the roll value or None if canceled.
        """
        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            # If called from non-GUI context, fall back to console input
            return None

        dialog = DiceRollInputDialog(racer_name, min_value, max_value, parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.roll_value
        return None
