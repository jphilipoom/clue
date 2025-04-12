import asyncio
import websockets
import json
from PyQt5.QtCore import QThread, pyqtSignal

from Interface.Player import Player
from msgs.messages import ChoosePlayer

# MY_PLAYER: Player
prev_board = {}
# prev_cards = {}
# GAME_OVER = False


# WebSocket Thread to handle async communication
class WebSocketThread(QThread):
    player_list_signal = pyqtSignal(list)  # Signal to pass updated player list to GUI
    start_game_signal = pyqtSignal(bool)  # Signal to notify when game can start
    character_selected_signal = pyqtSignal(
        dict
    )  # Signal to get selected character name
    choose_player_signal = pyqtSignal(dict)
    update_board_signal = pyqtSignal(dict)  # Signal to update players list

    def __init__(self):
        super().__init__()
        self.uri = "ws://localhost:8180"  # WebSocket URL
        self.players = []
        self.selected_character = None
        self.starting_game = False

        self.character_selected_signal.connect(self.on_character_selected)

    def on_character_selected(self, character_selected_dict):
        print("REC IN WEBSOCKET on char selected")

        character_name = character_selected_dict["selected_player"]
        self.selected_character = character_name  # Save selected character
        self.starting_game = character_selected_dict["start"]

    def run(self):
        # WebSocket connection and event loop
        asyncio.run(self.connect())

    async def connect(self):
        global prev_board
        async with websockets.connect(self.uri) as websocket:
            while True:
                data = await websocket.recv()
                message = json.loads(data)

                message_type = message["type"]

                info = message["data"]

                print(info)

                if message_type == "CHOOSE_PLAYER":
                    # Update player list from the server message
                    self.players = [Player(x) for x in info["players"]]
                    self.player_list_signal.emit(self.players)
                    self.choose_player_signal.emit(info)

                    # Wait until a character is selected
                    while self.selected_character is None:
                        await asyncio.sleep(0.1)

                    # Find the Player object matching selected character
                    chosen_player = next(
                        (p for p in self.players if p.name == self.selected_character),
                        None,
                    )

                    players_without_this = [
                        player.name
                        for player in self.players
                        if player != chosen_player
                    ]

                    if chosen_player:
                        cp = ChoosePlayer(
                            selected_player=chosen_player.name,
                            players=players_without_this,
                            start=self.starting_game,
                        )

                        msg = {"type": "CHOOSE_PLAYER", "data": cp.to_dict()}

                        await websocket.send(json.dumps(msg))
                elif message_type == "BOARD":
                    # print("info is")
                    # print(info)
                    self.update_board_signal.emit(info)

                    current_board = info

                    if prev_board != current_board:
                        print("New board!!!!")
                        # draw_board_terminal.draw_board(current_board)
                        prev_board = current_board
                ## PLAYER MSG NOTIFYING TURN AND PLAYER INFO
                # elif message_type == "PLAYER":
                #     MY_PLAYER = Player(**message["data"])
                #     print(MY_PLAYER.name)
                #     print(f"Your cards: {MY_PLAYER.cards}")

                #     if MY_PLAYER.current_turn:
                #         if MY_PLAYER.skip_turns:
                #             msg = {
                #                 "type": "FINISHED_TURN"
                #             }
                #             await websocket.send(json.dumps(msg))
                #         else:
                #             action = await asyncio.to_thread(input,"Would you like to move or stay? m/s: ")

                #             if action == 'm':
                #                 move = await asyncio.to_thread(input,f"Please select one of your available moves {MY_PLAYER.valid_moves}: ")

                #                 while move not in MY_PLAYER.valid_moves:
                #                     move = await asyncio.to_thread(input,f"Invalid move, you must select from one of the available options {MY_PLAYER.valid_moves}: ")

                #                 MY_PLAYER.location = move
                #                 msg = {
                #                     "type": "PLAYER",
                #                     "data": MY_PLAYER.to_dict()
                #                 }
                #                 await websocket.send(json.dumps(msg))

                #             if len(MY_PLAYER.location) > 3:
                #                 sug_input = await asyncio.to_thread(input,"Would you like to make a suggestion? y/n: ")

                #                 if sug_input == 'y':
                #                     weapon , suspect = await make_suggestion(MY_PLAYER)
                #                     suggestion = Suggestion(MY_PLAYER.name, MY_PLAYER.location, weapon, suspect)
                #                     msg = {
                #                         "type": "SUGGESTION",
                #                         "data": suggestion.to_dict()
                #                     }
                #                     await websocket.send(json.dumps(msg))
                #                 else:
                #                     msg = {
                #                     "type": "FINISHED_TURN"
                #                     }
                #                     await websocket.send(json.dumps(msg))
                #             else:
                #                 msg = {
                #                     "type": "FINISHED_TURN"
                #                 }
                #                 await websocket.send(json.dumps(msg))
                # ## OTHER PLAYER'S SUGGESTION SENT TO ALL PLAYERS
                # elif message_type == "SUGGESTION":
                #     sugg = Suggestion(**message["data"])
                #     print(f'{sugg.player}, made a suggestion: Location: {sugg.location}, Weapon: {sugg.weapon}, Suspect: {sugg.suspect}')
                #     print(f"Waiting for player responses...")
                # ## SUGGESTION RESPONSE SENT TO ALL PLAYERS
                # elif message_type == "PUBLIC_SUGGESTION_RESPONSE":
                #     pub_sugg_resp = PublicSuggestionResponse(**message["data"])
                #     if pub_sugg_resp.showed_card:
                #         print(f"Player {pub_sugg_resp.responding_player} showed a card!")
                #     else:
                #         print(f"Player {pub_sugg_resp.responding_player} passed!")
                # ## RESPONSE TO CURRENT PLAYER'S SUGGESTION
                # elif message_type == "PRIVATE_SUGGESTION_RESPONSE":
                #     priv_sugg_resp = SuggestionResponse(**message["data"])
                #     if priv_sugg_resp.location != "":
                #         print(f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.location}")
                #     elif priv_sugg_resp.suspect != "":
                #         print(f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.suspect}")
                #     elif priv_sugg_resp.weapon != "":
                #         print(f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.weapon}")

                #     acc_input = await asyncio.to_thread(input,"Would you like to make an accusation? y/n: ")

                #     if acc_input == 'y':
                #         room, weapon , suspect = await make_accusation(MY_PLAYER)
                #         accusation = Accusation(MY_PLAYER.name, room, weapon, suspect, False)
                #         msg = {
                #             "type": "ACCUSATION",
                #             "data": accusation.to_dict()
                #         }
                #         await websocket.send(json.dumps(msg))
                #     else:
                #         msg = {
                #         "type": "FINISHED_TURN"
                #         }
                #         await websocket.send(json.dumps(msg))
                # ## CURRENT PLAYER'S REPSONSE TO OTHER PLAYER'S SUGGESTION
                # elif message_type == "SUGGESTION_RESPONSE":
                #     sugg_resp = SuggestionResponse(**message["data"])
                #     gen_sugg_resp = await generate_suggestion_response(sugg_resp, MY_PLAYER)
                #     msg = {
                #         "type": "SUGGESTION_RESPONSE",
                #         "data": gen_sugg_resp.to_dict()
                #     }
                #     await websocket.send(json.dumps(msg))
                # ## OTHER PLAYER'S ACCUSATION AND RESULT
                # elif message_type == "ACCUSATION":
                #     acc = Accusation(**message["data"])

                #     if acc.correct:
                #         print(f'{acc.player}, made a CORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}')
                #         print("Game over!")
                #         GAME_OVER = True
                #     else:
                #         print(f'{acc.player}, made an INCORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}')
                #         print(f"{acc.player} is now out of the game!")
