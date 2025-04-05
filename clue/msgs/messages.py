class Suggestion:
    def __init__(self, player, location , weapon, suspect):
        self.player = player
        self.location = location 
        self.weapon = weapon
        self.suspect = suspect
    
    def to_dict(self):
        return {
            "player": self.player,
            "location": self.location,
            "weapon": self.weapon,
            "suspect" : self.suspect
        }

class SuggestionResponse:
    def __init__(self, player, location , weapon, suspect, respondent):
        self.player = player
        self.location = location 
        self.weapon = weapon
        self.suspect = suspect
        self.respondent = respondent
    
    def to_dict(self):
        return {
            "player": self.player,
            "location": self.location,
            "weapon": self.weapon,
            "suspect" : self.suspect,
            "respondent": self.respondent
        }
class PublicSuggestionResponse:
    def __init__(self, responding_player, showed_card):
        self.responding_player = responding_player
        self.showed_card = showed_card
    
    def to_dict(self):
        return {
            "responding_player": self.responding_player,
            "showed_card": self.showed_card
        }
    
class ChoosePlayer:
    def __init__(self, selected_player: str, players: list[str], start):
        self.selected_player = selected_player 
        self.players = players
        self.start = start
    
    def to_dict(self):
        return {
            "selected_player": self.selected_player,
            "players": self.players,
            "start" : self.start
        }

class Accusation:
    def __init__(self, player,location , weapon, suspect, correct):
        self.player = player
        self.location = location 
        self.weapon = weapon
        self.suspect = suspect
        self.correct = correct
    
    def to_dict(self):
        return {
            "player": self.player,
            "location": self.location,
            "weapon": self.weapon,
            "suspect" : self.suspect,
            "correct": self.correct
        }
    
