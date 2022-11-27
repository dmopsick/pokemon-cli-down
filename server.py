import socket
from utils import ServerStates
import utils

 # The server itself that will run the Pokémon battle simulator
class Server(object):

    def __init__(self):
        # Build and start the server
        self.state = ServerStates.CLOSED

        # Init some variables
        self.clientList = {}
        self.nextId = 0 # Next Id to assign to client as they connect

        # Create socket to listen for clients
        self.listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set option on the socket
        self.listeningSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Define a address and port to listen on
        # Telnet standard port 23, this project using different port to avoid potential permission issues
        self.listeningSocket.bind(("0.0.0.0", 1234))
        
        # Set to non blocking mode to not wait for connection
        self.listeningSocket.setblocking(False)

        # Listen for connections
        self.listeningSocket.listen(1)

        # Set the server state to listening
        self.state = ServerStates.LISTEN

        print ("CLIDown server started...")

    def update(self):
        pass

    
