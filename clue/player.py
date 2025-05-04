class Player:
    def __init__(self, name: str = "", location=None, cards=None, seen_cards=None, skip_turns=0,current_turn=False, valid_moves=None
    ):
        self.name = name
        self.location = location
        self.cards = cards if cards is not None else {'Weapon': [], 'Suspect': [], 'Location': []}
        self.seen_cards = seen_cards if seen_cards is not None else {'Weapon': [], 'Suspect': [], 'Location': []}
        self.skip_turns = skip_turns
        self.current_turn = current_turn
        self.valid_moves = valid_moves if valid_moves is not None else []

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
        found_cards = []
        if weapon in self.cards['Weapon']:
            found_cards.append(weapon)
        if suspect in self.cards['Suspect']:
            found_cards.append(suspect)
        if location in self.cards['Location']:
            found_cards.append(location)
        return found_cards
