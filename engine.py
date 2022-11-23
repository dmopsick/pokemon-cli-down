# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates

# Start the server
server = Server()

while True:
    # Perhaps pause the loop 
    
    # Determine what to do based on the state of the server
    if server.state == S

