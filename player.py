class Player:

    def __init__(self, id, clientId, name):
        self.id = id
        self.clientId = clientId
        self.name = name
        self.opponentName = None
        self.opponentId = None
        self.pokemonTeam = None
        self.activePokemon = None
        self.mostRecentMoveCommand = None
