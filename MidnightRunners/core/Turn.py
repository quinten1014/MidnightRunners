from enum import Enum

class TurnPhase(Enum):
    PH0_BETWEEN_TURNS = "Phase 0: Between Turns"
    PH1_START_OF_TURN = "Phase 1: Start of Turn"
    PH2_BEFORE_MAIN_MOVE = "Phase 2: Before Main Move"
    PH3_MAIN_MOVE = "Phase 3: Main Move"
    PH4_END_OF_TURN = "Phase 4: End of Turn"

def GetNextTurnPhase(current_phase):
    current_phase_idx = list(TurnPhase).index(current_phase)
    next_phase_idx = (current_phase_idx + 1) % len(TurnPhase)
    next_phase = list(TurnPhase)[next_phase_idx]
    return next_phase