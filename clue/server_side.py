import random
import string

from clue.players import (
    Player,
    NonPlayer,
    Location,
    SUSPECTS,
    HALLWAYS,
    ROOMS,
    WEAPONS,
    )


STARTING_LOCS = dict({'Colonel Mustard': 'V2',
                      'Miss Scarlet': 'H1',
                      'Professor Plum': 'V0',
                      'Mr. Green': 'H4',
                      'Mrs. White': 'H5',
                      'Mrs. Peacock': 'V3'})


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


def initialize_game():
    print(f'Which of the following suspects would you like to play as?\n{SUSPECTS}')
    host_player = input('Please type in your preferred character: ')
    while host_player not in SUSPECTS:
        print(f'Error: {host_player} is not a valid character.')
        print(f'Which of the following suspects would you like to play as?\n{SUSPECTS}')
        host_player = input('Please type in your preferred character: ')
    available_suspects = SUSPECTS.copy()
    available_suspects.remove(host_player)
    all_players = [Player(host_player)]

    game_code = random.choices(string.ascii_uppercase, k=3) + random.choices(
        string.digits, k=3)
    print('Your game code is ' + ''.join(game_code) + '! Share this code with friends for '
          'them to join.\n')

    ready_to_start = False
    while not ready_to_start:
        # TODO: websocket magic to receive suspect selection from clients
        print(f'Currently available characters are: {available_suspects}')
        new_player = input('Which would you like to play as? ')
        while new_player not in available_suspects:
            print(f'Error: {new_player} is not a valid character name.')
            print(f'Currently available characters are: {available_suspects}')
            new_player = input('Which would you like to play as? ')

        all_players.append(Player(new_player))
        available_suspects.remove(new_player)

        print(f'There are currently {6 - len(available_suspects)} players.')
        if len(available_suspects) > 3:
            print('Waiting for at least 3 players to join...')
        elif len(available_suspects) == 0:
            print('Six players joined! Starting game...')
            ready_to_start = True
        else:
            user_ready = input('If you are ready to start the game, type "y".'
                               ' To continue waiting for players, hit Enter.')
            if user_ready == 'y':
                ready_to_start = True

    # If Miss Scarlet is in play, she goes first, otherwise by join order
    for player in all_players:
        if player.name == 'Miss Scarlet':
            all_players.remove(player)
            all_players = [player] + all_players

    all_non_players = []
    for character in available_suspects:
        all_non_players.append(NonPlayer(character))

    solution = distribute_cards(all_players)
    # TODO: websocket magic to notify players of the cards dealt to them
    for player in all_players:
        print(f'{player.name}, your cards are: {player.cards}')

    all_locations = set()
    for location in list(ROOMS.keys()) + list(HALLWAYS.keys()):
        next_loc = Location(location)
        for suspect in all_players + all_non_players:
            if STARTING_LOCS[suspect.name] == location:
                next_loc.add_suspect(suspect)
                suspect.location = next_loc
        all_locations.add(next_loc)

    return all_players, all_non_players, all_locations, solution


def move_active_player(active_player: Player, all_locations: list[Location]):
    active_player_location = active_player.location
    valid_moves = active_player_location.valid_next_steps

    # If the location is an occupied hallway, you cannot move there
    for location in all_locations:
        if location.type == 'Hallway' and location.name in valid_moves and len(location.suspects) > 0:
            valid_moves.remove(location.name)

    # TODO: convert to websocket magic
    print(f'{active_player.name}, your available moves are {valid_moves}.')
    next_location = input('Where would you like to move to? ')
    while next_location not in valid_moves:
        print(f'Error: {next_location} is not a valid location to move to.')
        print(f'{active_player.name}, your available moves are {valid_moves}.')
        next_location = input('Where would you like to move to? ')

    print(f'{active_player.name} has moved to {next_location}!')

    for location in all_locations:
        if location.name == next_location:
            location.add_suspect(active_player)
            active_player.location = location
            break

    return active_player, all_locations


