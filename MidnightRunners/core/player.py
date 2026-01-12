from enum import Enum

class Player(Enum):
    P1, P2, P3, P4, P5, P6 = "P1", "P2", "P3", "P4", "P5", "P6"

    def __str__(self):
        return self.value