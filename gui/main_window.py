"""
Main window for Midnight Runners race setup
"""

from copy import deepcopy
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QComboBox, QGroupBox,
                              QMessageBox, QSpinBox)
from PyQt6.QtCore import Qt

from MidnightRunners.concreteracers.CR_Banana import Banana
from MidnightRunners.concreteracers.CR_Gunk import Gunk
from MidnightRunners.concreteracers.CR_Mouth import Mouth
from MidnightRunners.concreteracers.CR_Romantic import Romantic
from MidnightRunners.concreteracers.CR_Suckerfish import Suckerfish
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.Race import Race
from MidnightRunners.core.Track import TrackVersion
from MidnightRunners.core.Player import Player

from .replay_dialog import RaceReplayDialog


class MidnightRunnersMainWindow(QMainWindow):
    """Main window for setting up and running Midnight Runners races."""

    # Default racer selections for each player position (easy to modify)
    DEFAULT_RACERS = [
        RacerName.BANANA.value,
        RacerName.SUCKERFISH.value,
        RacerName.ROMANTIC.value,
        RacerName.GUNK.value,
        RacerName.MOUTH.value,
        RacerName.BANANA.value,  # Player 6 (if needed)
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Midnight Runners - Setup")
        self.setMinimumSize(600, 400)

        # Map racer names to their classes
        self.racer_classes = {
            RacerName.BANANA.value: Banana,
            RacerName.ROMANTIC.value: Romantic,
            RacerName.GUNK.value: Gunk,
            RacerName.MOUTH.value: Mouth,
            RacerName.SUCKERFISH.value: Suckerfish,
        }

        # Player selection dropdowns
        self.player_combos = {}

        # Store race results for replay
        self.completed_races = []
        self.last_race_config = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Midnight Runners - Race Setup")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Track selection
        track_group = QGroupBox("Track Selection")
        track_layout = QHBoxLayout()
        track_label = QLabel("Track Version:")
        self.track_combo = QComboBox()
        self.track_combo.addItems([TrackVersion.MILD.value, TrackVersion.WILD.value])
        self.track_combo.setCurrentText(TrackVersion.WILD.value)
        track_layout.addWidget(track_label)
        track_layout.addWidget(self.track_combo)
        track_layout.addStretch()
        track_group.setLayout(track_layout)
        main_layout.addWidget(track_group)

        # Race repetition selection
        repetition_group = QGroupBox("Race Repetition")
        repetition_layout = QHBoxLayout()
        repetition_label = QLabel("Number of Races:")
        self.race_count_spinbox = QSpinBox()
        self.race_count_spinbox.setMinimum(1)
        self.race_count_spinbox.setMaximum(1000)
        self.race_count_spinbox.setValue(1)
        self.race_count_spinbox.setSuffix(" race(s)")
        repetition_layout.addWidget(repetition_label)
        repetition_layout.addWidget(self.race_count_spinbox)
        repetition_layout.addStretch()
        repetition_group.setLayout(repetition_layout)
        main_layout.addWidget(repetition_group)

        # Player/Racer selection
        players_group = QGroupBox("Player & Racer Selection")
        players_layout = QVBoxLayout()

        # Number of players selector
        num_players_layout = QHBoxLayout()
        num_players_label = QLabel("Number of Players:")
        self.num_players_combo = QComboBox()
        self.num_players_combo.addItems(["2", "3", "4", "5", "6"])
        self.num_players_combo.setCurrentText("4")
        self.num_players_combo.currentTextChanged.connect(self._update_player_fields)
        num_players_layout.addWidget(num_players_label)
        num_players_layout.addWidget(self.num_players_combo)
        num_players_layout.addStretch()
        players_layout.addLayout(num_players_layout)

        # Container for player selection rows
        self.player_rows_widget = QWidget()
        self.player_rows_layout = QVBoxLayout(self.player_rows_widget)
        self.player_rows_layout.setContentsMargins(0, 0, 0, 0)
        players_layout.addWidget(self.player_rows_widget)

        players_group.setLayout(players_layout)
        main_layout.addWidget(players_group)

        # Initialize player selection rows
        self._update_player_fields()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_race_button = QPushButton("Start Race")
        self.start_race_button.setStyleSheet("font-size: 14px; padding: 10px 30px;")
        self.start_race_button.clicked.connect(self._start_race)
        button_layout.addWidget(self.start_race_button)

        self.watch_replay_button = QPushButton("Watch Replay")
        self.watch_replay_button.setStyleSheet("font-size: 14px; padding: 10px 30px;")
        self.watch_replay_button.clicked.connect(self._watch_replay)
        self.watch_replay_button.setEnabled(False)
        button_layout.addWidget(self.watch_replay_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        main_layout.addStretch()

    def _update_player_fields(self):
        """Update the number of player selection rows based on selected player count."""
        # Clear existing rows
        while self.player_rows_layout.count():
            item = self.player_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.player_combos.clear()

        num_players = int(self.num_players_combo.currentText())
        available_players = [Player.P1, Player.P2, Player.P3, Player.P4, Player.P5, Player.P6]

        # Create a row for each player
        for i in range(num_players):
            player = available_players[i]
            row_layout = QHBoxLayout()

            # Player label
            player_label = QLabel(f"Player {i+1} ({player.value}):")
            player_label.setMinimumWidth(120)
            row_layout.addWidget(player_label)

            # Racer selection combo box
            racer_combo = QComboBox()
            racer_combo.addItems(sorted(self.racer_classes.keys()))

            # Set default racer based on DEFAULT_RACERS list
            if i < len(self.DEFAULT_RACERS):
                default_racer = self.DEFAULT_RACERS[i]
                if default_racer in self.racer_classes:
                    racer_combo.setCurrentText(default_racer)
                else:
                    racer_combo.setCurrentIndex(i % len(self.racer_classes))
            else:
                racer_combo.setCurrentIndex(i % len(self.racer_classes))

            row_layout.addWidget(racer_combo)

            self.player_combos[player] = racer_combo
            self.player_rows_layout.addLayout(row_layout)

    def _start_race(self):
        """Start the race with the selected configuration."""
        # Build player to racer configuration (not instantiated yet)
        player_racer_config = {}
        used_racers = set()

        for player, combo in self.player_combos.items():
            racer_name = combo.currentText()

            # Check for duplicate racer selection
            if racer_name in used_racers:
                QMessageBox.warning(
                    self,
                    "Duplicate Racer",
                    f"Each racer can only be selected once!\n'{racer_name}' is selected multiple times."
                )
                return

            used_racers.add(racer_name)
            racer_class = self.racer_classes[racer_name]
            player_racer_config[player] = racer_class

        # Get track version
        track_version_str = self.track_combo.currentText()
        track_version = TrackVersion.MILD if track_version_str == TrackVersion.MILD.value else TrackVersion.WILD

        # Get number of races to run
        num_races = self.race_count_spinbox.value()

        # Clear previous race data
        self.completed_races = []
        self.overall_config = {
            'track_version': track_version,
            'player_racer_config': player_racer_config,
            'num_races': num_races
        }

        # Run multiple races
        # try:
        print("\n" + "="*70)
        print(f"=== Starting {num_races} Race(s) with Same Configuration ===")
        print("="*70)

        for race_num in range(1, num_races + 1):
            # Create fresh racer instances for each race
            player_to_racer_map = {player: racer_class(player) for player, racer_class in player_racer_config.items()}

            race = Race(track_version=track_version, player_to_racer_map=player_to_racer_map)
            initial_board_state = deepcopy(race.board_state)

            # Display game info in console
            print("\n" + "="*50)
            if num_races > 1:
                print(f"=== Race {race_num} of {num_races} ===")
            else:
                print("=== Midnight Runners ===")
            print(f"Players: {race.num_players} | Track: {race.track.track_version.value}")
            print()

            # Display players
            print("Starting Lineup:")
            for player, racer_name in race.board_state.player_to_racer_name_map.items():
                position = race.board_state.racer_name_to_position_map[racer_name]
                print(f"  {player.value}: {racer_name} at position {position}")
            print("="*50 + "\n")

            # Run the race
            full_race_changeset = race.do_race()

            # Store race data for replay
            self.completed_races.append({
                'race_number': race_num,
                'race': race,
                'initial_board_state': initial_board_state,
                'changeset': full_race_changeset
            })

            print(f"\n>>> Race {race_num} Complete <<<\n")

        print("="*70)
        print(f"=== All {num_races} Race(s) Complete ===")
        print("="*70 + "\n")

        # Enable replay button
        self.watch_replay_button.setEnabled(True)

        QMessageBox.information(
            self,
            "All Races Complete",
            f"{num_races} race(s) finished! Check the console for details."
        )

        ###### NOTE: Exception handling disabled for easier debugging ######
        # except Exception as e:
        #     print(f"Error during race: {str(e)}")
        #     QMessageBox.critical(
        #         self,
        #         "Error",
        #         f"An error occurred while running the race:\n{str(e)}"
        #     )

    def _watch_replay(self):
        """Open the replay dialog to watch completed races."""
        if not self.completed_races:
            QMessageBox.warning(self, "No Races", "No completed races to replay!")
            return

        replay_dialog = RaceReplayDialog(self.completed_races, self.overall_config, self)
        replay_dialog.exec()
