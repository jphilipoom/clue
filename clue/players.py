# Initialize several game constants
SUSPECTS = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
            'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
WEAPONS = ['Rope', 'Lead Pipe', 'Knife',
           'Wrench', 'Candlestick', 'Revolver']

SECRET_PASSAGES = dict({'Study': 'Kitchen',
                        'Lounge': 'Conservatory',
                        'Conservatory': 'Lounge',
                        'Kitchen': 'Study'})
# H indicates horizontal hallways, V indicates vertical
# Each hallway maps to its adjacent rooms
HALLWAYS = dict({'H0': ['Study', 'Hall'],
                 'H1': ['Hall', 'Lounge'],
                 'H2': ['Library', 'Billiard Room'],
                 'H3': ['Billiard Room', 'Dining Room'],
                 'H4': ['Conservatory', 'Ballroom'],
                 'H5': ['Ballroom', 'Kitchen'],
                 'V0': ['Study', 'Library'],
                 'V1': ['Hall', 'Billiard Room'],
                 'V2': ['Lounge', 'Dining Room'],
                 'V3': ['Library', 'Conservatory'],
                 'V4': ['Billiard Room', 'Ballroom'],
                 'V5': ['Dining Room', 'Kitchen']
                 })
# Reverse the dict, so we can also map rooms to adjacent hallways
ROOMS = dict()
for hallway, rms in HALLWAYS.items():
    for room in rms:
        if room in ROOMS:
            ROOMS[room].append(hallway)
        else:
            ROOMS[room] = [hallway]


class Player:
    def __init__(self, player_name: str):
        if player_name not in SUSPECTS:
            raise ValueError(f'{player_name} is not a valid character.'
                             f'The only valid characters are: {SUSPECTS}')
        self.name = player_name
        self.location = None
        self.cards = dict({'Weapon': [], 'Suspect': [], 'Location': []})
        self.seen_cards = dict({'Weapon': [], 'Suspect': [], 'Location': []})
        self.skip_turns = False
        return

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

    def viewed_card(self, card: str):
        # When another player disproves your accusation, take note
        if card in WEAPONS:
            self.seen_cards['Weapon'].append(card)
        elif card in SUSPECTS:
            self.seen_cards['Suspect'].append(card)
        elif card in ROOMS:
            self.seen_cards['Location'].append(card)
        else:
            raise ValueError(f'{card} is an invalid card.')

        return


class NonPlayer:
    def __init__(self, npc_name: str):
        if npc_name not in SUSPECTS:
            raise ValueError(f'{npc_name} is not a valid character.'
                             f'The only valid characters are: {SUSPECTS}')
        self.name = npc_name
        self.location = None
        return


class Location:
    """
    This class covers both hallways and rooms and allows us to keep track of
    who is in each room and where you can go from there
    """
    def __init__(self, name):
        self.name = name
        if name in ROOMS:
            self.type = 'Room'
            self.valid_next_steps = ROOMS[name]
            if name in SECRET_PASSAGES:
                self.valid_next_steps.append(SECRET_PASSAGES[name])
        else:
            self.type = 'Hallway'
            self.valid_next_steps = HALLWAYS[name]
        self.suspects = []

        return

    def add_suspect(self, suspect):
        self.suspects.append(suspect)
        return

    def remove_suspect(self, suspect):
        if suspect not in self.suspects:
            raise ValueError(f'Player {suspect} is not in {self.name} and cannot be removed')
        else:
            self.suspects.remove(suspect)
        return
