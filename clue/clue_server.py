import players
import asyncio
import websockets
import json
from msgs.messages import ChoosePlayer, Accusation, Suggestion, SuggestionResponse, PublicSuggestionResponse
from players import (
    Player
    )
    
from server_side import initialize_game,generate_valid_moves

# Keep track of player connections (assigned player -> connection)
connected_players = {}

all_players = []
available_suspects = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
            'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
all_non_players = []
all_locations = set()
solution = {}

SOLVED = False

LOCATION_TO_PLAYER = {'Study':"", 'H1':"", 'Hall':"", 'H2':"Miss Scarlet", 'Lounge':"",
                    'H3':"Professor Plum", 'H4':"", 'H5':"Colonel Mustard", 
                    'Library':"", 'H6':"", 'Billiard Room':"", 'H7':"",'Dining Room':"",
                    'H8':"Mrs. Peacock", 'H9':"", 'H10':"", 
                    'Conservatory':"", 'H11':"Mr. Green", 'Ballroom':"", 'H12':"Mrs. White",'Kitchen':"",
                    '':''}
PLAYER_TO_LOCATION = {
    "Miss Scarlet": 'H2', 
    "Professor Plum": 'H3', 
    "Colonel Mustard": 'H5', 
    "Mrs. Peacock": 'H8', 
    "Mrs. White": 'H12', 
    "Mr. Green": 'H11', 
}

SUSPECTS = ['Colonel Mustard', 'Miss Scarlet', 'Professor Plum',
            'Mr. Green', 'Mrs. White', 'Mrs. Peacock']

CURRENT_TURN_IDX = 0

START_GAME = False

CURRENT_SUGGESTION = None

# handles all web socket connections
async def handler(websocket):
    global START_GAME
    global CURRENT_TURN_IDX
    global CURRENT_SUGGESTION
    global all_players
    global solution
   
    try:
        choose_player = ChoosePlayer("", available_suspects,False)
        msg = {
            "type": "CHOOSE_PLAYER",
            "data" : choose_player.to_dict()
        }

        # Send initial player select to new player
        await websocket.send(json.dumps(msg))

        # Handle incoming messages from this player
        while True:
            data = await websocket.recv()
            message = json.loads(data)

            message_type = message["type"]

            # HANDLE CHOOSE PLAYER MESSAGE
            if message_type == "CHOOSE_PLAYER" and not START_GAME:
                choose_player = ChoosePlayer(**message["data"])
                connected_players[choose_player.selected_player] = websocket
                available_suspects.remove(choose_player.selected_player)
                player = Player(choose_player.selected_player,"",None,None,False,False,[])
                player.location = PLAYER_TO_LOCATION[player.name]
                
                all_players.append(player)
                print(f"New player connected: {choose_player.selected_player}")

                if choose_player.start:
                    print(all_players)
                    START_GAME = True
                    print("Starting game!")
                    all_players, all_non_players, all_locations, solution = initialize_game(all_players,available_suspects)
                    print(f"The solution is: {solution}")
                    all_players[CURRENT_TURN_IDX].current_turn = True
                    generate_valid_moves(all_players,PLAYER_TO_LOCATION)
                    await send_out_board_display("")
                    await send_out_player_information("")
            
            # HANDLE PLAYER MESSAGE (player moves)
            elif message_type == "PLAYER":
                print("received player message!")
                player = Player(**message["data"])
                all_players[CURRENT_TURN_IDX] = player
                prev_loc = PLAYER_TO_LOCATION[player.name]
                PLAYER_TO_LOCATION[player.name] = player.location
                LOCATION_TO_PLAYER[player.location] = player.name
                LOCATION_TO_PLAYER[prev_loc] = ""

                generate_valid_moves(all_players,PLAYER_TO_LOCATION)
                await send_out_board_display(player.name)

            # HANDLE SUGGESTION MESSAGE
            elif message_type == "SUGGESTION":
                print("received suggestion message!")
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

                await send_out_suggestion(suggestion.player,suggestion)
                await send_out_board_display("")

                next_player = all_players[(CURRENT_TURN_IDX + 1) % len(all_players)]
                sugg_resp = SuggestionResponse(suggestion.player,suggestion.location,suggestion.weapon,suggestion.suspect,next_player.name)
                msg = {
                    "type": "SUGGESTION_RESPONSE",
                    "data" : sugg_resp.to_dict()
                }
                await connected_players[next_player.name].send(json.dumps(msg))
                
            # HANDLE SUGGESTION RESPONSE MESSAGE (did a player pass or show cards)
            elif message_type == "SUGGESTION_RESPONSE":
                print("received suggestion response message!")
                suggestion = SuggestionResponse(**message["data"])
                if (suggestion.location == "" and suggestion.weapon == "" and suggestion.suspect == ""):
                    pub_sugg_resp = PublicSuggestionResponse(suggestion.respondent,False)
                    await send_out_suggestion_response(pub_sugg_resp.responding_player,pub_sugg_resp)

                    curr_resp_idx = 0
                    for player in all_players:
                        if player.name == pub_sugg_resp.responding_player:
                            break
                        curr_resp_idx += 1
                    
                    if (curr_resp_idx + 1) % len(all_players) != CURRENT_TURN_IDX:
                        next_player = all_players[(curr_resp_idx + 1) % len(all_players)]
                        sugg_resp = SuggestionResponse(CURRENT_SUGGESTION.player,CURRENT_SUGGESTION.location,CURRENT_SUGGESTION.weapon,CURRENT_SUGGESTION.suspect,next_player.name)
                        msg = {
                            "type": "SUGGESTION_RESPONSE",
                            "data" : sugg_resp.to_dict()
                        }
                        await connected_players[next_player.name].send(json.dumps(msg))
                    else:
                        
                        pub_sugg_resp = PublicSuggestionResponse(suggestion.respondent,True)
                        await send_out_suggestion_response(pub_sugg_resp.responding_player,pub_sugg_resp)
                        msg = {
                            "type": "PRIVATE_SUGGESTION_RESPONSE",
                            "data" : suggestion.to_dict()
                        }
                        await connected_players[suggestion.player].send(json.dumps(msg))

                else:
                    pub_sugg_resp = PublicSuggestionResponse(suggestion.respondent,True)
                    await send_out_suggestion_response(pub_sugg_resp.responding_player,pub_sugg_resp)
                    msg = {
                        "type": "PRIVATE_SUGGESTION_RESPONSE",
                        "data" : suggestion.to_dict()
                    }
                    await connected_players[suggestion.player].send(json.dumps(msg))

                    if suggestion.location != "":
                        all_players[CURRENT_TURN_IDX].seen_cards["Location"].append(suggestion.location )
                    elif suggestion.suspect != "":
                        all_players[CURRENT_TURN_IDX].seen_cards["Suspect"].append(suggestion.suspect )
                    elif suggestion.weapon != "":
                        all_players[CURRENT_TURN_IDX].seen_cards["Weapon"].append(suggestion.weapon )
                    

            # HANDLE ACCUSATION MESSAGE
            elif message_type == "ACCUSATION":
                
                print("received accusation message!")
                accusation = Accusation(**message["data"])
                if (accusation.location == solution["Location"] and accusation.weapon == solution["Weapon"] and accusation.suspect == solution["Suspect"]):
                    accusation.correct = True
                else:
                    all_players[CURRENT_TURN_IDX].skip_turns = True
                    prev_loc = PLAYER_TO_LOCATION[accusation.suspect]
                    PLAYER_TO_LOCATION[accusation.suspect] = accusation.location
                    LOCATION_TO_PLAYER[accusation.location] = accusation.suspect
                    LOCATION_TO_PLAYER[prev_loc] = ""

                await send_out_accusation(accusation)

                all_players[CURRENT_TURN_IDX].current_turn = False
                CURRENT_TURN_IDX = (CURRENT_TURN_IDX + 1) % len(all_players)
                all_players[CURRENT_TURN_IDX].current_turn = True
                generate_valid_moves(all_players,PLAYER_TO_LOCATION)
                await send_out_player_information("")

            elif message_type == "FINISHED_TURN":
                print("received finished turn message!")
                all_players[CURRENT_TURN_IDX].current_turn = False
                CURRENT_TURN_IDX = (CURRENT_TURN_IDX + 1) % len(all_players)
                all_players[CURRENT_TURN_IDX].current_turn = True
                generate_valid_moves(all_players,PLAYER_TO_LOCATION)
                await send_out_board_display("")
                await send_out_player_information("")
            
    
    except websockets.ConnectionClosed:
        print(f"Connection closed from {websocket.remote_address}")
    
    # finally:
        # # Disconnect
        # del connected_players[suspect]


