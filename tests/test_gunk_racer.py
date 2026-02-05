"""
Unit tests for the Gunk racer's get_power_changes method
"""

import unittest
from copy import deepcopy

from MidnightRunners.concreteracers.CR_Gunk import Gunk
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, MoveType, PositionChange
from MidnightRunners.core.Track import Track, TrackVersion


class TestGunkGetPowerChanges(unittest.TestCase):
    """Test cases for Gunk.get_power_changes method"""

    def setUp(self):
        """Set up common test fixtures"""
        self.gunk = Gunk(Player.P1, ask_for_input=False)
        self.track = Track(TrackVersion.MILD)

        # Create a 3-player board state
        self.player_to_racer_map = {
            Player.P1: RacerName.GUNK,
            Player.P2: RacerName.BANANA,
            Player.P3: RacerName.ROMANTIC
        }
        self.board_state = BoardState(3, self.track, self.player_to_racer_map)

        # Set initial positions
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 5
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 3
        self.board_state.racer_name_to_position_map[RacerName.ROMANTIC] = 7

    def test_other_racer_main_move_decreased_by_one(self):
        """Test that Gunk decreases another racer's main move by 1"""
        changes = []

        # Banana makes a main move from 3 to 8 (5 spaces)
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        change.add_message(f"{RacerName.BANANA.value} moves from 3 to 8")
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 1)

        # The position change should be modified to go to 7 instead of 8
        self.assertEqual(new_changes[0].position_changes[0].new_position, 7)
        self.assertIn("decreased by 1", new_changes[0].change_messages[-1])

    def test_non_main_move_not_affected(self):
        """Test that non-main moves are not affected by Gunk's power"""
        changes = []

        # Banana makes a non-main move (e.g., power move)
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.POWER)  # Not a main move
        change.add_pos_change_obj(pos_change)
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        # Position should remain unchanged
        self.assertEqual(new_changes[0].position_changes[0].new_position, 8)

    def test_gunk_own_move_not_affected(self):
        """Test that Gunk's own move is not decreased"""
        changes = []

        # Gunk makes a main move
        change = ChangeSet()
        pos_change = PositionChange(RacerName.GUNK, 5, 10)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        # Gunk's position should remain unchanged
        self.assertEqual(new_changes[0].position_changes[0].new_position, 10)

    def test_multiple_racers_all_decreased(self):
        """Test that all racers' main moves in one change are decreased"""
        changes = []

        # Both Banana and Romantic make main moves
        change = ChangeSet()
        pos_change1 = PositionChange(RacerName.BANANA, 3, 8)
        pos_change1.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change1)

        pos_change2 = PositionChange(RacerName.ROMANTIC, 7, 12)
        pos_change2.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change2)
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        # First racer found should trigger the power and return early
        # Only one racer's move should be decreased
        self.assertEqual(len(new_changes), 1)
        decreased_count = sum(1 for pc in new_changes[0].position_changes
                            if (pc.racer_name == RacerName.BANANA and pc.new_position == 7) or
                               (pc.racer_name == RacerName.ROMANTIC and pc.new_position == 11))
        self.assertGreaterEqual(decreased_count, 1)

    def test_move_decreased_flag_prevents_double_decrease(self):
        """Test that the move_decreased flag prevents decreasing the same move twice"""
        changes = []

        # Banana makes a main move
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        change.racer_flags["move_decreased"] = True  # Already decreased
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        # Position should remain at 8 (not decreased again)
        self.assertEqual(new_changes[0].position_changes[0].new_position, 8)

    def test_gunk_already_processed_skips_power(self):
        """Test that power is skipped if Gunk has already processed this change"""
        changes = []

        # Banana makes a main move but Gunk already processed this change
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        change.racers_processed.add(RacerName.GUNK)  # Already processed
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        # Position should remain unchanged
        self.assertEqual(new_changes[0].position_changes[0].new_position, 8)

    def test_racers_processed_reset_when_power_activates(self):
        """Test that racers_processed is reset when power activates"""
        changes = []

        # Banana makes a main move, and some other racer already processed this
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        change.racers_processed.add(RacerName.ROMANTIC)  # Some other racer processed
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        # After Gunk processes, racers_processed should be reset to only Gunk
        self.assertEqual(new_changes[0].racers_processed, {RacerName.GUNK})

    def test_processed_by_track_reset_when_power_activates(self):
        """Test that processed_by_track is reset when power activates"""
        changes = []

        # Banana makes a main move, already processed by track
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        change.processed_by_track = True  # Already processed by track
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        # processed_by_track should be reset so track can process the modified move
        self.assertFalse(new_changes[0].processed_by_track)

    def test_trip_changes_cleared_when_power_activates(self):
        """Test that trip changes are cleared when Gunk's power activates"""
        changes = []

        # Banana makes a main move with a trip change
        change = ChangeSet()
        pos_change = PositionChange(RacerName.BANANA, 3, 8)
        pos_change.set_move_type(MoveType.MAIN)
        change.add_pos_change_obj(pos_change)
        change.add_trip_change(RacerName.BANANA, False, True)  # Banana gets tripped
        change.add_message(f"{RacerName.BANANA.value} moves and trips!")
        changes.append(change)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        # Trip changes should be cleared since the movement changed
        self.assertEqual(len(new_changes[0].trip_changes), 0)

    def test_multiple_changes_only_first_main_move_affected(self):
        """Test that only the first main move triggers power (early return)"""
        changes = []

        # First change: Banana makes a main move
        change1 = ChangeSet()
        pos_change1 = PositionChange(RacerName.BANANA, 3, 8)
        pos_change1.set_move_type(MoveType.MAIN)
        change1.add_pos_change_obj(pos_change1)
        change1.add_message(f"{RacerName.BANANA.value} moves to 8")
        changes.append(change1)

        # Second change: Romantic makes a main move
        change2 = ChangeSet()
        pos_change2 = PositionChange(RacerName.ROMANTIC, 7, 12)
        pos_change2.set_move_type(MoveType.MAIN)
        change2.add_pos_change_obj(pos_change2)
        change2.add_message(f"{RacerName.ROMANTIC.value} moves to 12")
        changes.append(change2)

        new_changes, power_activated = self.gunk.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        # Should return early after processing first change
        self.assertEqual(len(new_changes), 1)
        self.assertEqual(new_changes[0].position_changes[0].new_position, 7)


if __name__ == '__main__':
    unittest.main()