def make_suggestion(active_player: Player, all_players: list[Player],
                    all_non_players: list[NonPlayer]):
    active_player_location = active_player.location

    print(f'{active_player.name}, your cards are: {active_player.cards}\n')
    print(f'You have see the following cards of other players: {active_player.seen_cards}\n')
    print(f'You will be making a suggestion in {active_player_location.name}')
    print(f'The list of all weapons is {WEAPONS}')
    weapon = input('Type the name of the weapon you would like to suggest was used: ')
    while weapon not in WEAPONS:
        print(f'Error: {weapon} is not a valid weapon.')
        print(f'The list of all weapons is {WEAPONS}')
        weapon = input('Type the name of the weapon you would like to suggest was used: ')

    print(f'The list of all suspects is {SUSPECTS}')
    suspect = input('Type the name of the suspect you would like to suggest was the murderer: ')
    while suspect not in SUSPECTS:
        print(f'Error: {suspect} is not a valid suspect.')
        print(f'The list of all suspects is {SUSPECTS}')
        suspect = input('Type the name of the suspect you would like to suggest was the murderer: ')
    for character in all_players + all_non_players:
        if character.name == suspect:
            print(f'{suspect} has been moved to {active_player_location.name}!')
            character.location = active_player_location
            active_player_location.add_suspect(character)

    active_player_index = all_players.index(active_player)
    num_players = len(all_players)
    disproven = False
    for idx in range(1, num_players):
        questioned_player = all_players[(active_player_index + idx) % num_players]
        cards_to_disprove = questioned_player.check_accusation(weapon,
                                                               suspect,
                                                               active_player_location.name)

        if len(cards_to_disprove) == 0:
            print(f'{questioned_player.name} has no cards to disprove this suggestion')
        elif len(cards_to_disprove) == 1:
            # TODO: websocket magic so this only gets displayed to active and questioned players
            print(f'{questioned_player.name} is disproving this suggestion with {cards_to_disprove[0]}')
            active_player.viewed_card(cards_to_disprove[0])
            disproven = True
        else:
            # TODO: websocket magic to display prompt only to questioned player
            #       and result only to active player
            print(f'{questioned_player.name}, which card would you like to use to disprove'
                  f'this suggestion?\n {cards_to_disprove}')
            card = input('Type the name of the card you\'d like to pick: ')
            while card not in cards_to_disprove:
                print(f'Error: {card} is not a valid card.')
                print(f'{questioned_player.name}, which card would you like to use to disprove'
                      f'this suggestion?\n {cards_to_disprove}')
                card = input('Type the name of the card you\'d like to pick: ')
            print(f'{active_player.name}, {questioned_player.name} is disproving'
                  f'your suggestion with {card}.')
            active_player.viewed_card(card)
            disproven = True

        if disproven:
            break
    return disproven, active_player, all_players, all_non_players


def make_accusation(active_player: Player, solution):
    print(f'{active_player.name}, your cards are: {active_player.cards}\n')
    print(f'You have see the following cards of other players: {active_player.seen_cards}\n')

    print(f'The list of all rooms is: {ROOMS.keys()}')
    room = input('Type the name of the room you would like to accuse the murder '
                 'took place in: ')
    while room not in ROOMS.keys():
        print(f'Error: {room} is not a valid room.')
        print(f'The list of all rooms is: {ROOMS.keys()}')
        room = input('Type the name of the room you would like to accuse the murder '
                     'took place in: ')
    print(f'The list of all weapons is: {WEAPONS}')
    weapon = input('Type the name of the weapon you would like to accuse was used: ')
    while weapon not in WEAPONS:
        print(f'Error: {weapon} is not a valid weapon.')
        print(f'The list of all weapons is: {WEAPONS}')
        weapon = input('Type the name of the weapon you would like to accuse was used: ')

    print(f'The list of all suspects is {SUSPECTS}')
    suspect = input('Type the name of the suspect you would like to accuse was the murderer: ')
    while suspect not in SUSPECTS:
        print(f'Error: {suspect} is not a valid suspect.')
        print(f'The list of all suspects is {SUSPECTS}')
        suspect = input('Type the name of the suspect you would like to accuse was the murderer: ')

    print(f'{active_player.name} is accusing {suspect} of murdering Mr. Boddy'
          f'with the {weapon} in the {room}!')
    if solution['Suspect'] == suspect and solution['Weapon'] == weapon and solution['Location'] == room:
        print(f'Success! {active_player.name} has won the game!')
        return True, active_player
    else:
        print(f'Oh no! {active_player.name} was wrong and will skip all future turns.')
        active_player.skip_turns = True
        return False, active_player


def turn(active_player: Player, all_players: list[Player],
         all_non_players: list[NonPlayer], all_locations: list[Location],
         solution):
    solved = False

    # TODO: convert to websocket
    action = 'm'
    if active_player.location.type == 'Room':
        print(f'{active_player.name}, you are located in {active_player.location.name}.')
        action = input('Do you want to move or stay put and make a suggestion? Type \'m\' or \'s\'')
        while action not in ['m', 's']:
            print(f'Error: {action} is not a valid response.')
            action = input('Do you want to move or make a suggestion? Type \'m\' or \'s\'')

    if action == 'm':
        active_player, all_locations = move_active_player(active_player, all_locations)
        if active_player.location.type == 'Room':
            action = input('Would you like to make a suggestion? Type \'s\' if so,'
                           ' or Enter to end turn.')

    if action == 's':
        disproven, active_player, all_players, all_non_players = make_suggestion(active_player,
                                                                                 all_players,
                                                                                 all_non_players)

        if not disproven:
            print('No one was able to disprove the suggestion!')

    action = input(f'{active_player.name}, would you like to make an accusation? If so, type \'a\','
                   f' otherwise hit Enter.')

    if action == 'a':
        action = input('Are you sure? If your accusation is wrong you will lose. Type \'y\''
                       'to proceed, \'n\' to cancel.')
        if action == 'y':
            solved, active_player = make_accusation(active_player, solution)

    return all_players, all_non_players, all_locations, solved
