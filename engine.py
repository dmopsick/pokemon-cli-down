# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates
import time
from player import Player

# Start the server
server = Server()

# Hold the player info
playerList = []

# Init the game state
gameState = GameStates.CLOSED

def getPlayerByClientId(clientId):
    foundPlayer = None

    for playerId, player in enumerate(playerList):
        if player.clientId == clientId:
            foundPlayer = player
    return foundPlayer

while True:
    # Wait a quarter of a second before executing the loop once more
    time.sleep(.25)    

    # Determine what to do based on the state of the server
    if server.state == ServerStates.CLOSED:
        # The server is closed, let's set it to listening
        server.state = ServerStates.LISTEN
    elif server.state == ServerStates.LISTEN:
        # Need to listen until there are 2 clients connected 
        server.update()

        for id, event in enumerate(server.getNewPlayers()):
            print("Flag 1")

            # Create new player record 
            newPlayer = Player(id, event.clientId, None, None, None)

            # Add to the map of players
            playerList.append(newPlayer)

            print("FLAG 20 adding new player Id " + str(newPlayer.id) + " with client Id " + str(newPlayer.clientId))

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

        while True:
            # Wait a quarter of a second before executing the loop once more
            time.sleep(.25)    

            # Check for messages/disconnects
            server.update()

            if gameState == GameStates.ACCEPT_NAMES:
                # Check commands 
                for eventId, event in enumerate(server.getCommands()):
                    # Verify that clientId is in the list of clients 
                    if server.commandFromValidClient(event.clientId):
                        # Only processing name commands at this time
                        if event.command == "name":
                            # print("Name command received ")
                            clientIndex = server.getClientIndexById(event.clientId)

                            player = getPlayerByClientId(event.clientId)

                            print("Looking for player with clientId " + str(event.clientId))
                            print("Player Id: " + str(player.id) + " is Client Id " + str(player.clientId))

                            if player != None:
                                # Updating by index will be problematic for running after the first two clients
                                player.name = str(event.params).strip()
                                print("Client " + str(event.clientId) + " name is now: " + player.name)
                            else:
                                print("ERROR: Cannot find player for Client Id " + event.clientId)

                if playerList[0].name != None and playerList[1].name != None:
                    # Set opponent names for the clients
                    playerList[0].opponentName = playerList[1].name
                    playerList[0].opponentId = playerList[1].id
                    playerList[1].opponentName = playerList[0].name
                    playerList[1].opponentId = playerList[0].id

                    gameState = GameStates.BATTLE_START

                    print("Both players have entered their name: " + playerList[0].name + " and " + playerList[1].name)

            elif gameState == GameStates.BATTLE_START:
                for id, player in enumerate(playerList):
                    # Must strip out any spaces or new lines
                    opponentName = str(player.opponentName).strip()
                    print("Flag 18")
                    print(opponentName)

                    # Build the opponent found message
                    opponentFoundMessage = "An opponent has been found! {} has challenged you to a battle!".format(opponentName)
                    print(opponentFoundMessage)

                    # Send the message telling them an opponent has been found
                    server.sendMessageToClientById(player.clientId, opponentFoundMessage)

                    # Tell the player what Pokémon they send out

                    # Tell the player what Pokémon their opponent sends out

                    # Change state
                    gameState = GameStates.ACCEPT_COMMANDS
                pass
            elif gameState == GameStates.ACCEPT_COMMANDS:
                # Accept commands from the players for this turn 
                pass
            elif gameState == GameStates.CALCULATE_RESULT:
                # Determine the results of this turn
                pass
            elif gameState == GameStates.DISPLAY_RESULT:
                # Display the Results of the turn to the user

                # Determine if the battle will continue
                # Battle will continue Set the state to ACCEPT_COMMANDS

                # Battle has met an end condition, set to END_BATTLE
                pass
            elif gameState == GameStates.END_BATTLE:
                pass
            else:
                print("ERROR: Invalid game state provided: " + str(gameState))

    else:
        print("ERROR: Invalid state provided: " + str(server.state))
