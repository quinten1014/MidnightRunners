from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState


class Gunk(AbstractRacer):
    def __init__(self):
        self.name = RacerName.GUNK