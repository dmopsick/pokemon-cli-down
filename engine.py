# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates

# Start the server
server = Server()

while True:
    # Perhaps pause the loop 
    
    # Determine what to do based on the state of the server
    if server.state == ServerStates.CLOSED:
        # The server is closed, let's set it to listening
        server.state = ServerStates.LISTEN
    elif server.state == ServerStates.LISTEN:
        # Need to listen until there are 2 clients connected 

        # Connect to the client

        # Check if there is now two clients connected

        # If there is only one client connected, give a message to the client telling him to please wait

        # When there are two clients connected, the connection is established and the game begins

        pass
    elif server.state == ServerStates.ESTAB:
        # The two clients have established their connection to the server

        # Game loop
        while True:
            # Display information the users about battle

            # Accept commands for the turn of the battle

            # Display waiting message to client after they submit commands

            # Once both clients submit their commands, calculate what occurs on the turn

            # Return information to the user

            # Check for an end condition

            # If not end condition, let the loop continue

            # End condition met, time to end the battle
            # Display end info
            # PERHAPS IF I HAVE TIME ALLOW BOTH USERS TO DECIDE TO BATTLE AGAIN
            # Once battle is over time to display final message and end connction

            pass

        pass
    else:
        print("ERROR: Invalid state provided: " + server.state)

