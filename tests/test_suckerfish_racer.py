"""
Unit tests for the Suckerfish racer's get_power_changes method
"""

import unittest
from copy import deepcopy
from unittest.mock import MagicMock

from MidnightRunners.concreteracers.CR_Suckerfish import Suckerfish
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, PositionChange
from MidnightRunners.core.Track import Track, TrackVersion


class TestSuckerfishGetPowerChanges(unittest.TestCase):
    """Test cases for Suckerfish.get_power_changes method"""

    def setUp(self):
        """Set up common test fixtures"""
        self.suckerfish = Suckerfish(Player.P1, ask_for_input=False)
        self.track = Track(TrackVersion.MILD)

        # Create a simple 2-player board state
        self.player_to_racer_map = {
            Player.P1: RacerName.SUCKERFISH,
            Player.P2: RacerName.GUNK
        }
        self.board_state = BoardState(2, self.track, self.player_to_racer_map)

        # Set initial positions - both start at same position
        self.board_state.racer_name_to_position_map[RacerName.SUCKERFISH] = 5
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 5

    def test_no_movement_from_same_space_no_power(self):
        """Test that power doesn't activate when no one moves from Suckerfish's space"""
        changes = []

        # Gunk moves from different position (not where Suckerfish is)
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 3
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)
        self.assertEqual(len(new_changes), 1)

    def test_racer_moves_from_suckerfish_space_power_activates(self):
        """Test that power activates when someone moves from Suckerfish's space"""
        # Mock AI to choose to activate power (index 1)
        self.suckerfish.ai = MagicMock()
        self.suckerfish.ai.choose_path.return_value = 1

        changes = []

        # Gunk moves from 5 (same as Suckerfish) to 8
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 5, 8)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 2)

        # Verify Suckerfish moved to the same position as Gunk
        bs_after = deepcopy(self.board_state)
        bs_after.apply_change_list(new_changes)
        suckerfish_final_pos = bs_after.racer_name_to_position_map[RacerName.SUCKERFISH]
        gunk_final_pos = bs_after.racer_name_to_position_map[RacerName.GUNK]

        self.assertEqual(suckerfish_final_pos, gunk_final_pos)
        self.assertIn("moves along with", new_changes[-1].change_messages[0])

    def test_ai_chooses_not_to_activate_power(self):
        """Test that power doesn't activate when AI chooses not to (index 0)"""
        # Mock AI to choose not to activate power (index 0)
        self.suckerfish.ai = MagicMock()
        self.suckerfish.ai.choose_path.return_value = 0

        changes = []

        # Gunk moves from 5 (same as Suckerfish) to 8
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 5, 8)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)  # Power was not activated since AI chose not to use it

        # Verify Suckerfish did NOT move
        suckerfish_moved = False
        for pos_change in new_changes[0].position_changes:
            if pos_change.racer_name == RacerName.SUCKERFISH:
                suckerfish_moved = True

        self.assertFalse(suckerfish_moved, "Suckerfish should not have moved")

    def test_suckerfish_already_moving_updates_position(self):
        """Test that if Suckerfish is already moving, the position is updated"""
        # Mock AI to choose to activate power
        self.suckerfish.ai = MagicMock()
        self.suckerfish.ai.choose_path.return_value = 1

        changes = []

        # Both move: Suckerfish from 5 to 6, Gunk from 5 to 10
        change = ChangeSet()
        change.add_pos_change(RacerName.SUCKERFISH, 5, 6)
        change.add_pos_change(RacerName.GUNK, 5, 10)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)

        # Verify Suckerfish's move was updated to 10 instead of 6
        bs_after = deepcopy(self.board_state)
        bs_after.apply_change_list(new_changes)
        suckerfish_final_pos = bs_after.racer_name_to_position_map[RacerName.SUCKERFISH]

        self.assertEqual(suckerfish_final_pos, 10)

    def test_multiple_racers_leaving_same_space(self):
        """Test power with multiple racers leaving Suckerfish's space"""
        # Create 3-player board state
        player_to_racer_map = {
            Player.P1: RacerName.SUCKERFISH,
            Player.P2: RacerName.GUNK,
            Player.P3: RacerName.MOUTH
        }
        board_state = BoardState(3, self.track, player_to_racer_map)
        board_state.racer_name_to_position_map[RacerName.SUCKERFISH] = 5
        board_state.racer_name_to_position_map[RacerName.GUNK] = 5
        board_state.racer_name_to_position_map[RacerName.MOUTH] = 5

        # Mock AI to always activate power
        self.suckerfish.ai = MagicMock()
        self.suckerfish.ai.choose_path.return_value = 1

        changes = []

        # Both Gunk and Mouth move from position 5
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 5, 8)
        change.add_pos_change(RacerName.MOUTH, 5, 9)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            board_state, changes
        )

        self.assertTrue(power_activated)

        # AI should have been called once
        self.assertEqual(self.suckerfish.ai.choose_path.call_count, 1)

    def test_suckerfish_moves_itself_no_power(self):
        """Test that Suckerfish moving by itself doesn't trigger power"""
        changes = []

        # Only Suckerfish moves
        change = ChangeSet()
        change.add_pos_change(RacerName.SUCKERFISH, 5, 8)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)

    def test_racer_at_different_space_no_power(self):
        """Test that racer at different space moving doesn't trigger power"""
        changes = []

        # Suckerfish at 5, Gunk at 3
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 3

        # Gunk moves from 3 to 7 (different space)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 7)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)

    def test_sequential_changes_with_power(self):
        """Test power across multiple sequential changes"""
        # Mock AI to activate power
        self.suckerfish.ai = MagicMock()
        self.suckerfish.ai.choose_path.return_value = 1

        changes = []

        # First change: Gunk moves from 5 to 8
        change1 = ChangeSet()
        change1.add_pos_change(RacerName.GUNK, 5, 8)
        changes.append(change1)

        # Second change: Suckerfish (now at 8) stays put
        change2 = ChangeSet()
        changes.append(change2)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertTrue(power_activated)
        self.assertEqual(len(new_changes), 3)

    def test_racer_moving_to_suckerfish_no_power(self):
        """Test that racer moving TO Suckerfish's space doesn't trigger power"""
        changes = []

        # Suckerfish at 5, Gunk at 3
        self.board_state.racer_name_to_position_map[RacerName.GUNK] = 3

        # Gunk moves from 3 to 5 (moving TO Suckerfish's space)
        change = ChangeSet()
        change.add_pos_change(RacerName.GUNK, 3, 5)
        changes.append(change)

        new_changes, power_activated = self.suckerfish.get_power_changes(
            self.board_state, changes
        )

        self.assertFalse(power_activated)


if __name__ == '__main__':
    unittest.main()
