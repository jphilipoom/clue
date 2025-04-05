import random
from player import Player

# Initialize several game constants
SUSPECTS = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
            'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
WEAPONS = ['Rope', 'Lead Pipe', 'Knife',
           'Wrench', 'Candlestick', 'Revolver']

LOCATIONS = ['Study', 'Hall','Lounge','Kitchen','Conservatory','Dining Room','Ballroom','Billiard Room','Library']

SECRET_PASSAGES = dict({'Study': 'Kitchen',
                        'Lounge': 'Conservatory',
                        'Conservatory': 'Lounge',
                        'Kitchen': 'Study'})

# Each hallway maps to its adjacent rooms
HALLWAYS = dict({'H1': ['Study', 'Hall'],
                 'H2': ['Hall', 'Lounge'],
                 'H6': ['Library', 'Billiard Room'],
                 'H7': ['Billiard Room', 'Dining Room'],
                 'H11': ['Conservatory', 'Ballroom'],
                 'H12': ['Ballroom', 'Kitchen'],
                 'H3': ['Study', 'Library'],
                 'H4': ['Hall', 'Billiard Room'],
                 'H5': ['Lounge', 'Dining Room'],
                 'H8': ['Library', 'Conservatory'],
                 'H9': ['Billiard Room', 'Ballroom'],
                 'H10': ['Dining Room', 'Kitchen']
                 })


# Reverse the dict, so we can also map rooms to adjacent hallways
ROOMS = dict()
for hallway, rms in HALLWAYS.items():
    for room in rms:
        if room in ROOMS:
            ROOMS[room].append(hallway)
        else:
            ROOMS[room] = [hallway]

def distribute_cards(players_list: list[Player]):
    # Determine what the solution is and distribute all other cards to players
    remaining_suspects = SUSPECTS.copy()
    remaining_weapons = WEAPONS.copy()
    remaining_locations = list(ROOMS.keys())

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
            elif len(remaining_weapons) > 0:
                weapon = remaining_weapons.pop()
                player.cards['Weapon'].append(weapon)
            elif len(remaining_locations) > 0:
                location = remaining_locations.pop()
                player.cards['Location'].append(location)

    return solution


def initialize_game(all_players):
    # If Miss Scarlet is in play, she goes first, otherwise by join order
    for player in all_players:
        if player.name == 'Miss Scarlet':
            all_players.remove(player)
            all_players = [player] + all_players

    solution = distribute_cards(all_players)

    return all_players, solution


def generate_valid_moves(all_players , player_locations):
    for current_player in all_players:
        if len(current_player.location) < 4:
            current_player.valid_moves = HALLWAYS[current_player.location]
            for loc in player_locations.values():
                if loc in current_player.valid_moves:
                    current_player.valid_moves.remove(loc)
        else:
            current_player.valid_moves = ROOMS[current_player.location]
            if current_player.location in SECRET_PASSAGES:
                if SECRET_PASSAGES[current_player.location] not in player_locations.values():
                    current_player.valid_moves.append(SECRET_PASSAGES[current_player.location])
    

