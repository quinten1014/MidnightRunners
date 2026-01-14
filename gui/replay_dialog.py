"""
Race replay dialog for viewing completed races
"""

from copy import deepcopy
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QTextEdit, QCheckBox, QSplitter)
from PyQt6.QtCore import QTimer, Qt

from MidnightRunners.core.BoardView import PrintBoardState, PrintChangeList
from gui.board_display import BoardDisplayWidget


class RaceReplayDialog(QDialog):
    """Dialog window for replaying races step by step."""

    def __init__(self, completed_races, overall_config, parent=None):
        super().__init__(parent)
        self.completed_races = completed_races
        self.overall_config = overall_config
        self.current_race_index = 0
        self.current_step = 0
        self.is_playing = False
        self.skip_turn_phase_only_changes = True
        self.skip_no_movement_changes = True

        self.setWindowTitle("Race Replay")
        self.setMinimumSize(1000, 800)

        self._setup_ui()
        self._load_race(0)

    def _setup_ui(self):
        """Setup the replay dialog UI."""
        layout = QVBoxLayout(self)

        # Race selector
        if len(self.completed_races) > 1:
            race_selector_layout = QHBoxLayout()
            race_selector_label = QLabel("Select Race:")
            self.race_selector = QComboBox()
            for i, race_data in enumerate(self.completed_races, 1):
                self.race_selector.addItem(f"Race {i} of {len(self.completed_races)}")
            self.race_selector.currentIndexChanged.connect(self._on_race_changed)
            race_selector_layout.addWidget(race_selector_label)
            race_selector_layout.addWidget(self.race_selector)
            race_selector_layout.addStretch()
            layout.addLayout(race_selector_layout)

        # Info label
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.info_label)

        # Progress label
        self.progress_label = QLabel("Turn 0")
        self.progress_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.progress_label)

        # Create a splitter for graphical display and text display
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Graphical board display
        self.board_display = BoardDisplayWidget()
        splitter.addWidget(self.board_display)

        # Text display area
        self.replay_text = QTextEdit()
        self.replay_text.setReadOnly(True)
        self.replay_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px;")
        splitter.addWidget(self.replay_text)

        # Set initial sizes - give more space to graphical display
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

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

        self.skip_to_end_button = QPushButton("⟲ Skip to End")
        self.skip_to_end_button.clicked.connect(self._skip_to_end)
        controls_layout.addWidget(self.skip_to_end_button)

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

        # Skip turn-phase-only-changes checkbox
        checkbox_layout = QHBoxLayout()
        self.skip_turn_phase_only_checkbox = QCheckBox("Skip changes with only turn phase changes")
        self.skip_turn_phase_only_checkbox.setChecked(True)
        self.skip_turn_phase_only_checkbox.stateChanged.connect(self._on_skip_turn_phase_only_checkbox_changed)
        checkbox_layout.addWidget(self.skip_turn_phase_only_checkbox)
        checkbox_layout.addStretch()
        layout.addLayout(checkbox_layout)

        # Skip no-movement-changes checkbox
        checkbox_layout = QHBoxLayout()
        self.skip_no_movement_checkbox = QCheckBox("Skip changes without movement changes")
        self.skip_no_movement_checkbox.setChecked(True)
        self.skip_no_movement_checkbox.stateChanged.connect(self._on_skip_no_movement_checkbox_changed)
        checkbox_layout.addWidget(self.skip_no_movement_checkbox)
        checkbox_layout.addStretch()
        layout.addLayout(checkbox_layout)

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

        race_data = self.completed_races[race_index]
        self.current_race = race_data['race']
        self.changeset = race_data['changeset']
        self.initial_board_state = race_data['initial_board_state']

        # Update info label
        num_races = len(self.completed_races)
        if num_races > 1:
            race_label = f"Race {race_index + 1} of {num_races}"
        else:
            race_label = "Race"

        track = self.current_race.track.track_version.value
        num_players = self.current_race.num_players
        self.info_label.setText(f"{race_label} | {num_players} Players | Track: {track}")

        self._display_step()

    def _on_race_changed(self, index):
        """Handle race selection change."""
        self._load_race(index)

    def _display_step(self):
        """Display the current step of the replay."""
        # Reconstruct board state at current step
        bs = deepcopy(self.initial_board_state)
        bs.apply_change_list(self.changeset[:self.current_step])

        # Build display text
        text_lines = []
        text_lines.append("="*60)
        text_lines.append("CURRENT STANDINGS:")
        text_lines.append(f"Turn ({bs.current_turn_number}/{self.current_race.num_turns_taken}): {bs.turn_order[0].value}")
        text_lines.append("="*60)

        # Show current board state details
        for player, racer_name in bs.player_to_racer_name_map.items():
            position = bs.racer_name_to_position_map[racer_name]
            pts = bs.player_points_map[player]
            tripped = " (tripped)" if bs.racer_trip_map.get(racer_name, False) else ""
            text_lines.append(f"  {player.value} [{pts} pts]: {racer_name.value} at position {position}{tripped}")
        text_lines.append("")

        # Show changes up to current step
        if self.current_step > 0 and self.changeset:
            show_up_to_index = min(self.current_step, len(self.changeset))
            start_index = max(0, show_up_to_index - 20)  # Show last few changes for context
            for i in reversed(range(start_index, show_up_to_index)):
                change = self.changeset[i]
                if change.change_messages and self._change_viewable(change):
                    text_lines.append("-" * 60)
                    for msg in change.change_messages:
                        text_lines.append(f"  {msg}")

        if self.current_step >= (len(self.changeset) if self.changeset else 0):
            text_lines.append("")
            text_lines.append("="*60)
            text_lines.append("RACE COMPLETE!")
            text_lines.append("="*60)
            text_lines.append(f"Winner: {bs.first_place_racer.value if bs.first_place_racer else 'N/A'}")
            text_lines.append(f"Second Place: {bs.second_place_racer.value if bs.second_place_racer else 'N/A'}")

        self.replay_text.setText("\n".join(text_lines))

        # Update graphical board display
        self.board_display.set_board_state(bs, self.current_race.track)

        # Update progress
        total_steps = len(self.changeset) if self.changeset else 0
        self.progress_label.setText(f"Step {self.current_step} of {total_steps}")

        # Update button states
        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setEnabled(self.current_step < total_steps)

    def _prev_step(self, items_skipped = 0):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            if self.current_step > 0:
                current_change = self.changeset[self.current_step]
                if self._change_skippable(current_change):
                    self._prev_step(items_skipped + 1)
                elif items_skipped == 0 and self._change_skippable(current_change):
                    self._prev_step(items_skipped=0)
                elif items_skipped and self.current_step > 0:
                    self.current_step += 1
            self._display_step()

    def _next_step(self, items_skipped = 0):
        """Go to next step."""
        total_steps = len(self.changeset) if self.changeset else 0
        if self.current_step < total_steps:
            self.current_step += 1
            if self.current_step < total_steps:
                current_change = self.changeset[self.current_step]
                if self._change_skippable(current_change):
                    self._next_step(items_skipped + 1)
                elif items_skipped and self.current_step < total_steps:
                    self.current_step += 1
            self._display_step()

            # Stop playing if we reach the end
            if self.current_step >= total_steps and self.is_playing:
                self._toggle_play()

    def _change_viewable(self, change) -> bool:
        """Check if a change is viewable based on current settings."""
        if (len(change.change_messages) == 1 and change.turn_phase_changes) and self.skip_turn_phase_only_changes:
            return False
        return True

    def _change_skippable(self, change) -> bool:
        """Check if a change is skippable based on current settings."""
        if (not change.position_changes) and self.skip_no_movement_changes:
            return True
        if (len(change.change_messages) == 1 and change.turn_phase_changes) and self.skip_turn_phase_only_changes:
            return True
        return False

    def _skip_to_end(self):
        """Skip to the end of the replay."""
        total_steps = len(self.changeset) if self.changeset else 0
        self.current_step = total_steps
        self._display_step()

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

    def _on_skip_turn_phase_only_checkbox_changed(self, state):
        """Handle skip turn-phase-only-changes checkbox state change."""
        # Refresh internal next/prev step behavior flag so that changes with only turn phase changes are/are not skipped
        self.skip_turn_phase_only_changes = (state == 2)  # Checked state is 2
        self._display_step()

    def _on_skip_no_movement_checkbox_changed(self, state):
        """Handle skip changes without movement changes checkbox state change."""
        # Refresh internal next/prev step behavior flag so that changes with no messages are/are not skipped
        self.skip_no_movement_changes = (state == 2)  # Checked state is 2
        self._display_step()