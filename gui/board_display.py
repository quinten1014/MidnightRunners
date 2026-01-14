"""
Custom widget for displaying the race track and racers in 2D
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from MidnightRunners.core.Track import SpecialSpaceProperties


class BoardDisplayWidget(QWidget):
    """Custom widget for drawing the race track and racers in 2D."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_state = None
        self.track = None
        self.setMinimumHeight(300)
        self.setMaximumHeight(400)

        # Color mapping for players
        self.player_colors = {
            'Player 1': QColor(255, 100, 100),  # Red
            'Player 2': QColor(100, 100, 255),  # Blue
            'Player 3': QColor(100, 255, 100),  # Green
            'Player 4': QColor(255, 255, 100),  # Yellow
        }

    def set_board_state(self, board_state, track):
        """Update the board state to display."""
        self.board_state = board_state
        self.track = track
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """Draw the board and racers."""
        if not self.board_state or not self.track:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        width = self.width()
        height = self.height()
        margin = 40
        track_length = 31  # Positions 0-30

        # Draw track
        track_y = height // 2
        track_width = width - 2 * margin
        space_width = track_width / (track_length - 1)

        # Draw track line
        painter.setPen(QPen(QColor(50, 50, 50), 3))
        painter.drawLine(margin, track_y, width - margin, track_y)

        # Draw spaces and special properties
        font = QFont("Arial", 8)
        painter.setFont(font)

        for i in range(track_length):
            x = margin + i * space_width

            # Draw space marker
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(int(x - 3), int(track_y - 3), 6, 6)

            # Draw vertical line for space
            overshoot = 30
            if (i < track_length - 1):
                x_line = x + (space_width/2)
                painter.drawLine(int(x_line), int(track_y + overshoot), int(x_line), int(-(height/2) + margin))

            # Draw space number
            height = painter.fontMetrics().boundingRect(str(i)).height()
            painter.drawText(int(x - (height / 2)), int(track_y + 20), str(i))
            # painter.sePen(QPen(QColor(50, 50, 50), 3))
            # painter.drtawLine(margin, track_y, width - margin, track_y)

            # Draw special properties
            base_vertical_offset = 30
            if i < len(self.track.space_properties):
                properties = self.track.space_properties[i]
                y_offset = 0
                for prop in properties:
                    painter.save()  # Save the current state
                    painter.translate(x, track_y + base_vertical_offset + y_offset)  # Move to the text position
                    painter.rotate(-90)  # Rotate -90 degrees
                    color = QColor(0, 0, 0)
                    text = ""

                    if prop == SpecialSpaceProperties.START:
                        color = QColor(0, 200, 0)
                        text = "START"
                    elif prop == SpecialSpaceProperties.FINISH:
                        color = QColor(200, 0, 0)
                        text = "FINISH"
                    elif prop == SpecialSpaceProperties.TRIP:
                        color = QColor(150, 0, 150)
                        text = "TRIP"
                    elif "ARROW" in prop.name:
                        color = QColor(0, 0, 200)
                        arrow_sign = "→"
                        if "MINUS" in prop.name:
                            arrow_sign = "←"
                        text = prop.name.replace("ARROW_", arrow_sign)
                    elif "STAR" in prop.name:
                        color = QColor(255, 200, 0)
                        text = "★"

                    width = painter.fontMetrics().boundingRect(text).width()
                    painter.translate(- width, 0)
                    painter.setPen(color)
                    painter.drawText(0, 5, text)

                    painter.restore()  # Restore the previous state
                    y_offset += width

        # Draw racers
        racer_positions = {}
        for racer_name, position in self.board_state.racer_name_to_position_map.items():
            if position not in racer_positions:
                racer_positions[position] = []
            racer_positions[position].append(racer_name)

        font_bold = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font_bold)

        for position, racers in racer_positions.items():
            x = margin + position * space_width
            y_offset = -50

            for racer_name in racers:
                player = self.board_state.get_player_by_racer(racer_name)
                color = self.player_colors.get(player.value, QColor(128, 128, 128))

                # Draw racer circle
                racer_size = 20
                painter.setBrush(color)
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.drawEllipse(int(x - racer_size/2), int(track_y + y_offset - racer_size/2),
                                   racer_size, racer_size)

                # Draw racer initial in circle
                painter.setPen(QColor(255, 255, 255))
                initial = racer_name.value[0]
                painter.drawText(int(x - 6), int(track_y + y_offset + 6), initial)

                # Draw trip indicator
                if self.board_state.racer_trip_map.get(racer_name, False):
                    painter.setPen(QPen(QColor(255, 0, 0), 3))
                    painter.drawText(int(x + 15), int(track_y + y_offset + 6), "✕")

                y_offset -= 30
