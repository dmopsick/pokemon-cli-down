# Client that will connect to the server, allowing a player to play the game
class Client:
    
    def __init__(self, socket, addr, buffer, lastChecked):
        self.socket = socket # Socket used to communicate with this client
        self.addr = addr # IP Address of the client
        self.bufffer = buffer # Holds data sent from the client 
        self.lastChecked = lastChecked # Last time we checked to confirm client still connected
