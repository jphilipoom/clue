import asyncio
import websockets
import json
from msgs.messages import (
    ChoosePlayer,
    Accusation,
    Suggestion,
    SuggestionResponse,
    PublicSuggestionResponse,
)
from player import Player
from server_side_util import initialize_game, generate_valid_moves

connected_players = {}
all_players = []

available_suspects = [
    "Colonel Mustard",
    "Miss Scarlet",
    "Professor Plum",
    "Mr. Green",
    "Mrs. White",
    "Mrs. Peacock",
]

solution = {}

LOCATION_TO_PLAYER = {
    "Study": "",
    "H1": "",
    "Hall": "",
    "H2": "Miss Scarlet",
    "Lounge": "",
    "H3": "Professor Plum",
    "H4": "",
    "H5": "Colonel Mustard",
    "Library": "",
    "H6": "",
    "Billiard Room": "",
    "H7": "",
    "Dining Room": "",
    "H8": "Mrs. Peacock",
    "H9": "",
    "H10": "",
    "Conservatory": "",
    "H11": "Mr. Green",
    "Ballroom": "",
    "H12": "Mrs. White",
    "Kitchen": "",
    "": "",
}

PLAYER_TO_LOCATION = {
    "Miss Scarlet": "H2",
    "Professor Plum": "H3",
    "Colonel Mustard": "H5",
    "Mrs. Peacock": "H8",
    "Mrs. White": "H12",
    "Mr. Green": "H11",
}

CURRENT_TURN_IDX = 0
START_GAME = False
CURRENT_SUGGESTION = None


def get_next_turn_idx(start_idx):
    print("determining next turn idx: start: " + str(start_idx))
    next_idx = (start_idx + 1) % len(all_players)
    original_idx = start_idx

    while all_players[next_idx].skip_turns:
        next_idx = (next_idx + 1) % len(all_players)
        if next_idx == original_idx:
            return None  # No one left to play
    print("result: " + str(next_idx))
    return next_idx


