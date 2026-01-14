""" Unique name for each racer card in the game."""
from enum import Enum

class RacerName(Enum):
    BANANA           = "Banana"
    ROMANTIC         = "Romantic"
    GUNK             = "Gunk"
    MOUTH            = "Mouth"
    EGG              = "Egg"
    ROCKET_SCIENTIST = "Rocket Scientist"

RacerNameToColorMap = {
    RacerName.BANANA:           (255, 255, 0),    # Yellow
    RacerName.ROMANTIC:         (255, 105, 180),  # Hot Pink
    RacerName.GUNK:             (0, 255, 0),      # Green
    RacerName.MOUTH:            (255, 0, 0),      # Red
    RacerName.EGG:              (255, 255, 255),  # White
    RacerName.ROCKET_SCIENTIST: (0, 0, 255),      # Blue
}