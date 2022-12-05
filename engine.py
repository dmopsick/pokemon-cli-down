# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates
import time

# Start the server
server = Server()

# Init the game state
gameState = GameStates.CLOSED

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

        # Prompt both users to enter their name
        gameState = GameStates.ACCEPT_NAMES
        bothPlayersEnteredName = False

        for clientId, _client in list(server.clientList.items()):
            # Ask the player to enter their name
            namePrompt = "Please enter your name with name command (ex: name Dan): "
            server.sendMessageToClientById(_client.id, namePrompt)

        while bothPlayersEnteredName == False:
            # Wait a quarter of a second before executing the loop once more
            time.sleep(.25)    

            # Check for messages/disconnects
            server.update()

            # Check commands 
            for eventId, event in enumerate(server.getCommands()):
                # Verify that clientId is in the list of clients 
                if server.commandFromValidClient(event.clientId):
                    # print("Flag 11") 
                    # Only processing name commands at this time
                    if event.command == "name":
                        # print("Name command received ")
                        clientIndex = server.getClientIndexById(event.clientId)

                        # print("Flag 12 " + str(clientIndex))

                        # Updating by index will be problematic for running after the first two clients
                        server.clientList[clientIndex].name = event.params
                        print("Client " + str(event.clientId) + " name is now: " + server.clientList[clientIndex].name)
            
            # print("Flag 10")
            # print(server.clientList[0].name)
            # print(server.clientList[1].name)

            if server.clientList[0].name != None and server.clientList[1].name != None:
                print("Both players have entered their name: " + server.clientList[0].name + " and " + server.clientList[1].name)
                bothPlayersEnteredName = True

            pass

        # Set opponent names for the clients
        server.clientList[0].opponentName = server.clientList[1].name
        server.clientList[1].opponentName = server.clientList[0].name
        
        for id, _client in list(server.clientList.items()):
            opponentName = str(_client.opponentName).strip()
            print("Flag 18")
            print(opponentName)

            # Build the opponent found message
            # opponentFoundMessage = "An opponent has been found! {} has challenged you to a battle!".format(_client.opponentName) 
            opponentFoundMessage = "An opponent has been found! {} has challenged you to a battle!".format(opponentName)
            print("Flag 17")
            print(opponentFoundMessage)

            # Send the message telling them an opponent has been found
            server.sendMessageToClientById(_client.id, opponentFoundMessage)

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

            # Listen for commands/disconnects

            pass

        pass
    else:
        print("ERROR: Invalid state provided: " + server.state)