async def handler(websocket):
    global START_GAME, CURRENT_TURN_IDX, CURRENT_SUGGESTION, all_players, solution

    try:
        choose_player = ChoosePlayer("", available_suspects, False)
        await websocket.send(
            json.dumps({"type": "CHOOSE_PLAYER", "data": choose_player.to_dict()})
        )

        while True:
            data = await websocket.recv()
            message = json.loads(data)
            message_type = message["type"]

            print("message of type: " + str(message_type))

            if message_type == "CHOOSE_PLAYER" and not START_GAME:
                choose_player = ChoosePlayer(**message["data"])
                connected_players[choose_player.selected_player] = websocket
                available_suspects.remove(choose_player.selected_player)

                player = Player(
                    choose_player.selected_player, "", None, None, False, False, []
                )
                player.location = PLAYER_TO_LOCATION[player.name]
                all_players.append(player)

                print(f"New player connected: {choose_player.selected_player}")

                if choose_player.start:
                    START_GAME = True
                    all_players, solution = initialize_game(all_players)
                    print(f"The solution is: {solution}")
                    all_players[CURRENT_TURN_IDX].current_turn = True
                    generate_valid_moves(all_players, PLAYER_TO_LOCATION)
                    await send_out_board_display("")
                    await send_out_player_information("")

            elif message_type == "PLAYER":
                print("Received player message")
                player = Player(**message["data"])
                all_players[CURRENT_TURN_IDX] = player
                prev_loc = PLAYER_TO_LOCATION[player.name]
                PLAYER_TO_LOCATION[player.name] = player.location
                LOCATION_TO_PLAYER[player.location] = player.name
                LOCATION_TO_PLAYER[prev_loc] = ""
                generate_valid_moves(all_players, PLAYER_TO_LOCATION)
                await send_out_board_display(player.name)

            elif message_type == "SUGGESTION":
                print("Received suggestion")
                suggestion = Suggestion(**message["data"])
                prev_loc = PLAYER_TO_LOCATION[suggestion.suspect]
                PLAYER_TO_LOCATION[suggestion.suspect] = suggestion.location
                LOCATION_TO_PLAYER[suggestion.location] = suggestion.suspect
                LOCATION_TO_PLAYER[prev_loc] = ""

                CURRENT_SUGGESTION = suggestion

                for player in all_players:
                    if player.name == suggestion.suspect:
                        player.location = suggestion.location
                        break

                await send_out_suggestion(suggestion.player, suggestion)
                await send_out_board_display("")

                next_player = all_players[(CURRENT_TURN_IDX + 1) % len(all_players)]
                await connected_players[next_player.name].send(
                    json.dumps(
                        {
                            "type": "SUGGESTION_RESPONSE",
                            "data": SuggestionResponse(
                                suggestion.player,
                                suggestion.location,
                                suggestion.weapon,
                                suggestion.suspect,
                                next_player.name,
                            ).to_dict(),
                        }
                    )
                )

            elif message_type == "SUGGESTION_RESPONSE":
                print("Received suggestion response")
                print(message["data"])
                suggestion = SuggestionResponse(**message["data"])
                print(suggestion)

                if not any(
                    [suggestion.location, suggestion.weapon, suggestion.suspect]
                ):
                    pub_resp = PublicSuggestionResponse(suggestion.respondent, False)
                    await send_out_suggestion_response(
                        pub_resp.responding_player, pub_resp
                    )

                    curr_resp_idx = next(
                        i
                        for i, p in enumerate(all_players)
                        if p.name == pub_resp.responding_player
                    )

                    if (curr_resp_idx + 1) % len(all_players) != CURRENT_TURN_IDX:
                        next_player = all_players[
                            (curr_resp_idx + 1) % len(all_players)
                        ]
                        await connected_players[next_player.name].send(
                            json.dumps(
                                {
                                    "type": "SUGGESTION_RESPONSE",
                                    "data": SuggestionResponse(
                                        CURRENT_SUGGESTION.player,
                                        CURRENT_SUGGESTION.location,
                                        CURRENT_SUGGESTION.weapon,
                                        CURRENT_SUGGESTION.suspect,
                                        next_player.name,
                                    ).to_dict(),
                                }
                            )
                        )
                    else:
                        pub_resp = PublicSuggestionResponse(suggestion.respondent, True)
                        await send_out_suggestion_response(
                            pub_resp.responding_player, pub_resp
                        )
                        await connected_players[suggestion.player].send(
                            json.dumps(
                                {
                                    "type": "PRIVATE_SUGGESTION_RESPONSE",
                                    "data": suggestion.to_dict(),
                                }
                            )
                        )
                else:
                    pub_resp = PublicSuggestionResponse(suggestion.respondent, True)
                    await send_out_suggestion_response(
                        pub_resp.responding_player, pub_resp
                    )
                    await connected_players[suggestion.player].send(
                        json.dumps(
                            {
                                "type": "PRIVATE_SUGGESTION_RESPONSE",
                                "data": suggestion.to_dict(),
                            }
                        )
                    )

                    if suggestion.location and suggestion.location not in all_players[CURRENT_TURN_IDX].seen_cards["Location"]:
                        all_players[CURRENT_TURN_IDX].seen_cards["Location"].append(suggestion.location)
                    elif suggestion.suspect and suggestion.suspect not in all_players[CURRENT_TURN_IDX].seen_cards["Suspect"]:
                        all_players[CURRENT_TURN_IDX].seen_cards["Suspect"].append(suggestion.suspect)
                    elif suggestion.weapon and suggestion.weapon not in all_players[CURRENT_TURN_IDX].seen_cards["Weapon"]:
                        all_players[CURRENT_TURN_IDX].seen_cards["Weapon"].append(suggestion.weapon)

            elif message_type == "ACCUSATION":
                print("Received accusation")
                accusation = Accusation(**message["data"])

                if (
                    accusation.location == solution["Location"]
                    and accusation.weapon == solution["Weapon"]
                    and accusation.suspect == solution["Suspect"]
                ):
                    accusation.correct = True
                else:
                    all_players[CURRENT_TURN_IDX].skip_turns = True
                    prev_loc = PLAYER_TO_LOCATION[accusation.suspect]
                    PLAYER_TO_LOCATION[accusation.suspect] = accusation.location
                    LOCATION_TO_PLAYER[accusation.location] = accusation.suspect
                    LOCATION_TO_PLAYER[prev_loc] = ""

                await send_out_accusation(accusation)

                all_players[CURRENT_TURN_IDX].current_turn = False
                CURRENT_TURN_IDX = get_next_turn_idx(CURRENT_TURN_IDX)

                if CURRENT_TURN_IDX is not None:
                    all_players[CURRENT_TURN_IDX].current_turn = True
                    generate_valid_moves(all_players, PLAYER_TO_LOCATION)
                    await send_out_player_information("")
                else:
                    print("No players left. Game over?")

            elif message_type == "FINISHED_TURN":
                print("Received finished turn")
                print("all players: ")
                print(all_players)
                all_players[CURRENT_TURN_IDX].current_turn = False
                CURRENT_TURN_IDX = get_next_turn_idx(CURRENT_TURN_IDX)

                if CURRENT_TURN_IDX is not None:
                    all_players[CURRENT_TURN_IDX].current_turn = True
                    generate_valid_moves(all_players, PLAYER_TO_LOCATION)
                    await send_out_board_display("")
                    await send_out_player_information("")
                else:
                    print("No players left. Game over?")

    except websockets.ConnectionClosed:
        print(f"Connection closed from {websocket.remote_address}")


async def send_out_suggestion_response(player_exclude, suggestion):
    print("Sending suggestion response")
    for player in all_players:
        if player.name != player_exclude:
            try:
                await connected_players[player.name].send(
                    json.dumps(
                        {
                            "type": "PUBLIC_SUGGESTION_RESPONSE",
                            "data": suggestion.to_dict(),
                        }
                    )
                )
            except websockets.ConnectionClosed:
                pass


async def send_out_suggestion(player_exclude, suggestion):
    print("Sending suggestion")
    for player in all_players:
        if player.name != player_exclude:
            try:
                await connected_players[player.name].send(
                    json.dumps({"type": "SUGGESTION", "data": suggestion.to_dict()})
                )
            except websockets.ConnectionClosed:
                pass


async def send_out_player_information(player_exclude):
    print("Sending player info")
    for player in all_players:
        if player.name != player_exclude:
            try:
                await connected_players[player.name].send(
                    json.dumps({"type": "PLAYER", "data": player.to_dict()})
                )
            except websockets.ConnectionClosed:
                pass


async def send_out_accusation(accusation):
    print("Sending accusation")
    for player in all_players:
        try:
            await connected_players[player.name].send(
                json.dumps({"type": "ACCUSATION", "data": accusation.to_dict()})
            )
        except websockets.ConnectionClosed:
            pass


async def send_out_board_display(player_exclude):
    print("Sending board display")
    for player in all_players:
        if player.name != player_exclude:
            try:
                await connected_players[player.name].send(
                    json.dumps({"type": "BOARD", "data": PLAYER_TO_LOCATION})
                )
            except websockets.ConnectionClosed:
                pass


async def start_server():
    server = await websockets.serve(handler, "localhost", 8180)
    print("Server started on ws://localhost:8180")
    await server.wait_closed()


asyncio.get_event_loop().run_until_complete(start_server())
