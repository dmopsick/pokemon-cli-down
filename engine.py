# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates
import time
from player import Player
from move import Move
from pokemon import Pokemon

# Start the server
server = Server()

# Hold the player info
playerList = []

# Init the game state
gameState = GameStates.CLOSED

def getPlayerByClientId(clientId):
    foundPlayer = None

    for id, player in enumerate(playerList):
        if player.clientId == clientId:
            foundPlayer = player
    return foundPlayer

def getPlayerByPlayerId(playerId):
    foundPlayer = None

    for id, player in enumerate(playerList):
        if playerId == player.id:
            foundPlayer = player

    return foundPlayer

# Based on limited time and the focus of this project being the networking purposes, for the time being hardcode the Pokemon for the two players
def hardCodeTestValues():
    # Create some moves for the Pokemon to use
    tackle = Move(1, 'Tackle', 'Normal', 35, 35, 40, 100)
    scratch = Move(2, 'Scratch', 'Normal', 35, 35, 40, 100)
    razorLeaf = Move(3, 'Razor Leaf', 'Grass', 25, 25, 55, 95)
    bite = Move(4, 'Bite', 'Dark', 25, 25, 60, 100)
    vineWhip = Move(5, 'Vine Whip', 'Grass', 25, 25, 45, 100)
    headbutt = Move(6, 'Headbutt', 'Normal', 15, 15, 70, 100)

    # Set the move list for Treeko
    treekoMoveList = []
    treekoMoveList.append(scratch)
    treekoMoveList.append(razorLeaf)
    treekoMoveList.append(vineWhip)

    # Set the type list for Treeko
    treekoTypeList = []
    treekoTypeList.append('Grass')

    # Set the move list for Bidoof
    bidoofMoveList = []
    bidoofMoveList.append(tackle)
    bidoofMoveList.append(bite)
    bidoofMoveList.append(headbutt)

    # Set the type list for Bidoof
    bidoofTypeList = []
    bidoofTypeList.append('Normal')

    # Player 1 will get Treeko, my favorite Pokemon
    treeko = Pokemon(1, 'Treeko', None, 5, 20, 9, 9, 12, 11, 13, treekoMoveList, treekoTypeList, 20)

    # Player 2 will get Bidoof 
    bidoof = Pokemon(2, 'Bidoof', None, 5, 21, 10, 8, 8, 10, 10, bidoofMoveList, bidoofTypeList, 21)

    # Build Player 1 team
    player1Team = []
    player1Team.append(treeko)

    # Build Player 2 team
    player2Team = []
    player2Team.append(bidoof)

    # Assign Player 1 their Pokemon team
    playerList[0].pokemonTeam = player1Team

    # Assign Player 2 their Pokemon team
    playerList[1].pokemonTeam = player2Team
    

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
            # Create new player record 
            newPlayer = Player(id, event.clientId, None)

            # Add to the map of players
            playerList.append(newPlayer)

            print("Flag 20 adding new player Id " + str(newPlayer.id) + " with client Id " + str(newPlayer.clientId))

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

            # Accept names of the players. 
            # At this point in the future could also allow players to select which Pokemon to use
            if gameState == GameStates.ACCEPT_NAMES:
                # Check commands 
                for eventId, event in enumerate(server.getCommands()):
                    # Verify that clientId is in the list of clients 
                    if server.commandFromValidClient(event.clientId):
                        # Only processing name commands at this time
                        if event.command == "name":
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

                    # For testing purposes for the final project, hard code both players Pokemon teams
                    hardCodeTestValues()
                    
                    # Set player 1 and player 2 active Pokemon
                    playerList[0].activePokemon = playerList[0].pokemonTeam[0]
                    playerList[1].activePokemon = playerList[1].pokemonTeam[0]

                    print("Both players have entered their name: " + playerList[0].name + " and " + playerList[1].name)

            elif gameState == GameStates.BATTLE_START:
                for id, player in enumerate(playerList):
                    # Must strip out any spaces or new lines
                    opponentName = str(player.opponentName).strip()
        
                    # Build the opponent found message
                    opponentFoundMessage = "An opponent has been found! {} has challenged you to a battle!".format(opponentName)
                    print(opponentFoundMessage)

                    # Send the message telling them an opponent has been found
                    server.sendMessageToClientById(player.clientId, opponentFoundMessage)

                    # Load the oppsoing trainer so you can load their active Pokemon
                    opposingTrainer = getPlayerByPlayerId(player.opponentId)

                    # Tell the player what Pokemon their opponent sends out
                    opponentPokemonMessage = "Opponent {} sends out {}.".format(opposingTrainer.name, opposingTrainer.activePokemon.speciesName)
                    server.sendMessageToClientById(player.clientId, opponentPokemonMessage)

                    # Tell the player what Pokemon they send out
                    trainerPokemonMessage = "You send out {}. Go {}!".format(player.activePokemon.speciesName, player.activePokemon.speciesName)
                    server.sendMessageToClientById(player.clientId, trainerPokemonMessage)

                    # Change state
                    gameState = GameStates.DISPLAY_COMMANDS
                pass
            elif gameState == GameStates.DISPLAY_COMMANDS:
                # Let the user know the current status of their Pokemon and the opposing Pokemon
                for id, player in enumerate(playerList):
                    # Load the oppsoing trainer so you can load their active Pokemon
                    opposingTrainer = getPlayerByPlayerId(player.opponentId)

                    # Tell the player the current status, HP of their opponent's Pokemon
                    opponentPokemonStatusMessage = "{0}'s Level {1} {2} has {3} / {4} HP remaining.".format(opposingTrainer.name, str(opposingTrainer.activePokemon.level), opposingTrainer.activePokemon.speciesName, \
                        opposingTrainer.activePokemon.currentHp, str(opposingTrainer.activePokemon.maxHp))
                    server.sendMessageToClientById(player.clientId, opponentPokemonStatusMessage)

                    # Tell the player the current status, HP of their Pokemon
                    playerPokemonStatusMessage = "Your Level {} {} has {} / {} HP remaining.".format(player.activePokemon.level, player.activePokemon.speciesName, \
                        player.activePokemon.currentHp, player.activePokemon.maxHp)
                    server.sendMessageToClientById(player.clientId, playerPokemonStatusMessage)

                    # Let the user know what moves are available to them at this time
                    playerMovesOptionsMessage = "Select a move to use. This is done by using the `move` command and the number of the move you wish to use. Ex: `move 1`\n"

                    for id, move in enumerate(player.activePokemon.movesList):
                        # Show the move Id as + one because humans start counting at + 1
                        # Make sure to do minus 1 when reading the commands
                        playerMovesOptionsMessage += "{}. {} ({} type) - {}/{} pp\n".format((id + 1), move.name, move.type, move.currentPp, move.maxPp)
                    server.sendMessageToClientById(player.clientId, playerMovesOptionsMessage)

                # We have displayed the info, now we must wait and get user input for the moves
                gameState = GameStates.ACCEPT_COMMANDS
                pass
            elif gameState == GameStates.ACCEPT_COMMANDS:
                # Accept commands from the players for this turn 
                for eventId, event in enumerate(server.getCommands()):

                    pass

                # Check if both players have given a command this turn
                if playerList[0].mostRecentMoveCommand != None and playerList[1].mostRecentMoveCommand != None:
                    # Let both users know that moves have been made


                    gameState = GameStates.CALCULATE_RESULT
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
