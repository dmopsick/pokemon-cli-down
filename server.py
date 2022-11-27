import socket
from utils import ServerStates
import utils
import select
import client
import time

# Actual IP to use for the app
# TELNET_IP = "0.0.0.0" # Wildcard to listen on any port possible
TELNET_IP = "127.0.0.1" # Local IP address for testing locally on one machine
TELNET_PORT = 1234

TELNET_NEW_LINE = "\n\r"

 # The server itself that will run the Pokémon battle simulator
class Server(object):

    def __init__(self):
        # Build and start the server
        self.state = ServerStates.CLOSED

        # Init some variables
        self.clientList = {}
        self.nextClientId = 0 # Next Id to assign to client as they connect

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

    def update(self):
        pass

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
            createdClient = client.Client(acceptedSocket, addr, '', time.time())

            # Add the object to the server's list of clients
            self.clientList[self.nextClientId] = createdClient
            
            # Log the connection made
            print("New connection established with Client Id " + str(self.nextClientId) + " at address " + str(addr[0]) + ". At this time the client is Player " + str(len(self.clientList)) + ".")

            # Write the message to tell the player that they have connected to the server successfully 
            newUserMessage = "You have succesfully connected to Pokemon CLI Down! You are player Id: " + str(self.nextClientId)

            # Give a message to the one client telling them they are connected but must wait for a second client to connect
            self.sendMessageToClientById(self.nextClientId, newUserMessage)

            # Check if the player we have added above is the first player, if so let them know we are waiting for another player to connect
            if len(self.clientList) == 1:
                waitingMessage = "Waiting for a second Trainer to connect to begin the battle."

                self.sendMessageToClientById(self.nextClientId, waitingMessage)
            
            # Increment the nextClientId in preperation of the next client
            self.nextClientId += 1

        else:
            # There is not data to be read at this time at the socket we are listening on
            print("NO DATA AVAILABLE TO READ")
            return
        pass

    def sendMessageToClientById(self, clientId, message):
        # Add new line to end of the message for printing neater
        message = message + TELNET_NEW_LINE

        try:
            # Load the client we are going to send the message to
            clientToSendMessageTo = self.clientList[clientId]

            clientToSendMessageTo.socket.sendall(bytearray(message, "latin1"))

            print("Message sent to Client Id: " + str(clientId))
        except KeyError:
            print("ERROR: Attempting to send message to client that does not exist with Id: " + str(clientId))
        except socket.error:
            # Disconnect the socket if something goes wrong
            print("ERROR: Unable to send to socket associated with client Id: " + str(clientId))
            pass 

    
