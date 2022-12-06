from enum import Enum

# Hold the states that the engine will use to determine  
class ServerStates(Enum):
    CLOSED, LISTEN,\
    ESTAB, END = range(1, 5)

class GameStates(Enum):
    BATTLE_START, ACCEPT_NAMES, \
    DISPLAY_COMMANDS, \
    ACCEPT_COMMANDS, CALCULATE_RESULT, \
    END_BATTLE, CLOSED, = range(1, 8)
