"""
BoardState class for managing state of track and racers during a race.
"""

from enum import Enum

class TrackVersion(Enum):
    MILD = "Mild Miles"
    WILD = "Wild Wilds"

# Represent start space (0) up to and including finish space (30)
FIXED_TRACK_LENGTH = 31

# Define special properties that spaces on the track can have
class SpecialSpaceProperties(Enum):
    START = "Start"
    FINISH = "Finish"
    ARROW_PLUS_1 = "Arrow +1"
    ARROW_PLUS_2 = "Arrow +2"
    ARROW_PLUS_3 = "Arrow +3"
    ARROW_MINUS_1 = "Arrow -1"
    ARROW_MINUS_2 = "Arrow -2"
    ARROW_MINUS_4 = "Arrow -4"
    STAR1 = "Star 1"
    TRIP = "Trip"

class Track:
    def __init__(self, track_version: TrackVersion):
        self.track_version = track_version
        self.space_properties = [[] for _ in range(FIXED_TRACK_LENGTH)]
        self.space_properties[0].append(SpecialSpaceProperties.START)
        self.space_properties[30].append(SpecialSpaceProperties.FINISH)

        if track_version == TrackVersion.WILD:
            self.space_properties[1].append(SpecialSpaceProperties.STAR1)
            self.space_properties[5].append(SpecialSpaceProperties.TRIP)
            self.space_properties[7].append(SpecialSpaceProperties.ARROW_PLUS_3)
            self.space_properties[11].append(SpecialSpaceProperties.ARROW_PLUS_1)
            self.space_properties[13].append(SpecialSpaceProperties.STAR1)
            self.space_properties[16].append(SpecialSpaceProperties.ARROW_MINUS_4)
            self.space_properties[17].append(SpecialSpaceProperties.TRIP)
            self.space_properties[23].append(SpecialSpaceProperties.ARROW_PLUS_2)
            self.space_properties[24].append(SpecialSpaceProperties.ARROW_MINUS_2)
            self.space_properties[26].append(SpecialSpaceProperties.TRIP)