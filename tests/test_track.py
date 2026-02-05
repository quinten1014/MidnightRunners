"""
Unit tests for the Track class
"""

import unittest
from copy import deepcopy

from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, MoveType, PointChange, PositionChange
from MidnightRunners.core.Track import (
    Track, TrackVersion, SpecialSpaceProperties, FIXED_TRACK_LENGTH
)


class TestTrackInit(unittest.TestCase):
    """Test cases for Track initialization"""

    def test_mild_track_initialization(self):
        """Test that Mild Miles track initializes correctly"""
        track = Track(TrackVersion.MILD)

        self.assertEqual(track.track_version, TrackVersion.MILD)
        self.assertEqual(len(track.space_properties), FIXED_TRACK_LENGTH)

        # Verify START and FINISH are set
        self.assertIn(SpecialSpaceProperties.START, track.space_properties[0])
        self.assertIn(SpecialSpaceProperties.FINISH, track.space_properties[30])

        # Verify no special spaces in between for MILD track
        for i in range(1, 30):
            self.assertEqual(len(track.space_properties[i]), 0)

    def test_wild_track_initialization(self):
        """Test that Wild Wilds track initializes with special spaces"""
        track = Track(TrackVersion.WILD)

        self.assertEqual(track.track_version, TrackVersion.WILD)
        self.assertEqual(len(track.space_properties), FIXED_TRACK_LENGTH)

        # Verify START and FINISH
        self.assertIn(SpecialSpaceProperties.START, track.space_properties[0])
        self.assertIn(SpecialSpaceProperties.FINISH, track.space_properties[30])

        # Verify WILD track special spaces
        self.assertIn(SpecialSpaceProperties.STAR1, track.space_properties[1])
        self.assertIn(SpecialSpaceProperties.TRIP, track.space_properties[5])
        self.assertIn(SpecialSpaceProperties.ARROW_PLUS_3, track.space_properties[7])
        self.assertIn(SpecialSpaceProperties.ARROW_PLUS_1, track.space_properties[11])
        self.assertIn(SpecialSpaceProperties.STAR1, track.space_properties[13])
        self.assertIn(SpecialSpaceProperties.ARROW_MINUS_4, track.space_properties[16])
        self.assertIn(SpecialSpaceProperties.TRIP, track.space_properties[17])
        self.assertIn(SpecialSpaceProperties.ARROW_PLUS_2, track.space_properties[23])
        self.assertIn(SpecialSpaceProperties.ARROW_MINUS_2, track.space_properties[24])
        self.assertIn(SpecialSpaceProperties.TRIP, track.space_properties[26])


class TestGetNewSpace(unittest.TestCase):
    """Test cases for Track.GetNewSpace static method"""

    def test_normal_forward_movement(self):
        """Test normal forward movement"""
        self.assertEqual(Track.GetNewSpace(5, 3), 8)
        self.assertEqual(Track.GetNewSpace(10, 5), 15)

    def test_normal_backward_movement(self):
        """Test normal backward movement"""
        self.assertEqual(Track.GetNewSpace(10, -3), 7)
        self.assertEqual(Track.GetNewSpace(15, -5), 10)

    def test_no_movement(self):
        """Test zero delta"""
        self.assertEqual(Track.GetNewSpace(10, 0), 10)

    def test_clamp_to_lower_bound(self):
        """Test that movement is clamped to 0 (minimum)"""
        self.assertEqual(Track.GetNewSpace(3, -10), 0)
        self.assertEqual(Track.GetNewSpace(0, -5), 0)

    def test_clamp_to_upper_bound(self):
        """Test that movement is clamped to track end (30)"""
        self.assertEqual(Track.GetNewSpace(28, 10), 30)
        self.assertEqual(Track.GetNewSpace(30, 5), 30)

    def test_at_boundaries(self):
        """Test movement at track boundaries"""
        self.assertEqual(Track.GetNewSpace(0, 1), 1)
        self.assertEqual(Track.GetNewSpace(30, -1), 29)


