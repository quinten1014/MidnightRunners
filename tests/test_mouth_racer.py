"""
Unit tests for the Mouth racer's get_power_changes method
"""

import unittest
from copy import deepcopy

from MidnightRunners.concreteracers.CR_Mouth import Mouth
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, PositionChange
from MidnightRunners.core.Track import Track, TrackVersion


class TestMouthGetPowerChanges(unittest.TestCase):
    """Test cases for Mouth.get_power_changes method"""

    def setUp(self):
        """Set up common test fixtures"""
        self.mouth = Mouth(Player.P1, ask_for_input=False)
        self.track = Track(TrackVersion.MILD)

        # Create a 3-player board state
        self.player_to_racer_map = {
            Player.P1: RacerName.MOUTH,
            Player.P2: RacerName.GUNK,
            Player.P3: RacerName.BANANA
        }
        self.board_state = BoardState(3, self.track, self.player_to_racer_map)

        # Set initial positions
        self.board_state.racer_name_to_position_map[RacerName.MOUTH] = 5
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 7
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 3

    def test_mouth_lands_on_empty_space_no_elimination(self):
        """Test that no elimination occurs when Mouth lands on an empty space"""
        changes = []

        # Mouth moves from 5 to 10 (empty space)
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 10)
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)
        self.assertEqual(len(new_changes[0].eliminate_changes), 0)

    def test_mouth_lands_on_exactly_one_racer_elimination(self):
        """Test that Mouth eliminates a racer when landing on a space with exactly one other racer"""
        changes = []

        # Mouth moves from 5 to 7 (where Gunk is alone)
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 7)
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 2)
        self.assertEqual(len(new_changes[1].eliminate_changes), 1)
        self.assertEqual(new_changes[1].eliminate_changes[0].racer_name, RacerName.GUNK)
        self.assertIn("eliminates", new_changes[1].change_messages[0])

        # Verify the eliminated racer is in the eliminated set after applying changes
        bs_after = deepcopy(self.board_state)
        bs_after.apply_change_list(new_changes)
        self.assertIn(RacerName.GUNK, bs_after.eliminated_racers)

    def test_mouth_lands_on_two_racers_no_elimination(self):
        """Test that no elimination occurs when Mouth lands on a space with two other racers"""
        # Set up both Gunk and Banana at position 7
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 7
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 7

        changes = []

        # Mouth moves from 5 to 7 (where both Gunk and Banana are)
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 7)
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)
        self.assertEqual(len(new_changes[0].eliminate_changes), 0)

    def test_mouth_does_not_move_no_elimination(self):
        """Test that no elimination occurs when Mouth doesn't move"""
        # Set Gunk at Mouth's position
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 5

        changes = []

        # Only Banana moves, not Mouth
        change = ChangeSet()
        change.add_pos_change(RacerName.BANANA, 3, 8)
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)

    def test_mouth_and_one_racer_move_to_same_space_elimination(self):
        """Test elimination when Mouth and another racer both move to the same space"""
        changes = []

        # Both Mouth and Gunk move to space 10
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 10)
        change.add_pos_change(RacerName.GUNK, 7, 10)
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 2)
        self.assertEqual(new_changes[1].eliminate_changes[0].racer_name, RacerName.GUNK)

    def test_multiple_changes_only_eliminates_on_mouth_move(self):
        """Test that elimination only happens on changes where Mouth moves"""
        changes = []

        # First change: Other racers move (not Mouth)
        change1 = ChangeSet()
        change1.add_pos_change(RacerName.GUNK, 7, 8)
        changes.append(change1)

        # Second change: Mouth moves to where Banana is alone
        change2 = ChangeSet()
        change2.add_pos_change(RacerName.MOUTH, 5, 3)
        changes.append(change2)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        # Should have 3 changes: original 2 + 1 elimination change
        self.assertEqual(len(new_changes), 3)
        # The elimination should be in the third change (added after change2)
        self.assertEqual(len(new_changes[2].eliminate_changes), 1)
        self.assertEqual(new_changes[2].eliminate_changes[0].racer_name, RacerName.BANANA)

    def test_mouth_already_processed_skips_power(self):
        """Test that power is skipped if Mouth has already processed this change"""
        changes = []

        # Mouth moves to where Gunk is
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 7)
        change.racers_processed.add(RacerName.MOUTH)  # Mark as already processed
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)
        self.assertEqual(len(new_changes[0].eliminate_changes), 0)

    def test_elimination_message_contains_details(self):
        """Test that the elimination message contains relevant details"""
        changes = []

        # Mouth moves to where Banana is at position 3
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 3)
        changes.append(change)

        new_changes, power_activated = self.mouth.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        elimination_message = new_changes[1].change_messages[0]
        self.assertIn("Mouth", elimination_message)
        self.assertIn("Banana", elimination_message)
        self.assertIn("3", elimination_message)
        self.assertIn("eliminates", elimination_message)


if __name__ == '__main__':
    unittest.main()
