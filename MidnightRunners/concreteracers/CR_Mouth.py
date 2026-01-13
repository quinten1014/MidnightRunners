from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState


class Mouth(AbstractRacer):
    def __init__(self, ask_for_input: bool = False):
        super().__init__(RacerName.MOUTH, ask_for_move_input=ask_for_input)