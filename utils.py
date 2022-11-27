from enum import Enum

# Hold the states that the engine will use to determine  
class ServerStates(Enum):
    CLOSED, LISTEN,\
    ESTAB, FIN = range(1, 5)

class GameStates(Enum):
    BATTLE_START, ACCEPT_COMMANDS, \
    CALCULATE_RESULT, DISPLAY_RESULT, \
    END_BATTLE, CLOSED= range(1, 7)

