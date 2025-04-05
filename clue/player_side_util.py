import asyncio
from msgs.messages import SuggestionResponse
from server_side_util import (
    Player,
    SUSPECTS,
    ROOMS,
    WEAPONS,
    LOCATIONS
    )


async def make_suggestion(MY_PLAYER: Player):
    active_player_location = MY_PLAYER.location

    print(f'{MY_PLAYER.name}, your cards are: {MY_PLAYER.cards}\n')
    print(f'You have see the following cards of other players: {MY_PLAYER.seen_cards}\n')
    print(f'You will be making a suggestion in {active_player_location}')
    print(f'The list of all weapons is {WEAPONS}')
    weapon = await asyncio.to_thread(input,'Type the name of the weapon you would like to suggest was used: ')
    while weapon not in WEAPONS:
        print(f'Error: {weapon} is not a valid weapon.')
        print(f'The list of all weapons is {WEAPONS}')
        weapon = await asyncio.to_thread(input,'Type the name of the weapon you would like to suggest was used: ')

    print(f'The list of all suspects is {SUSPECTS}')
    suspect = await asyncio.to_thread(input,'Type the name of the suspect you would like to suggest was the murderer: ')
    while suspect not in SUSPECTS:
        print(f'Error: {suspect} is not a valid suspect.')
        print(f'The list of all suspects is {SUSPECTS}')
        suspect = await asyncio.to_thread(input,'Type the name of the suspect you would like to suggest was the murderer: ')
    return weapon, suspect

async def make_accusation(active_player: Player):
    print(f'{active_player.name}, your cards are: {active_player.cards}\n')
    print(f'You have see the following cards of other players: {active_player.seen_cards}\n')

    print(f'The list of all rooms is: {ROOMS.keys()}')
    room = await asyncio.to_thread(input,'Type the name of the room you would like to accuse the murder '
                 'took place in: ')
    while room not in ROOMS.keys():
        print(f'Error: {room} is not a valid room.')
        print(f'The list of all rooms is: {ROOMS.keys()}')
        room = await asyncio.to_thread(input,'Type the name of the room you would like to accuse the murder '
                     'took place in: ')
    print(f'The list of all weapons is: {WEAPONS}')
    weapon = await asyncio.to_thread(input,'Type the name of the weapon you would like to accuse was used: ')
    while weapon not in WEAPONS:
        print(f'Error: {weapon} is not a valid weapon.')
        print(f'The list of all weapons is: {WEAPONS}')
        weapon = await asyncio.to_thread(input,'Type the name of the weapon you would like to accuse was used: ')

    print(f'The list of all suspects is {SUSPECTS}')
    suspect = await asyncio.to_thread(input,'Type the name of the suspect you would like to accuse was the murderer: ')
    while suspect not in SUSPECTS:
        print(f'Error: {suspect} is not a valid suspect.')
        print(f'The list of all suspects is {SUSPECTS}')
        suspect = await asyncio.to_thread(input,'Type the name of the suspect you would like to accuse was the murderer: ')
    return room, weapon, suspect
    

async def generate_suggestion_response(suggestion: SuggestionResponse, curr_player: Player):
    gen_sugg_resp = SuggestionResponse(suggestion.player, "","","",curr_player.name)

    found_cards = curr_player.check_accusation(suggestion.weapon,suggestion.suspect,suggestion.location)
    if len(found_cards) > 0:
        selected_card = await asyncio.to_thread(input,f"Select one of your matching cards {found_cards} (enter card value - ex. Wrench): ")
        if selected_card in WEAPONS:
            gen_sugg_resp.weapon = selected_card
        elif selected_card in LOCATIONS:
            gen_sugg_resp.location = selected_card
        elif selected_card in SUSPECTS:
            gen_sugg_resp.suspect = selected_card
    else:
        print("You have no matching cards")
    return gen_sugg_resp