"""
Unit tests for the Romantic racer's get_power_changes method
"""

import unittest
from copy import deepcopy

from MidnightRunners.concreteracers.CR_Romantic import Romantic
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, PositionChange
from MidnightRunners.core.Track import Track, TrackVersion


class TestRomanticGetPowerChanges(unittest.TestCase):
    """Test cases for Romantic.get_power_changes method"""

    def setUp(self):
        """Set up common test fixtures"""
        self.romantic = Romantic(Player.P1, ask_for_input=False)
        self.track = Track(TrackVersion.MILD)

        # Create a 3-player board state
        self.player_to_racer_map = {
            Player.P1: RacerName.ROMANTIC,
            Player.P2: RacerName.GUNK,
            Player.P3: RacerName.BANANA
        }
        self.board_state = BoardState(3, self.track, self.player_to_racer_map)

        # Set initial positions
        self.board_state.racer_name_to_position_map[RacerName.ROMANTIC] = 5
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 3
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 7

    def test_no_pair_created_no_power_activation(self):
        """Test that no power activates when no pair is created"""
        changes = []

        # Gunk moves from 3 to 4 (doesn't create a pair)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 4)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)

    def test_two_racers_arrive_together_power_activates(self):
        """Test that power activates when two racers arrive on the same space"""
        changes = []

        # Gunk moves from 3 to 7 (where Banana already is)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 2)

        # Verify Romantic moved 2 spaces forward
        romantic_move = new_changes[1]
        self.assertEqual(len(romantic_move.position_changes), 1)
        self.assertEqual(romantic_move.position_changes[0].racer_name, RacerName.ROMANTIC)
        self.assertEqual(romantic_move.position_changes[0].old_position, 5)
        self.assertEqual(romantic_move.position_changes[0].new_position, 7)
        self.assertIn("arrived together", romantic_move.change_messages[0])

    def test_both_racers_move_to_same_space_power_activates(self):
        """Test power activates when both racers move to create a pair"""
        changes = []

        # Both Gunk and Banana move to space 10
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 10)
        change.add_pos_change(RacerName.BANANA, 7, 10)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 2)

        # Verify Romantic moved 2 spaces forward
        romantic_move = new_changes[1]
        self.assertEqual(romantic_move.position_changes[0].racer_name, RacerName.ROMANTIC)
        self.assertEqual(romantic_move.position_changes[0].old_position, 5)
        self.assertEqual(romantic_move.position_changes[0].new_position, 7)

    def test_pair_already_exists_no_power_activation(self):
        """Test that power doesn't activate if two racers were already together"""
        # Set both Gunk and Banana at position 7
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 7
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 7

        changes = []

        # Gunk moves from 7 to 8 (pair breaks, doesn't trigger)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 7, 8)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)

    def test_romantic_joins_to_create_pair_no_self_trigger(self):
        """Test that Romantic joining someone doesn't trigger their own power"""
        changes = []

        # Romantic moves to where Gunk is (position 3)
        change = ChangeSet()
        change.add_pos_change(RacerName.ROMANTIC, 5, 3)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        # Power should activate for Romantic joining Gunk
        self.assertTrue(power_activated)

        # But there should be a Romantic move in response
        bs_after = deepcopy(self.board_state)
        bs_after.apply_change_list(new_changes)

        # Romantic should have moved forward by 2 after creating the pair
        romantic_final_pos = bs_after.racer_name_to_position_map[RacerName.ROMANTIC]
        self.assertEqual(romantic_final_pos, 5)  # 3 + 2 = 5

    def test_three_racers_on_same_space_no_power(self):
        """Test that having 3 racers on the same space doesn't trigger power"""
        # Set all three racers at position 10
        self.board_state.racer_name_to_position_map[RacerName.ROMANTIC] = 10
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 10
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 10

        changes = []

        # Someone else moves to position 10
        # Add a 4th racer for this test
        self.board_state.racer_name_to_position_map[RacerName.MOUTH] = 5
        change = ChangeSet()
        change.add_pos_change(RacerName.MOUTH, 5, 10)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        # Power should not activate because there are now 4 racers, not exactly 2
        self.assertFalse(power_activated)

    def test_romantic_moves_forward_from_near_end(self):
        """Test that Romantic's movement is clamped at track end"""
        # Position Romantic near the end
        self.board_state.racer_name_to_position_map[RacerName.ROMANTIC] = 29

        changes = []

        # Two other racers create a pair
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 10)
        change.add_pos_change(RacerName.BANANA, 7, 10)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)

        # Verify Romantic moved but was clamped to position 30 (not 31)
        romantic_move = new_changes[1]
        self.assertEqual(romantic_move.position_changes[0].new_position, 30)

    def test_multiple_pairs_created_in_one_change(self):
        """Test when multiple pairs are created in a single change"""
        # Add more racers for this test
        self.board_state.racer_name_to_position_map[RacerName.MOUTH] = 12
        self.board_state.racer_name_to_position_map[RacerName.SUCKERFISH] = 15

        changes = []

        # Create two separate pairs in one change
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)  # Joins Banana at 7
        change.add_pos_change(RacerName.MOUTH, 12, 15)  # Joins Suckerfish at 15
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)

        # Should have 3 changes: original + 2 romantic moves (one for each pair)
        self.assertEqual(len(new_changes), 3)

    def test_power_processed_only_once_per_change(self):
        """Test that Romantic doesn't reprocess changes already marked as processed"""
        changes = []

        # Create a change and mark it as already processed by Romantic
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        change.racers_processed.add(RacerName.ROMANTIC)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        # Should not activate power since change was already processed
        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)

    def test_one_racer_stays_one_arrives_creates_pair(self):
        """Test pair creation when one racer was already there"""
        # Banana is already at position 10
        self.board_state.racer_name_to_position_map[RacerName.BANANA] = 10

        changes = []

        # Gunk arrives at position 10
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 10)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)

        # Verify power message mentions the pair
        romantic_move = new_changes[1]
        self.assertIn("arrived together", romantic_move.change_messages[0])

    def test_romantic_power_updates_board_state_correctly(self):
        """Test that applying Romantic's power changes updates board state correctly"""
        changes = []

        # Create a pair
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change)

        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)

        # Apply all changes to board state
        bs_after = deepcopy(self.board_state)
        bs_after.apply_change_list(new_changes)

        # Verify final positions
        self.assertEqual(bs_after.racer_name_to_position_map[RacerName.ROMANTIC], 7)
        self.assertEqual(bs_after.racer_name_to_position_map[RacerName.GUNK], 7)
        self.assertEqual(bs_after.racer_name_to_position_map[RacerName.BANANA], 7)

    def test_cascading_romantic_moves(self):
        """Test that Romantic's power considers intermediate board states"""
        changes = []

        # First, move Gunk to create pair with Banana at 7
        change1 = ChangeSet()
        change1.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change1)

        # Process first change
        new_changes, power_activated = self.romantic.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)

        # The Romantic should have moved from 5 to 7
        self.assertEqual(len(new_changes), 2)
        self.assertEqual(new_changes[1].position_changes[0].new_position, 7)


if __name__ == '__main__':
    unittest.main()
