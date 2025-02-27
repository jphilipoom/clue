import random

SUSPECTS = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
            'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
WEAPONS = ['Rope', 'Lead Pipe', 'Knife',
           'Wrench', 'Candlestick', 'Revolver']
LOCATIONS = ['Study', 'Hall', 'Lounge', 'Library', 'Billiard Room',
             'Dining Room', 'Conservatory', 'Ballroom', 'Kitchen']
STARTING_LOCS = dict({'Colonel Mustard': [4, 3],
                      'Miss Scarlet': [3, 4],
                      'Professor Plum': [0, 3],
                      'Mr. Green': [1, 0],
                      'Mrs. White': [3, 0],
                      'Mrs. Peacock': [0, 1]})


class Player:
    def __init__(self, player_name: str):
        if player_name not in SUSPECTS:
            raise ValueError(f'{player_name} is not a valid character.'
                             f'The only valid characters are: {SUSPECTS}')
        self.name = player_name
        self.location = STARTING_LOCS[player_name]
        self.cards = dict({'Weapon': [], 'Suspect': [], 'Location': []})
        self.seen_cards = dict({'Weapon': [], 'Suspect': [], 'Location': []})

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
        elif card in LOCATIONS:
            self.seen_cards['Location'].append(card)
        else:
            raise ValueError(f'{card} is an invalid card.')

        return


def distribute_cards(players_list: list[Player]):
    # Determine what the solution is and distribute all other cards to players
    remaining_suspects = SUSPECTS.copy()
    remaining_weapons = WEAPONS.copy()
    remaining_locations = LOCATIONS.copy()

    random.shuffle(remaining_suspects)
    random.shuffle(remaining_weapons)
    random.shuffle(remaining_locations)

    suspect = remaining_suspects.pop()
    weapon = remaining_weapons.pop()
    location = remaining_locations.pop()
    solution = dict({'Suspect': suspect, 'Weapon': weapon, 'Location': location})

    while len(remaining_locations) > 0:
        for player in players_list:
            if len(remaining_suspects) > 0:
                suspect = remaining_suspects.pop()
                player.cards['Suspect'].append(suspect)
            if len(remaining_weapons) > 0:
                weapon = remaining_weapons.pop()
                player.cards['Weapon'].append(weapon)
            location = remaining_locations.pop()
            player.cards['Location'].append(location)

    return solution
