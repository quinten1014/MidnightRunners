from MidnightRunners.concreteracers.ConcreteRacerNames import RacerName
from MidnightRunners.core import AbstractRacer, BoardState


class Mouth(AbstractRacer):
    def __init__(self):
        self.name = RacerName.MOUTH