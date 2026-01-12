from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState


class Romantic(AbstractRacer):
    def __init__(self):
        self.name = RacerName.ROMANTIC