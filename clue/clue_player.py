import asyncio
import websockets
import draw_board_terminal
import json
from msgs.messages import ChoosePlayer, Accusation, Suggestion, SuggestionResponse, PublicSuggestionResponse
from player_side_util import make_suggestion,generate_suggestion_response, make_accusation
from player import Player


MY_PLAYER: Player
prev_board = {}
prev_cards = {}
GAME_OVER = False

async def connect():
    global prev_board
    global GAME_OVER
    uri = "ws://localhost:8180"

    async with websockets.connect(uri) as websocket:

        print("player has connected")
        while True:
            try:
                if GAME_OVER:
                    return
                
                # Wait for a message from the server
                data = await websocket.recv()
                message = json.loads(data)

                message_type = message["type"]
                
                ## INITIAL CHOOSE PLAYER MSG
                if message_type == "CHOOSE_PLAYER":
                    choose_player = ChoosePlayer(**message["data"])
                    print(f'Which of the following suspects would you like to play as?\n{choose_player.players}')
                    choose_player.selected_player = await asyncio.to_thread(input,'Please type in your preferred character: ')
                    
                    while choose_player.selected_player not in choose_player.players:
                        print(f'Error: {choose_player.selected_player} is not a valid character.')
                        print(f'Which of the following suspects would you like to play as?\n{choose_player.players}')
                        choose_player.selected_player = await asyncio.to_thread(input,'Please type in your preferred character: ')
                    
                    if (len(choose_player.players) < 5):
                        choose_player.start = 'y' == await asyncio.to_thread(input,f'There are {6- len(choose_player.players)} other players, would you like to start the game? y/n: ')
                    else:
                        choose_player.start = False
                    
                    msg = {
                        "type": "CHOOSE_PLAYER",
                        "data": choose_player.to_dict()
                    }
                    await websocket.send(json.dumps(msg))

                    print("Thank you, waiting for the game to start...")
                ## BOARD MESSAGE WITH UPDATED LOCATIONS
                elif message_type == "BOARD":
                    current_board = message["data"]
                    
                    if prev_board != current_board:
                        draw_board_terminal.draw_board(current_board)
                        prev_board = current_board
                ## PLAYER MSG NOTIFYING TURN AND PLAYER INFO
                elif message_type == "PLAYER":
                    MY_PLAYER = Player(**message["data"])
                    print(MY_PLAYER.name)
                    print(f"Your cards: {MY_PLAYER.cards}")
                    
                    if MY_PLAYER.current_turn:
                        if MY_PLAYER.skip_turns:
                            msg = {
                                "type": "FINISHED_TURN"
                            }
                            await websocket.send(json.dumps(msg))
                        else:
                            action = await asyncio.to_thread(input,"Would you like to move or stay? m/s: ")
                            
                            if action == 'm':
                                move = await asyncio.to_thread(input,f"Please select one of your available moves {MY_PLAYER.valid_moves}: ")
                                
                                while move not in MY_PLAYER.valid_moves:
                                    move = await asyncio.to_thread(input,f"Invalid move, you must select from one of the available options {MY_PLAYER.valid_moves}: ")
                                
                                MY_PLAYER.location = move
                                msg = {
                                    "type": "PLAYER",
                                    "data": MY_PLAYER.to_dict()
                                }
                                await websocket.send(json.dumps(msg))
                            
                            if len(MY_PLAYER.location) > 3:
                                sug_input = await asyncio.to_thread(input,"Would you like to make a suggestion? y/n: ")
                                
                                if sug_input == 'y':
                                    weapon , suspect = await make_suggestion(MY_PLAYER)
                                    suggestion = Suggestion(MY_PLAYER.name, MY_PLAYER.location, weapon, suspect)
                                    msg = {
                                        "type": "SUGGESTION",
                                        "data": suggestion.to_dict()
                                    }
                                    await websocket.send(json.dumps(msg))
                                else:
                                    msg = {
                                    "type": "FINISHED_TURN"
                                    }
                                    await websocket.send(json.dumps(msg))
                            else:
                                msg = {
                                    "type": "FINISHED_TURN"
                                }
                                await websocket.send(json.dumps(msg))
                ## OTHER PLAYER'S SUGGESTION SENT TO ALL PLAYERS
                elif message_type == "SUGGESTION":
                    sugg = Suggestion(**message["data"])
                    print(f'{sugg.player}, made a suggestion: Location: {sugg.location}, Weapon: {sugg.weapon}, Suspect: {sugg.suspect}')
                    print(f"Waiting for player responses...")
                ## SUGGESTION RESPONSE SENT TO ALL PLAYERS
                elif message_type == "PUBLIC_SUGGESTION_RESPONSE":
                    pub_sugg_resp = PublicSuggestionResponse(**message["data"])
                    if pub_sugg_resp.showed_card:
                        print(f"Player {pub_sugg_resp.responding_player} showed a card!")
                    else:
                        print(f"Player {pub_sugg_resp.responding_player} passed!")
                ## RESPONSE TO CURRENT PLAYER'S SUGGESTION
                elif message_type == "PRIVATE_SUGGESTION_RESPONSE":
                    priv_sugg_resp = SuggestionResponse(**message["data"])
                    if priv_sugg_resp.location != "":
                        print(f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.location}")
                    elif priv_sugg_resp.suspect != "":
                        print(f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.suspect}")
                    elif priv_sugg_resp.weapon != "":
                        print(f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.weapon}")

                    acc_input = await asyncio.to_thread(input,"Would you like to make an accusation? y/n: ")
                    
                    if acc_input == 'y':
                        room, weapon , suspect = await make_accusation(MY_PLAYER)
                        accusation = Accusation(MY_PLAYER.name, room, weapon, suspect, False)
                        msg = {
                            "type": "ACCUSATION",
                            "data": accusation.to_dict()
                        }
                        await websocket.send(json.dumps(msg))
                    else:
                        msg = {
                        "type": "FINISHED_TURN"
                        }
                        await websocket.send(json.dumps(msg))
                ## CURRENT PLAYER'S REPSONSE TO OTHER PLAYER'S SUGGESTION
                elif message_type == "SUGGESTION_RESPONSE":
                    sugg_resp = SuggestionResponse(**message["data"])
                    gen_sugg_resp = await generate_suggestion_response(sugg_resp, MY_PLAYER)
                    msg = {
                        "type": "SUGGESTION_RESPONSE",
                        "data": gen_sugg_resp.to_dict()
                    }
                    await websocket.send(json.dumps(msg))
                ## OTHER PLAYER'S ACCUSATION AND RESULT
                elif message_type == "ACCUSATION":
                    acc = Accusation(**message["data"])
                    
                    if acc.correct:
                        print(f'{acc.player}, made a CORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}')
                        print("Game over!")
                        GAME_OVER = True
                    else:
                        print(f'{acc.player}, made an INCORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}')
                        print(f"{acc.player} is now out of the game!")
            
            except Exception as e:
                print(f"An error occurred: {e}")
                break

# Run the client
asyncio.get_event_loop().run_until_complete(connect())



