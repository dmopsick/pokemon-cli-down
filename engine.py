# This is the game engine that runs the game
# Contains the main loop and state based logic

from server import Server
from utils import ServerStates, GameStates
import time
from player import Player
from move import Move
from pokemon import Pokemon
import random

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

def getNumRemainingPokemon(player):
    count = 0

    for id, pokemon in enumerate(player.pokemonTeam):
        if pokemon.currentHp > 0:
            count += 1

    return count

# Taken from the Generation 5 section of https://bulbapedia.bulbagarden.net/wiki/Damage
# With the spice of the slight random from core series games
def calculateDamage(attackingPokemon, defendingPokemon, move):
    atkForCalculation = 0
    defForCalculation = 0
    modifier = 1
    randomDamageModifier = random.randint(85, 100) / 100

    if move.physical == True:
        atkForCalculation = attackingPokemon.attack
        defForCalculation = defendingPokemon.defense
    # If the attacking move is not physical, use special attack and defense
    else: 
        atkForCalculation = attackingPokemon.spAtk
        defForCalculation = defendingPokemon.spDef

    # Use the formula from Bulbapedia for Pokemon GO for simplicity sake
    # calculatedDamage = (0.5 * move.power * (atkForCalculation / defForCalculation) * modifier * randomDamageModifier) +1
    rawDamage = ( ((2 * attackingPokemon.level / 5) + 2) * move.power * atkForCalculation / defForCalculation + 2) / 50 * randomDamageModifier

    # Round to nearest 1
    calculatedDamage = round(rawDamage)

    return calculatedDamage

def sendMessageToBothPlayers(message):
    for id, player in enumerate(playerList):
        server.sendMessageToClientById(player.clientId, message)

def playerHasRemainingPokemon(player):
    result = False

    # Check for at least one Pokemon in the player's team with remaining HP
    for id, pokemon in enumerate(player.pokemonTeam):
        if pokemon.currentHp > 0:
            result=True

    return result

def executePlayerOneAttack():
    # Announce to both players what move has been used
    sendMessageToBothPlayers("{} uses {}!".format(playerList[0].activePokemon.speciesName, playerList[0].mostRecentMoveCommand.name))
    time.sleep(0.5)

    # Select a random int from 1-100 for accuracy check
    accuracyRandomInt = random.randint(1, 100)
    # Check if the move will hit
    if accuracyRandomInt < playerList[0].mostRecentMoveCommand.accuracy:
        # Calculate damage done by this move
        damage = calculateDamage(playerList[0].activePokemon, playerList[1].activePokemon, playerList[0].mostRecentMoveCommand)

        print("Calculated damage " + str(damage))

        # Apply the damage to the defending pokemon 
        playerList[1].activePokemon.currentHp -= damage 

        # Does the defending Pokemon have any remaining hp?
        if (playerList[1].activePokemon.currentHp > 0):
            sendMessageToBothPlayers("{} received {} points of damage! {} has {} HP remaining".format(playerList[1].activePokemon.speciesName, damage, playerList[1].activePokemon.speciesName, playerList[1].activePokemon.currentHp))
            time.sleep(.5)

        else:
            playerList[1].activePokemon.currentHp = 0
                # Let the players know 
            sendMessageToBothPlayers("{} has been knocked out by the attack!".format(playerList[1].activePokemon.speciesName))
            time.sleep(0.5)

    else:
        # The move missed -- No damage will be done 
        # Announce to both players what move has been used
        sendMessageToBothPlayers("{} avoided the attack!".format(playerList[1].activePokemon.speciesName))
        time.sleep(.5)
    # Decrement the PP of the used move on the attacking active Pokemon
    for id, move in enumerate(playerList[0].activePokemon.moveList):
        if move.id == playerList[0].mostRecentMoveCommand.id:
            # Decerement the PP
            move.currentPp -= 1
            break

    # The command has been issued, set most recent command to null
    playerList[0].mostRecentMoveCommand = None
        