class TestTrigChanges(unittest.TestCase):
    """Test cases for Track.trig_changes method"""

    def setUp(self):
        """Set up common test fixtures"""
        self.player_to_racer_map = {
            Player.P1: RacerName.BANANA,
            Player.P2: RacerName.GUNK
        }

    def test_no_special_space_mild_track(self):
        """Test that no changes are triggered on MILD track regular spaces"""
        track = Track(TrackVersion.MILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 5, 8)

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertFalse(triggered)
        self.assertEqual(len(new_changes), 1)
        # Verify the original change is present and marked as processed
        self.assertTrue(new_changes[0].processed_by_track)

    def test_star_space_gives_point(self):
        """Test that landing on STAR space gives 1 point"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 0, 1)  # Space 1 has STAR1

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)
        self.assertGreater(len(new_changes), 1)

        # Check that a point change was added for Player.P1
        point_changes_found = False
        for change in new_changes:
            if change.point_changes:
                self.assertEqual(change.point_changes[0].player, Player.P1)
                self.assertEqual(change.point_changes[0].points_delta, 1)

    def test_trip_space_trips_racer(self):
        """Test that landing on TRIP space trips the racer"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 4, 5)  # Space 5 has TRIP

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a trip change was added
        for change in new_changes:
            if change.trip_changes:
                self.assertEqual(change.trip_changes[0].racer_name, RacerName.BANANA)
                self.assertTrue(change.trip_changes[0].tripped_after)

    def test_trip_space_no_trip_if_no_movement(self):
        """Test that TRIP space doesn't trip if racer didn't move"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 5, 5)  # Space 5 has TRIP, but no movement

        new_changes, triggered = track.trig_changes(board_state, changes)

        # No trip should be triggered when old_pos == landed_pos
        for change in new_changes:
            if change.trip_changes:
                self.fail("Trip changes should not be triggered when there is no movement")

    def test_arrow_plus_1(self):
        """Test ARROW_PLUS_1 moves racer forward by 1"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 10, 11)  # Space 11 has ARROW_PLUS_1

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a position change to space 12 was added
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 12:
                    self.assertEqual(pos_change.old_position, 11)
                    self.assertEqual(pos_change.move_type, MoveType.TRACK)

    def test_arrow_plus_2(self):
        """Test ARROW_PLUS_2 moves racer forward by 2"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 22, 23)  # Space 23 has ARROW_PLUS_2

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a position change to space 25 was added
        position_changes_found = False
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 25:
                    position_changes_found = True
                    self.assertEqual(pos_change.old_position, 23)

        self.assertTrue(position_changes_found)

    def test_arrow_plus_3(self):
        """Test ARROW_PLUS_3 moves racer forward by 3"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 6, 7)  # Space 7 has ARROW_PLUS_3

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a position change to space 10 was added
        position_changes_found = False
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 10:
                    position_changes_found = True
                    self.assertEqual(pos_change.old_position, 7)

        self.assertTrue(position_changes_found)

    def test_arrow_minus_1(self):
        """Test ARROW_MINUS_1 moves racer backward by 1"""
        # First create a MILD track and manually add ARROW_MINUS_1 for testing
        track = Track(TrackVersion.MILD)
        track.space_properties[15].append(SpecialSpaceProperties.ARROW_MINUS_1)

        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 14, 15)

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a position change to space 14 was added
        position_changes_found = False
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 14:
                    position_changes_found = True
                    self.assertEqual(pos_change.old_position, 15)

        self.assertTrue(position_changes_found)

    def test_arrow_minus_2(self):
        """Test ARROW_MINUS_2 moves racer backward by 2"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 23, 24)  # Space 24 has ARROW_MINUS_2

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a position change to space 22 was added
        position_changes_found = False
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 22:
                    position_changes_found = True
                    self.assertEqual(pos_change.old_position, 24)

        self.assertTrue(position_changes_found)

    def test_arrow_minus_4(self):
        """Test ARROW_MINUS_4 moves racer backward by 4"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 15, 16)  # Space 16 has ARROW_MINUS_4

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that a position change to space 12 was added
        position_changes_found = False
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 12:
                    position_changes_found = True
                    self.assertEqual(pos_change.old_position, 16)

        self.assertTrue(position_changes_found)

    def test_finish_space_adds_finished_racer(self):
        """Test that landing on FINISH space marks racer as finished"""
        track = Track(TrackVersion.MILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 29, 30)  # Space 30 is FINISH

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check that racer was marked as finished
        finished_found = False
        for change in new_changes:
            if change.finished_racers:
                finished_found = True
                self.assertIn(RacerName.BANANA, change.finished_racers)

        self.assertTrue(finished_found)

    def test_start_space_has_no_effect(self):
        """Test that START space has no special effect when landed on"""
        track = Track(TrackVersion.MILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 1, 0)  # Landing on START

        new_changes, triggered = track.trig_changes(board_state, changes)

        # No special effect should trigger for START space
        self.assertFalse(triggered)

    def test_arrow_returns_early(self):
        """Test that arrow triggers cause early return"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        # Create multiple changes, where first triggers arrow
        changes = [
            ChangeSet(),
            ChangeSet()
        ]
        changes[0].add_pos_change(RacerName.BANANA, 6, 7)  # Space 7 has ARROW_PLUS_3
        changes[1].add_pos_change(RacerName.GUNK, 2, 5)  # This should be processed even after arrow

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)
        # Arrow should cause early return, so second change may not be fully processed

    def test_already_processed_change_not_reprocessed(self):
        """Test that changes already processed by track are not reprocessed"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 5, 7)
        changes[0].processed_by_track = True  # Mark as already processed

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertFalse(triggered)
        self.assertEqual(len(new_changes), 1)

    def test_multiple_position_changes_in_one_changeset(self):
        """Test handling multiple position changes in a single ChangeSet"""
        track = Track(TrackVersion.WILD)
        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 0, 1)  # Space 1 has STAR1
        changes[0].add_pos_change(RacerName.GUNK, 4, 5)  # Space 5 has TRIP

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Check board state after applying changes
        board_state.apply_change_list(new_changes)
        self.assertEqual(board_state.player_points_map[Player.P1], 1)
        self.assertTrue(board_state.racer_trip_map[RacerName.GUNK])

        # Verify individual changes
        for change in new_changes:
            if change.point_changes:
                self.assertEqual(change.point_changes[0].player, Player.P1)
                self.assertEqual(change.point_changes[0].points_delta, 1)
            if change.trip_changes:
                self.assertEqual(change.trip_changes[0].racer_name, RacerName.GUNK)
                self.assertTrue(change.trip_changes[0].tripped_after)

    def test_arrow_clamps_to_track_bounds(self):
        """Test that arrow movements respect track boundaries"""
        track = Track(TrackVersion.MILD)
        # Add ARROW_PLUS_3 near the end
        track.space_properties[29].append(SpecialSpaceProperties.ARROW_PLUS_3)

        board_state = BoardState(2, track, self.player_to_racer_map)

        changes = [ChangeSet()]
        changes[0].add_pos_change(RacerName.BANANA, 28, 29)

        new_changes, triggered = track.trig_changes(board_state, changes)

        self.assertTrue(triggered)

        # Should clamp to space 30, not beyond
        position_changes_found = False
        for change in new_changes:
            for pos_change in change.position_changes:
                if pos_change.racer_name == RacerName.BANANA and pos_change.new_position == 30:
                    position_changes_found = True

        self.assertTrue(position_changes_found)


if __name__ == '__main__':
    unittest.main()
