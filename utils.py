from enum import Enum

# Hold the states that the engine will use to determine  
class ServerStates(Enum):
    CLOSED, LISTEN,\
    ESTAB, FIN = range(1, 5)

class GameStates(Enum):
    BATTLE_START, DISPLAY_COMMANDS, \
    ACCEPT_COMMANDS, CALCULATE_RESULT, \
    END_BATTLE, CLOSED, ACCEPT_NAMES = range(1, 8)
