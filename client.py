# Client that will connect to the server, allowing a player to play the game
class Client:
    
    def __init__(self, id, socket, addr, buffer, lastChecked, name, opponentName):
        self.id = id # Id of this here client
        self.socket = socket # Socket used to communicate with this client
        self.addr = addr # IP Address of the client
        self.buffer = buffer # Holds data sent from the client 
        self.lastChecked = lastChecked # Last time we checked to confirm client still connected