async def send_out_suggestion_response(player_exclude,suggestion):
    print("Sending out suggestion!")
    for player in all_players:
        if player_exclude != player.name:
            try:
                msg = {
                    "type": "PUBLIC_SUGGESTION_RESPONSE",
                    "data": suggestion.to_dict()
                }
                await connected_players[player.name].send(json.dumps(msg))
            except websockets.ConnectionClosed:
                pass 

async def send_out_suggestion(player_exclude,suggestion):
    print("Sending out suggestion!")
    for player in all_players:
        if player_exclude != player.name:
            try:
                msg = {
                    "type": "SUGGESTION",
                    "data": suggestion.to_dict()
                }
                await connected_players[player.name].send(json.dumps(msg))
            except websockets.ConnectionClosed:
                pass 

async def send_out_player_information(player_exclude):
    print("Sending out player info!")
    for player in all_players:
        if player_exclude != player.name:
            try:
                msg = {
                    "type": "PLAYER",
                    "data": player.to_dict()
                }
                await connected_players[player.name].send(json.dumps(msg))
            except websockets.ConnectionClosed:
                pass 

async def send_out_accusation(accusation):
    print("Sending out accusation!")
    for player in all_players:
        try:
            msg = {
                "type": "ACCUSATION",
                "data": accusation.to_dict()
            }
            await connected_players[player.name].send(json.dumps(msg))
        except websockets.ConnectionClosed:
            pass  

async def send_out_board_display(player_exclude):
    print("Sending out the current board display!")
    for player in all_players:
        if player_exclude != player.name:
            try:
                msg = {
                    "type": "BOARD",
                    "data": PLAYER_TO_LOCATION
                }
                await connected_players[player.name].send(json.dumps(msg))
            except websockets.ConnectionClosed:
                pass

async def start_server():
    server = await websockets.serve(handler, "localhost", 8180)
    print("Server started on ws://localhost:8180")
    await server.wait_closed()
    

asyncio.get_event_loop().run_until_complete(start_server())
