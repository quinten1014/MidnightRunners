"""
Race live dialog for stepping through ongoing races
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QTextEdit)
from PyQt6.QtCore import QTimer


class RaceLiveDialog(QDialog):
    """Dialog window for showing live races step by step."""

    def __init__(self, race_config, parent=None):
        super().__init__(parent)
        self.race_config = race_config
        self.current_race_index = 0
        self.current_step = 0
        self.is_playing = False

        self.setWindowTitle("Race Replay")
        self.setMinimumSize(700, 600)

        self._setup_ui()
        self._load_race(0)

    def _setup_ui(self):
        """Setup the replay dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.info_label)

        # Progress label
        self.progress_label = QLabel("Turn 0")
        self.progress_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.progress_label)

        # Text display area
        self.replay_text = QTextEdit()
        self.replay_text.setReadOnly(True)
        self.replay_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px;")
        layout.addWidget(self.replay_text)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.prev_button = QPushButton("◄ Previous Turn")
        self.prev_button.clicked.connect(self._prev_step)
        controls_layout.addWidget(self.prev_button)

        self.play_pause_button = QPushButton("▶ Play")
        self.play_pause_button.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self.play_pause_button)

        self.next_button = QPushButton("Next Turn ►")
        self.next_button.clicked.connect(self._next_step)
        controls_layout.addWidget(self.next_button)

        self.restart_button = QPushButton("⟲ Restart")
        self.restart_button.clicked.connect(self._restart)
        controls_layout.addWidget(self.restart_button)

        layout.addLayout(controls_layout)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Playback Speed:")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Slow (2s)", "Normal (1s)", "Fast (0.5s)", "Very Fast (0.2s)"])
        self.speed_combo.setCurrentIndex(1)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_combo)
        speed_layout.addStretch()
        layout.addLayout(speed_layout)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        # Timer for auto-play
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self._auto_advance)

    def _load_race(self, race_index):
        """Load a specific race for replay."""
        self.current_race_index = race_index
        self.current_step = 0
        self.is_playing = False
        self.play_timer.stop()
        self.play_pause_button.setText("▶ Play")

        self.current_race = self.race_config.race
        self.changeset = self.race_config.changeset

        track = self.current_race.track.track_version.value
        num_players = self.current_race.num_players
        self.info_label.setText(f"{num_players} Players | Track: {track}")

        self._display_step()

    def _on_race_changed(self, index):
        """Handle race selection change."""
        self._load_race(index)

    def _display_step(self):
        """Display the current step of the replay."""
        # Build display text
        text_lines = []
        text_lines.append("="*60)
        text_lines.append("STARTING POSITIONS:")
        text_lines.append("="*60)

        # Show initial lineup
        bs = self.current_race.board_state
        for player in bs.turn_order:
            racer_name = bs.player_to_racer_name_map[player]
            position = bs.racer_name_to_position_map[racer_name]
            text_lines.append(f"  {player.value}: {racer_name.value} at position {position}")
        text_lines.append("")

        # Show changes up to current step
        if self.current_step > 0 and self.changeset:
            num_changes = min(self.current_step, len(self.changeset))
            for i in range(num_changes):
                change = self.changeset[i]
                if change.change_messages:
                    text_lines.append("-" * 60)
                    for msg in change.change_messages:
                        text_lines.append(f"  {msg}")

        if self.current_step >= len(self.changeset) if self.changeset else 0:
            text_lines.append("")
            text_lines.append("="*60)
            text_lines.append("RACE COMPLETE!")
            text_lines.append("="*60)
            text_lines.append(f"Winner: {bs.first_place_racer.value}")
            text_lines.append(f"Second Place: {bs.second_place_racer.value}")

        self.replay_text.setText("\n".join(text_lines))

        # Update progress
        total_steps = len(self.changeset) if self.changeset else 0
        self.progress_label.setText(f"Step {self.current_step} of {total_steps}")

        # Update button states
        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setEnabled(self.current_step < total_steps)

    def _prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._display_step()

    def _next_step(self):
        """Go to next step."""
        total_steps = len(self.changeset) if self.changeset else 0
        if self.current_step < total_steps:
            self.current_step += 1
            self._display_step()

            # Stop playing if we reach the end
            if self.current_step >= total_steps and self.is_playing:
                self._toggle_play()

    def _restart(self):
        """Restart the replay from the beginning."""
        if self.is_playing:
            self._toggle_play()
        self.current_step = 0
        self._display_step()

    def _toggle_play(self):
        """Toggle auto-play mode."""
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_pause_button.setText("⏸ Pause")
            # Get speed from combo box
            speeds = [2000, 1000, 500, 200]  # milliseconds
            speed_index = self.speed_combo.currentIndex()
            self.play_timer.start(speeds[speed_index])
        else:
            self.play_pause_button.setText("▶ Play")
            self.play_timer.stop()

    def _auto_advance(self):
        """Auto-advance to next step during playback."""
        total_steps = len(self.changeset) if self.changeset else 0
        if self.current_step < total_steps:
            self._next_step()
        else:
            self._toggle_play()