def executePlayerTwoAttack():
    # Announce to both players what move has been used
    sendMessageToBothPlayers("{} uses {}!".format(playerList[1].activePokemon.speciesName, playerList[1].mostRecentMoveCommand.name))
    time.sleep(0.5)

    # Select a random int from 1-100 for accuracy check
    accuracyRandomInt = random.randint(1, 100)
    # Check if the move will hit
    if accuracyRandomInt < playerList[1].mostRecentMoveCommand.accuracy:
        # Calculate damage done by this move
        damage = calculateDamage(playerList[1].activePokemon, playerList[0].activePokemon, playerList[1].mostRecentMoveCommand)

        print("Calculated damage " + str(damage))

        # Apply the damage to the defending pokemon 
        playerList[0].activePokemon.currentHp -= damage 

        # Does the defending Pokemon have any remaining hp?
        if (playerList[0].activePokemon.currentHp > 0):
            sendMessageToBothPlayers("{} received {} points of damage! {} has {} HP remaining".format(playerList[0].activePokemon.speciesName, damage, playerList[0].activePokemon.speciesName, playerList[0].activePokemon.currentHp))
            time.sleep(.5)
        else:
            playerList[0].activePokemon.currentHp = 0
            # Let the players know 
            sendMessageToBothPlayers("{} has been knocked out by the attack!".format(playerList[0].activePokemon.speciesName))
            time.sleep(0.5)
    else:
        # The move missed -- No damage will be done 
        # Announce to both players what move has been used
        sendMessageToBothPlayers("{} avoided the attack!".format(playerList[0].activePokemon.speciesName))
        time.sleep(.5)

    # Decrement the PP of the used move on the attacking active Pokemon
    for id, move in enumerate(playerList[1].activePokemon.moveList):
        if move.id == playerList[1].mostRecentMoveCommand.id:
            # Decerement the PP
            move.currentPp -= 1
            break

    # The command has been issued, set most recent command to null
    playerList[1].mostRecentMoveCommand = None

