# Event class to hold data about an event on the server
class Event:
    
    # Event Ids used for processing different types of events
    _EVENT_NEW_PLAYER = 1
    _EVENT_PLAYER_LEFT = 2
    _EVENT_COMMAND = 3

    def __init__(self, eventType, clientId, command, params):
        self.eventType = eventType # Thet type of event, ex: new player, disconnect, command
        self.clientId = clientId
        self.command = command
        self.params = params
        