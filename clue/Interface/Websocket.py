import asyncio
import websockets
import json
from PyQt5.QtCore import QThread, pyqtSignal

from Interface.Player import DumbPlayer
from player import Player

from msgs.messages import (
    ChoosePlayer,
    SuggestionResponse,
    PublicSuggestionResponse,
    Suggestion,
    Accusation,
)
from player_side_util import (
    make_suggestion,
    generate_suggestion_response,
    make_accusation,
)

# MY_PLAYER: Player
prev_board = {}
# prev_cards = {}
# GAME_OVER = False


# TODO: need to add in the stuff
# WebSocket Thread to handle async communication
class WebSocketThread(QThread):
    player_list_signal = pyqtSignal(list)  # Signal to pass updated player list to GUI
    start_game_signal = pyqtSignal(bool)  # Signal to notify when game can start
    character_selected_signal = pyqtSignal(
        dict
    )  # Signal to get selected character name
    choose_player_signal = pyqtSignal(dict)
    update_board_signal = pyqtSignal(dict)  # Signal to update players list
    player_turn_signal = pyqtSignal(dict)  # Signal to update players list
    tile_clicked = pyqtSignal(str)  # Signal to get selected character name
    suggestion_response_options_signal = pyqtSignal(list)

    (accusation_value, suggestion_value, suggestion_response_value) = (None, None, None)

    def __init__(self):
        super().__init__()
        self.uri = "ws://localhost:8180"  # WebSocket URL
        self.players = []
        self.selected_character = None
        self.starting_game = False

        self.tile_move = None

        self.tile_clicked.connect(self.on_character_moved)

    def on_character_selected(self, character_selected_dict):
        character_name = character_selected_dict["selected_player"]
        self.selected_character = character_name  # Save selected character
        self.starting_game = character_selected_dict["start"]

    def on_character_moved(self, move_loc):
        self.tile_move = move_loc

    def will_accuse(self, value):
        self.will_accuse = value

    def will_suggest(self, value):
        self.will_suggest = value

    def will_move(self, value):
        self.will_move = value

    def handle_accusation(self, value):
        self.accusation_value = value
        print("HANDLING ACCUS")

    def handle_suggestion(self, value):
        self.suggestion_value = value
        print(value)

    def handle_suggestion_response(self, value):
        self.suggestion_response_value = value
        print(value)

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

                if message_type == "CHOOSE_PLAYER":
                    # Update player list from the server message
                    self.players = [DumbPlayer(x) for x in info["players"]]
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
                # Note: this will only trigger the new board layout
                elif message_type == "BOARD":
                    self.update_board_signal.emit(info)

                    current_board = info

                    if prev_board != current_board:
                        # draw_board_terminal.draw_board(current_board)
                        prev_board = current_board
                # Note: this will trigger requests for if the player wants to move and/or make a suggestion
                elif message_type == "PLAYER":
                    print(info)
                    MY_PLAYER = Player(**message["data"])
                    self.player_turn_signal.emit(info)

                    if MY_PLAYER.current_turn:

                        # skip_turns is True if the oplayer failed an accusation, this will skip their turn everytime since they are out of the game
                        if MY_PLAYER.skip_turns:
                            msg = {
                                "type": "FINISHED_TURN"
                            }
                            await websocket.send(json.dumps(msg))
                        else:
                            # TODO: make sure this doesn't cause stalls when they pick not to move locations
                            # Wait until a location is selected
                            while self.will_move is None:
                                await asyncio.sleep(0.1)
                            if self.will_move is True:
                                while self.tile_move is None:
                                    await asyncio.sleep(0.1)
                                MY_PLAYER.location = self.tile_move
                                msg = {"type": "PLAYER", "data": MY_PLAYER.to_dict()}
                                await websocket.send(json.dumps(msg))

                            while self.will_suggest is None:
                                await asyncio.sleep(0.1)
                            if self.will_suggest is True:
                                while self.suggestion_value is None:
                                    await asyncio.sleep(0.1)

                                msg = self.suggestion_value
                                # send suggestion to server, server will then first broadcast suggestion info, then privately ask players for sugg response
                                await websocket.send(json.dumps(msg))
                            else:
                                print("MY TURN IS NOW OVER")
                                msg = {"type": "FINISHED_TURN"}
                                await websocket.send(json.dumps(msg))

                        # while self.will_accuse is None:
                        #     print("wait")
                        #     await asyncio.sleep(0.1)
                        # if self.will_accuse is True:
                        #     while self.accusation_value is None:
                        #         await asyncio.sleep(0.1)
                        #     print("send accus")

                        #     msg = self.accusation_value
                        #     await websocket.send(json.dumps(msg))

                        # (self.will_move, self.will_suggest, self.will_accuse) = (
                        #     None,
                        #     None,
                        #     None,
                        # )
                        # (
                        #     self.accusation_value,
                        #     self.suggestion_value,
                        #     self.tile_move,
                        # ) = (
                        #     None,
                        #     None,
                        #     None,
                        # )

                        # print("MY TURN IS NOW OVER")
                        # msg = {"type": "FINISHED_TURN"}
                        # await websocket.send(json.dumps(msg))

                # this is the public broadcast of suggestion info (Note: this will not trigger any actions)
                elif message_type == "SUGGESTION":
                    sugg = Suggestion(**message["data"])
                    print(
                        f"{sugg.player}, made a suggestion: Location: {sugg.location}, Weapon: {sugg.weapon}, Suspect: {sugg.suspect}"
                    )
                    print(f"Waiting for player responses...")
                ## SUGGESTION RESPONSE SENT TO ALL PLAYERS (Note: this will not trigger any actions)
                elif message_type == "PUBLIC_SUGGESTION_RESPONSE":
                    pub_sugg_resp = PublicSuggestionResponse(**message["data"])
                    if pub_sugg_resp.showed_card:
                        print(
                            f"Player {pub_sugg_resp.responding_player} showed a card!"
                        )
                    else:
                        print(f"Player {pub_sugg_resp.responding_player} passed!")

                ## RESPONSE TO CURRENT PLAYER'S SUGGESTION (Note: This will trigger the accusation request action)
                elif message_type == "PRIVATE_SUGGESTION_RESPONSE":
                    priv_sugg_resp = SuggestionResponse(**message["data"])
                    if priv_sugg_resp.location != "":
                        print(
                            f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.location}"
                        )
                    elif priv_sugg_resp.suspect != "":
                        print(
                            f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.suspect}"
                        )
                    elif priv_sugg_resp.weapon != "":
                        print(
                            f"Player {priv_sugg_resp.respondent} showed you {priv_sugg_resp.weapon}"
                        )
                    # Note: if all fields  are "" then all players passed

                    # TODO
                    # At this point the player who made the initial suggestion, will have the result of their suggestion (a player showed card or all players passed)
                    # This is where you want to ask if they want to make accusation or not and send the result to server
                    while self.will_accuse is None:
                            print("wait")
                            await asyncio.sleep(0.1)
                        if self.will_accuse is True:
                            while self.accusation_value is None:
                                await asyncio.sleep(0.1)
                            print("send accus")

                            msg = self.accusation_value
                            await websocket.send(json.dumps(msg))
                        else:
                            print("MY TURN IS NOW OVER")
                            msg = {"type": "FINISHED_TURN"}
                            await websocket.send(json.dumps(msg))

                # This is asking the current player to show their card if present in the suggestion (Note: this will trigger the suggestion response action)
                elif message_type == "SUGGESTION_RESPONSE":
                    sugg_resp = SuggestionResponse(**message["data"])
                    # TODO: replace this text input with some sort of button/option on GUI

                    print("all the data provided in sugg resp")
                    found_cards = MY_PLAYER.check_accusation(
                        sugg_resp.weapon, sugg_resp.suspect, sugg_resp.location
                    )

                    # start with an empty suggestion
                    resp = SuggestionResponse(suggestion.player, "","","",curr_player.name)

                    # If the current player does not have any matching cards in suggestion, send an empty suggestion to the server,
                    # this will let the server know to ask the next player
                    if len(found_cards) == 0:
                        msg = {"type": "SUGGESTION_RESPONSE", "data": resp.to_dict()}
                        await websocket.send(json.dumps(msg))
                    else:
                        self.suggestion_response_options_signal.emit(found_cards)
                        # TODO fill in the empty suggestion with whatever card the player chooses to show and send this to the server

                ## OTHER PLAYER'S ACCUSATION AND RESULT (Everyone gets this even the player who made the accusation Note: this will not trigger any actions)
                elif message_type == "ACCUSATION":
                    acc = Accusation(**message["data"])

                    if acc.correct:
                        print(
                            f"{acc.player}, made a CORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}"
                        )
                        print("Game over!")
                        GAME_OVER = True
                    else:
                        print(
                            f"{acc.player}, made an INCORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}"
                        )
                        print(f"{acc.player} is now out of the game!")

                # old below this point probably
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
