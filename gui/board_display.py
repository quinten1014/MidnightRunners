"""
Custom widget for displaying the race track and racers in 2D
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from MidnightRunners.concreteracers.RacerList import RacerNameToColorMap
from MidnightRunners.core.Track import SpecialSpaceProperties


class BoardDisplayWidget(QWidget):
    """Custom widget for drawing the race track and racers in 2D."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_state = None
        self.track = None
        self.setMinimumHeight(300)
        self.setMaximumHeight(400)

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

        line_height = 170
        overshoot = 30

        for i in range(track_length):
            x = margin + i * space_width

            # Draw space marker
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(int(x - 3), int(track_y - 3), 6, 6)

            # Draw vertical line for space
            if (i < track_length - 1):
                x_line = x + (space_width/2)
                painter.drawLine(int(x_line), int(track_y + overshoot), int(x_line), int(track_y - line_height))

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
                # Draw racer circle
                racer_size = 20
                painter.setBrush(QColor(*RacerNameToColorMap[racer_name]))
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.drawEllipse(int(x - racer_size/2), int(track_y + y_offset - racer_size/2),
                                   racer_size, racer_size)

                # Draw racer initial in circle
                initial = racer_name.value[0]
                initial_width = painter.fontMetrics().boundingRect(initial).width()
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(int(x - (initial_width/2)), int(track_y + y_offset + 6), initial)

                # Draw trip indicator
                indicator = "✕"
                indicator_width = painter.fontMetrics().boundingRect(indicator).width()
                if self.board_state.racer_trip_map.get(racer_name, False):
                    painter.setPen(QPen(QColor(255, 255, 255), 20))
                    painter.drawText(int(x - (indicator_width/2)), int(track_y + y_offset + 6), indicator)

                y_offset -= 30

        # Draw legend
        legend_y = track_y + line_height
        legend_x = margin
        legend_font = QFont("Arial", 9)
        painter.setFont(legend_font)

        for player, racer_name in self.board_state.player_to_racer_name_map.items():
            color = QColor(*RacerNameToColorMap[racer_name])

            # Draw color circle
            circle_size = 15
            painter.setBrush(color)
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(int(legend_x), int(legend_y - circle_size/2), circle_size, circle_size)

            # Draw racer name
            painter.setPen(QColor(0, 0, 0))
            text = f"{player.value}: {racer_name.value}"
            painter.drawText(int(legend_x + circle_size + 8), int(legend_y + 5), text)

            # Move to next legend entry
            text_width = painter.fontMetrics().boundingRect(text).width()
            legend_x += circle_size + text_width + 30
