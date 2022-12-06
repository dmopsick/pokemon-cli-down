import socket
from utils import ServerStates
from event import Event
import select
import client
import time

# Actual IP to use for the app
TELNET_IP = "0.0.0.0" # Wildcard to listen on any port possible
# TELNET_IP = "127.0.0.1" # Local IP address for testing locally on one machine
TELNET_PORT = 1234

TELNET_NEW_LINE = "\n\r"
TELNET_MESSAGE_MAX_LENGTH = 4096 # Do need long messages here

 # The server itself that will run the Pokémon battle simulator
class Server(object):

    # Read state values to allow for processing of client data via telnet as laid out in the example linked on GitHub | http://pcmicro.com/netfoss/telnet.html
    # Taken directly from GitHub MUD project reference | https://github.com/Frimkron/mud-pi/blob/a152f20516cde03411db4015211e3d3b64c8d883/mudserver.py
    _READ_STATE_NORMAL = 1
    _READ_STATE_COMMAND = 2
    _READ_STATE_SUBNEG = 3
    _TN_INTERPRET_AS_COMMAND = 255
    _TN_ARE_YOU_THERE = 246
    _TN_WILL = 251
    _TN_WONT = 252
    _TN_DO = 253
    _TN_DONT = 254
    _TN_SUBNEGOTIATION_START = 250
    _TN_SUBNEGOTIATION_END = 240

    def __init__(self):
        # Build and start the server
        self.state = ServerStates.CLOSED

        # Init some variables
        self.clientList = {}
        self.nextClientId = 0 # Next Id to assign to client as they connect
        self.eventList = []
        self.newEventList = [] # How does this get processed?

        # Create socket to listen for clients
        self.listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set option on the socket
        self.listeningSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Define a address and port to listen on
        # Telnet standard port 23, this project using different port to avoid potential permission issues
        self.listeningSocket.bind((TELNET_IP, TELNET_PORT))
        
        # Set to non blocking mode to not wait for connection
        self.listeningSocket.setblocking(False)

        # Listen for connections
        self.listeningSocket.listen(1)

        # Set the server state to listening
        self.state = ServerStates.LISTEN

        print ("CLIDown server started...")
        print("Listening at " + TELNET_IP + ":" + str(TELNET_PORT))

        if TELNET_IP == "0.0.0.0":
            print("Check the server IP at https://whatismyipaddress.com/")

    def update(self):
        # Check for new connected clients
        self.checkNewConnections()

        # Check if one or more clients disconnected
        
        # Check for any new messages from the clients to be processed as commands
        self.receiveMessagesFromClients()

        # Replace the existing events list with the new events taken in this cycle
        # No longer need the old event list
        self.eventList = list(self.newEventList)

        # Reset the new event list
        self.newEventList = []

    def getCommands(self):
        commandList = []

        # Iterate through the list of events 
        for id, event in enumerate(self.eventList):
            print(event.command + " " + event.params)
            # If the event is command, add it to the command list
            if event.eventType == Event._EVENT_COMMAND:
                commandList.append(event)

        return commandList

    # Check for a new client connecting to the game server
    def checkNewConnections(self):
        # Check 3 lists of sockets, only concerned about the first one, the reading sockets
        rlist, wlist, xlist = select.select([self.listeningSocket], [], [], 0)
        
        # Check if the listening socket is in the readable list
        if self.listeningSocket in rlist:
            # The defined listening socket contains data to be read
            # Accept the new socket
            acceptedSocket, addr = self.listeningSocket.accept()

            # Set non-blocking mode on the socket so the send and recv will occur instantly
            acceptedSocket.setblocking(False)

            # Construct new client object
            createdClient = client.Client(self.nextClientId, acceptedSocket, addr, '', time.time(), None, None)

            # Add the object to the server's list of clients
            self.clientList[self.nextClientId] = createdClient

            # Increment the nextClientId in preperation of the next client
            self.nextClientId += 1

            # Log the connection made
            print("New connection established with Client Id " + str(createdClient.id) + " at address " + str(addr[0]) + ". At this time the client is Player " + str(len(self.clientList)) + ".")

            # Write the message to tell the player that they have connected to the server successfully 
            newUserMessage = "You have succesfully connected to Pokemon CLIDown! You are player Id: " + str(createdClient.id)

            # Create a new player event
            newPlayerEvent = Event(Event._EVENT_NEW_PLAYER, createdClient.id, None, None)

            # Add the event we just made to the list of new events
            self.newEventList.append(newPlayerEvent)

            # Give a message to the one client telling them they are connected but must wait for a second client to connect
            self.sendMessageToClientById(createdClient.id, newUserMessage)

            # Check if the player we have added above is the first player, if so let them know we are waiting for another player to connect
            if len(self.clientList) == 1:
                waitingMessage = "Waiting for a second Trainer to connect to begin the battle."

                self.sendMessageToClientById(createdClient.id, waitingMessage)
        else:
            # There is not data to be read at this time at the socket we are listening on
            # print("NO DATA AVAILABLE TO READ")
            return

    def disconnectClient(self, clientId):
        # Remove the client from the client map
        del(self.clientList[clientId])

        # Do we need to do something here? 
        # In the example they add a player left to new events list... but how is that handled and where

    def sendMessageToClientById(self, clientId, message):
        # Add new line to end of the message for printing neater
        message = message + TELNET_NEW_LINE

        # print("Flag 16")
        # print(message)

        clientIndex = self.getClientIndexById(clientId)

        try:
            # Load the client we are going to send the message to
            clientToSendMessageTo = self.clientList[clientIndex]

            clientToSendMessageTo.socket.sendall(bytearray(message, "latin1"))

            print("Message sent to Client Id: " + str(clientId))
        except KeyError:
            print("ERROR: Attempting to send message to client that does not exist with Id: " + str(clientId))
        except socket.error:
            # Disconnect the socket if something goes wrong
            print("ERROR: Unable to send to socket associated with client Id: " + str(clientId))
            self.disconnectClient(clientId) 

    def receiveMessagesFromClients(self):
        # Iterate through each of the clients currently connected
        for id, _client in list(self.clientList.items()):
            # _client = self.clientList[clientId]

            # print("Flag 2")
            # print(_client.id)

            # Get the list of data to read 
            rlist, wrlist, xlist = select.select([_client.socket], [], [], 0)

            # Check if this client's associated socket appears in the read list of data
            if _client.socket in rlist:
                try:
                    # The client's socket appears, there is new data from this client
                    rawData = _client.socket.recv(TELNET_MESSAGE_MAX_LENGTH).decode("latin1")

                    # Process the received message
                    processedMessage = self.processReceivedData(_client, rawData)

                    if processedMessage != None:
                        # Separate the command and the parameter(s) out
                        # First string is command, all the rest would be parameters

                        # Check if there are any params
                        if len(processedMessage.split()) > 1:
                            # Command and args provided
                            command, params = (processedMessage.split(" ", 1) + ["", ""])[:2]

                            # Create new event object
                            event = Event(Event._EVENT_COMMAND, _client.id, command.lower(), params)
                        else:
                            # No args provided, just a one word command
                            command = processedMessage.strip()
                            # Create new event object
                            event = Event(Event._EVENT_COMMAND, _client.id, command.lower(), "")

                        # Add the command/params to list of new events
                        self.newEventList.append(event)

                except socket.error:
                    self.disconnectClient(_client.id)

            # If it does not appear that means there is no data from this client

    # Taken directly from GitHub MUD project reference | https://github.com/Frimkron/mud-pi/blob/a152f20516cde03411db4015211e3d3b64c8d883/mudserver.py
    def processReceivedData(self, client, data):
        # Init the return value of the processed message
        processedMessage = None

        readState = self._READ_STATE_NORMAL

        # Iterate through the received data one character at a time
        for char in data:
            # Handle the read state
            if readState == self._READ_STATE_NORMAL:
                # Check if the character is a special command
                # This command means 'interpret as command'
                if ord(char) == self._TN_INTERPRET_AS_COMMAND:
                    readState = self._READ_STATE_COMMAND
                # Check for new line character... that will be end of message
                elif char == "\n":
                    processedMessage = client.buffer
                    
                    # Message has been processed... now clear the client obj buffer
                    client.buffer = ""
                # Check for back spaces -- The GitHub example says some Telnet clients send character right away so must account for backspace
                elif char == "\x08":
                    # Remove the last character from the buffer
                    client.buffer = client.buffer[:-1]
                else:
                    # No special command at this time, add character to buffer
                    client.buffer += char
            # Handle the command state
            elif readState == self._READ_STATE_COMMAND:
                if ord(char) == self._TN_SUBNEGOTIATION_START:
                    readState = self._READ_STATE_SUBNEG
                
                elif ord(char) in (self._TN_WILL, self._TN_WONT, self._TN_DO, self._TN_DONT):
                    readState = self._READ_STATE_COMMAND
                
                else:
                    readState = self._READ_STATE_NORMAL

            #Handle the Subnegotiation state
            elif readState == self._READ_STATE_SUBNEG:
                if ord(char) == self._TN_SUBNEGOTIATION_END:
                    readState = self._READ_STATE_NORMAL

        return processedMessage


    def getNewPlayers(self):
        newPlayerEventList = []
        for id, event in enumerate(self.eventList):
            if event.eventType == Event._EVENT_NEW_PLAYER:
                newPlayerEventList.append(event)
            
        return newPlayerEventList

    # Helper functions

    def getListOfClientIds(self):
        clientIdList = []

        for id, client in list(self.clientList.items()):
            # Make sure to cast Ids as ints for equality
            clientIdList.append(int(client.id))
        
        return clientIdList

    def commandFromValidClient(self, clientId):
        validCommand = False
        
        for id, client in list(self.clientList.items()):
            if clientId == client.id:
                validCommand = True

        return validCommand

    def getClientIndexById(self, clientId):
        index = -1

        for id, client in list(self.clientList.items()):
            if clientId == client.id:
                index = id

        return index 