# Based on limited time and the focus of this project being the networking purposes, for the time being hardcode the Pokemon for the two players
def hardCodeTestValues():
    # Create some moves for the Pokemon to use
    tackle = Move(1, 'Tackle', 'Normal', 35, 35, 40, 100, True)
    scratch = Move(2, 'Scratch', 'Normal', 35, 35, 40, 100, True)
    razorLeaf = Move(3, 'Razor Leaf', 'Grass', 25, 25, 55, 95, True)
    bite = Move(4, 'Bite', 'Dark', 25, 25, 60, 100, True)
    vineWhip = Move(5, 'Vine Whip', 'Grass', 25, 25, 45, 100, True)
    headbutt = Move(6, 'Headbutt', 'Normal', 15, 15, 70, 100,True )

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

        elif len(server.clientList) == 1:
            # print("1 client is connected to the server")
            pass
        elif len(server.clientList) > 2:
            # print("WARNING: There are " + str(len(server.clientList)) + " connections detected.")
            pass
        else:
            # print("No clients are connected to the server")
            pass
        
    elif server.state == ServerStates.ESTAB:
        # The two clients have established their connection to the server

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

                                # Let user know their name has been recorded
                                nameConfirmation = "Your name is confirmed, {}.".format(player.name)
                                server.sendMessageToClientById(event.clientId, nameConfirmation)
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

                    # print("Both players have entered their name: " + playerList[0].name + " and " + playerList[1].name)

            elif gameState == GameStates.BATTLE_START:
                for id, player in enumerate(playerList):
                    # Must strip out any spaces or new lines
                    opponentName = str(player.opponentName).strip()
        
                    # Build the opponent found message
                    opponentFoundMessage = "An opponent has been found! {} has challenged you to a battle!".format(opponentName)
    
                    # Send the message telling them an opponent has been found
                    server.sendMessageToClientById(player.clientId, opponentFoundMessage)
                    
                    time.sleep(.5)    

                    # Load the oppsoing trainer so you can load their active Pokemon
                    opposingTrainer = getPlayerByPlayerId(player.opponentId)

                    # Tell the player what Pokemon their opponent sends out
                    opponentPokemonMessage = "Opponent {} sends out {}.".format(opposingTrainer.name, opposingTrainer.activePokemon.speciesName)
                    server.sendMessageToClientById(player.clientId, opponentPokemonMessage)
                    time.sleep(.5) 

                    # Tell the player what Pokemon they send out
                    trainerPokemonMessage = "You send out {}. Go {}!".format(player.activePokemon.speciesName, player.activePokemon.speciesName)
                    server.sendMessageToClientById(player.clientId, trainerPokemonMessage)

                    time.sleep(.5) 

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

                    for id, move in enumerate(player.activePokemon.moveList):
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
                    # Ensure the command is from a valid client 
                    if server.commandFromValidClient(event.clientId):
                        # Check for a move command issued
                        if event.command == "move":
                            selectedMove = None

                            # Load player associated with this event
                            player = getPlayerByClientId(event.clientId)

                            # Validate the param passed in
                            try:
                                # Get in the passed in number of the move
                                # We add one when displaying the move index, so must do -1 when calculating what move is used
                                moveIndex = int(event.params[0]) -1

                                # Get the move based on provided index
                                selectedMove = player.activePokemon.moveList[moveIndex]

                            except:
                                print("ERROR: Invalid param passed in for move")

                            if selectedMove != None:
                                # Verify that the selected move has pp left
                                if selectedMove.currentPp > 0:
                                    # A valid move has been selected, update player model
                                    player.mostRecentMoveCommand = selectedMove

                                    # Let player know their move was succesfuly registered
                                    moveReceived = "Your move has been submitted. Waiting for your opponent..."
                                    server.sendMessageToClientById(player.clientId, moveReceived)
                                
                                else:
                                    # TODO change this to an elif to make sure that the Pokemon has pp in at least one other move
                                    # If there is no PP in any moves, then the Pokemon can only Struggle
                                    server.sendMessageToClientById(player.clientId, "{} has no PP left, select another move")
      
                            else:
                                # Let player know their move was not registered and let them know proper syntax
                                moveFailedToReceive = "Your move was not submitted. Use syntax `move 1` to select the first move from the list"
                                server.sendMessageToClientById(player.clientId, moveFailedToReceive)

                # Check if both players have given a command this turn
                if playerList[0].mostRecentMoveCommand != None and playerList[1].mostRecentMoveCommand != None:
                    # Both users have made their moves, now to execute them
                    gameState = GameStates.CALCULATE_RESULT
            elif gameState == GameStates.CALCULATE_RESULT:
                # Determine the results of this turn
                # Check which active Pokemon has a higher speed stat, they move first
                if playerList[0].activePokemon.speed > playerList[1].activePokemon.speed:
                    # Player 1 attacks
                    executePlayerOneAttack()

                    # Check if the defending player has any other remaining Pokemon
                    if playerHasRemainingPokemon(playerList[1]) == False:
                        gameState = GameStates.END_BATTLE
                        playerList[0].battleWinner = True
                    else:
                        # Player 2 attacks
                        executePlayerTwoAttack()

                        # Check if the defending player has any other remaining Pokemon
                        if playerHasRemainingPokemon(playerList[0]) == False:
                            gameState = GameStates.END_BATTLE
                            playerList[1].battleWinner = True
                        else:
                            # Reset the loop to accept another round of commands
                            gameState = GameStates.DISPLAY_COMMANDS

                else:
                    # Player 2 has the faster Pokémon so they will go first
                    executePlayerTwoAttack()

                    # Check if the defending player has any other remaining Pokemon
                    if playerHasRemainingPokemon(playerList[0]) == False:
                        gameState = GameStates.END_BATTLE
                        playerList[1].battleWinner = True
                    else:
                        # Player 1 attacks
                        executePlayerOneAttack()

                        # Check if the defending player has any other remaining Pokemon
                        if playerHasRemainingPokemon(playerList[1]) == False:
                            gameState = GameStates.END_BATTLE
                            playerList[0].battleWinner = True
                        else:
                            # Reset the loop to accept another round of commands
                            gameState = GameStates.DISPLAY_COMMANDS

            elif gameState == GameStates.END_BATTLE:
                if playerList[0].battleWinner:
                    # Notify the winner
                    server.sendMessageToClientById(playerList[0].clientId, "{} is out of usable Pokemon...".format(playerList[1].name))
                    time.sleep(0.5)
                    server.sendMessageToClientById(playerList[0].clientId, "You have won the battle {} to {} against {}. Congratulations!".\
                        format(playerList[1].name, getNumRemainingPokemon(playerList[0]), getNumRemainingPokemon(playerList[1]), playerList[1].name))

                    # Notify the loser
                    server.sendMessageToClientById(playerList[1].clientId, "You are out of usable Pokemon...")
                    time.sleep(0.5)
                    server.sendMessageToClientById(playerList[1].clientId, "{} wins the battle {} to {}. Better luck next time.".\
                        format(playerList[0].name, getNumRemainingPokemon(playerList[0]), getNumRemainingPokemon(playerList[1]), playerList[0].name))
                else:
                     # Notify the winner
                    server.sendMessageToClientById(playerList[1].clientId, "{} is out of usable Pokemon...".format(playerList[0].name))
                    time.sleep(0.5)
                    server.sendMessageToClientById(playerList[1].clientId, "You have won the battle {} to {} against {}. Congratulations!".\
                        format(playerList[0].name, getNumRemainingPokemon(playerList[1]), getNumRemainingPokemon(playerList[0]), playerList[0].name))

                    # Notify the loser
                    server.sendMessageToClientById(playerList[0].clientId, "You are out of usable Pokemon...")
                    time.sleep(0.5)
                    server.sendMessageToClientById(playerList[0], "You have won the battle {} to {} against {}. Congratulations!".\
                        format(getNumRemainingPokemon(playerList[1]), getNumRemainingPokemon(playerList[0]), playerList[1].name))

                sendMessageToBothPlayers("Thank you for playing Pokemon CLIDown.")

                # Game is now over, put the game to the closed state
                gameState = GameStates.CLOSED

            elif gameState == GameStates.CLOSED:
                # Empty the player info
                playerList = []

                # Disconnect both clients
                for id, client in list(server.clientList.items()):
                    server.disconnectClient(client.id)
                    client.socket.close()

                # Close the server
                server.state = ServerStates.CLOSED

                # Break out of this nested game loop 
                break
            else:
                print("ERROR: Invalid game state provided: " + str(gameState))

    else:
        print("ERROR: Invalid state provided: " + str(server.state))
