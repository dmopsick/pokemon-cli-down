# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates
import time

# Start the server
server = Server()

while True:
    # Wait a quarter of a second before executing the loop once more
    time.sleep(.25)    

    # Determine what to do based on the state of the server
    if server.state == ServerStates.CLOSED:
        # The server is closed, let's set it to listening
        server.state = ServerStates.LISTEN
    elif server.state == ServerStates.LISTEN:
        # Need to listen until there are 2 clients connected 
        server.checkNewConnections()

        # Check to see if there are now two clients
        if len(server.clientList) == 2:
            # If so the connections have been established and the battle can begin
            server.state = ServerStates.ESTAB

            # Let both of the users know that a connection with two clients has been established
             
        elif len(server.clientList) == 1:
            print("1 client is connected to the server")
            pass
        elif len(server.clientList) > 2:
            print("WARNING: There are " + str(len(server.clientList)) + " connections detected.")
            pass
        else:
            print("No clients are connected to the server")
            pass
        
    elif server.state == ServerStates.ESTAB:
        # The two clients have established their connection to the server
        print("Time for the game loop to begin")

        # Let each player know that an opponent has been found and the battle will begin
        for _client in server.clientList:
            # Build the opponent found message
            opponentFoundMessage = "An opponent has been found! The battle will begin now..."

            # Send the message telling them an opponent has been found
            server.sendMessageToClientById(_client, opponentFoundMessage)

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

