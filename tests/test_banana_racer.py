"""
Unit tests for the Banana racer's get_power_changes method
"""

import unittest
from copy import deepcopy

from MidnightRunners.concreteracers.CR_Banana import Banana
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, PositionChange
from MidnightRunners.core.Track import Track, TrackVersion


class TestBananaGetPowerChanges(unittest.TestCase):
    """Test cases for Banana.get_power_changes method"""

    def setUp(self):
        """Set up common test fixtures"""
        self.banana = Banana(Player.P1, ask_for_input=False)
        self.track = Track(TrackVersion.MILD)

        # Create a simple 2-player board state
        self.player_to_racer_map = {
            Player.P1: RacerName.BANANA,
            Player.P2: RacerName.GUNK
        }
        self.board_state = BoardState(2, self.track, self.player_to_racer_map)

        # Set initial positions
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 5
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 3

    def test_no_passing_no_power_activation(self):
        """Test that no power activates when no one passes Banana"""
        changes = []

        # Gunk moves from 3 to 4, not passing Banana at 5
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 4)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)
        self.assertEqual(len(new_changes[0].trip_changes), 0)

    def test_racer_passes_banana_triggers_trip(self):
        """Test that a racer passing Banana gets tripped"""
        changes = []

        # Gunk moves from 3 to 7, passing Banana at 5
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 1)
        self.assertEqual(len(new_changes[0].trip_changes), 1)
        self.assertEqual(new_changes[0].trip_changes[0].racer_name, RacerName.GUNK)
        self.assertEqual(new_changes[0].trip_changes[0].tripped_after, True)
        self.assertIn("trips", new_changes[0].change_messages[0].lower())

    def test_banana_moving_while_being_passed(self):
        """Test that power works correctly when Banana also moves"""
        changes = []

        # Both racers move: Banana from 5 to 6, Gunk from 3 to 8 (passes Banana)
        change = ChangeSet()
        change.add_pos_change(RacerName.BANANA, 5, 6)
        change.add_pos_change(RacerName.GUNK, 3, 8)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes[0].trip_changes), 1)
        self.assertEqual(new_changes[0].trip_changes[0].racer_name, RacerName.GUNK)

    def test_racer_landing_on_banana_no_trip(self):
        """Test that landing exactly on Banana doesn't trigger trip"""
        changes = []

        # Gunk moves from 3 to 5 (same position as Banana)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 5)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes[0].trip_changes), 0)

    def test_racer_starting_past_banana_no_trip(self):
        """Test that moving when already past Banana doesn't trigger trip"""
        # Set Gunk ahead of Banana
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 7

        changes = []

        # Gunk moves from 7 to 10 (already past Banana)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 7, 10)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes[0].trip_changes), 0)

    def test_multiple_changes_sequential(self):
        """Test power activation across multiple sequential changes"""
        changes = []

        # First change: Gunk moves from 3 to 7 (passes Banana)
        change1 = ChangeSet()
        change1.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change1)

        # Second change: Banana moves from 5 to 8
        change2 = ChangeSet()
        change2.add_pos_change(RacerName.BANANA, 5, 8)
        changes.append(change2)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 2)
        self.assertEqual(len(new_changes[0].trip_changes), 1)

    def test_banana_self_movement_not_processed(self):
        """Test that Banana's own movement doesn't trigger its power"""
        changes = []

        # Only Banana moves
        change = ChangeSet()
        change.add_pos_change(RacerName.BANANA, 5, 8)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes[0].trip_changes), 0)

    def test_three_player_game(self):
        """Test power with three players"""
        # Create 3-player board state
        player_to_racer_map = {
            Player.P1: RacerName.BANANA,
            Player.P2: RacerName.GUNK,
            Player.P3: RacerName.MOUTH
        }
        board_state = BoardState(3, self.track, player_to_racer_map)
        board_state.racer_name_to_position_map[RacerName.BANANA] = 5
        board_state.racer_name_to_position_map[RacerName.GUNK] = 3
        board_state.racer_name_to_position_map[RacerName.MOUTH] = 2

        changes = []

        # Both Gunk and Mouth pass Banana
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        change.add_pos_change(RacerName.MOUTH, 2, 8)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes[0].trip_changes), 2)
        tripped_racers = [tc.racer_name for tc in new_changes[0].trip_changes]
        self.assertIn(RacerName.GUNK, tripped_racers)
        self.assertIn(RacerName.MOUTH, tripped_racers)

    def test_backward_movement_no_trip(self):
        """Test that backward movement doesn't trigger trip"""
        # Set Gunk ahead of Banana
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 7

        changes = []

        # Gunk moves backward from 7 to 4 (crossing Banana backward)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 7, 4)
        changes.append(change)

        new_changes, power_activated = self.banana.get_power_changes(
            self.board_state, changes
        )

        # Should not trigger since passing check requires old_pos < banana < new_pos
        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes[0].trip_changes), 0)


if __name__ == '__main__':
    unittest.main()
