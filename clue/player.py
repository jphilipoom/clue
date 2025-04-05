
class Player:
    def __init__(self, name: str, location,cards,seen_cards,skip_turns,current_turn,valid_moves):
        self.name = name
        self.location = location
        self.cards = cards or dict({'Weapon': [], 'Suspect': [], 'Location': []})
        self.seen_cards = seen_cards or dict({'Weapon': [], 'Suspect': [], 'Location': []})
        self.skip_turns = skip_turns
        self.current_turn = current_turn
        self.valid_moves = valid_moves
        return
    
    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "cards": self.cards,
            "seen_cards": self.seen_cards,
            "skip_turns": self.skip_turns,
            "current_turn": self.current_turn,
            "valid_moves": self.valid_moves
        }

    def __repr__(self):
        return self.name

    def check_accusation(self, weapon: str, suspect: str, location: str):
        # Check if another player's accusation contrasts with a card you have
        found_cards = []
        if weapon in self.cards['Weapon']:
            found_cards.append(weapon)
        if suspect in self.cards['Suspect']:
            found_cards.append(suspect)
        if location in self.cards['Location']:
            found_cards.append(location)

        return found_cards