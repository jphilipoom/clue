import asyncio
import websockets
import json
from PyQt5.QtCore import QThread, pyqtSignal

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

import asyncio
import websockets

MY_PLAYER: Player
prev_board = {}
# prev_cards = {}
GAME_OVER = False


# TODO: need to add in the stuff
# WebSocket Thread to handle async communication
class WebSocketThread(QThread):
    player_list_signal = pyqtSignal(list)  # Signal to pass updated player list to GUI
    start_game_signal = pyqtSignal(bool)  # Signal to notify when game can start
    character_selected_signal = pyqtSignal(
        dict
    )  # Signal to get selected character name
    send_board_signal = pyqtSignal(dict)
    choose_player_signal = pyqtSignal(dict)
    send_board_signal = pyqtSignal(dict)  # Signal to update players list
    player_turn_signal = pyqtSignal(dict)  # Signal to update players list
    tile_clicked = pyqtSignal(str)  # Signal to get selected character name
    suggestion_response_options_signal = pyqtSignal(dict)

    game_info_bar = pyqtSignal(str)

    (accusation_value, suggestion_value) = (None, None)

    def __init__(self):
        super().__init__()
        self.uri = "ws://localhost:8180"  # WebSocket URL
        self.players = []
        self.selected_character = None
        self.starting_game = False

        self.tile_move = None
        self.tile_clicked.connect(self.on_character_moved)

        self.suggestion_response_received = False
        self.suggestion_response_value = None

    def on_character_selected(self, character_selected_dict):
        character_name = character_selected_dict["selected_player"]
        self.selected_character = character_name  # Save selected character
        self.starting_game = character_selected_dict["start"]

    def on_character_moved(self, move_loc):
        print(f"Websocket received on character move with value {move_loc}\n"
            f"The current values of websocket are: {self.selected_character} {self.starting_game} "
            f"{self.tile_move} {self.suggestion_response_value} {self.suggestion_response_received}")


        self.tile_move = move_loc

    def will_accuse(self, value):
        self.will_accuse = value
        self.will_suggest = False
        print("will accuse: " + str(value))

    def will_suggest(self, value):
        self.will_suggest = value
        self.will_move = False
        print("will suggest: " + str(value))

    def will_move(self, value):
        self.will_move = value
        print("will move: " + str(value))

    def handle_accusation(self, value):
        self.accusation_value = value
        print("accuse: " + str(value))

    def handle_suggestion(self, value):
        self.suggestion_value = value
        print("suggest: " + str(value))

    def handle_suggestion_response(self, value):
        self.suggestion_response_value = value
        print("suggest response: " + str(value))

    def run(self):
        """Integrate PyQt event loop with asyncio."""
        self.loop = asyncio.new_event_loop()  # Create a new event loop for asyncio
        asyncio.set_event_loop(self.loop)  # Set the new event loop
        self.loop.create_task(
            self.connect()
        )  # Start the WebSocket connection in the asyncio loop
        self.loop.run_forever()  # Run the event loop

    async def connect(self):
        global GAME_OVER
        global prev_board
        global MY_PLAYER
        async with websockets.connect(self.uri) as websocket:
            print("Connected to WebSocket server")

            # Create tasks for sending and receiving concurrently
            print("rec")
            global GAME_OVER

            while not GAME_OVER:
                data = await websocket.recv()
                message = json.loads(data)

                message_type = message["type"]

                info = message["data"]

                print("new message!")
                print(message)

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
                    self.send_board_signal.emit(info)

                    current_board = info

                    if prev_board != current_board:
                        # draw_board_terminal.draw_board(current_board)
                        prev_board = current_board
                elif message_type == "PLAYER":
                    print(info)
                    MY_PLAYER = Player(**message["data"])
                    self.player_turn_signal.emit(info)

                    if MY_PLAYER.current_turn:
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

                            # TODO: need to add code to show the user what the other user showed for their suggestion

                            msg = self.suggestion_value
                            await websocket.send(json.dumps(msg))

                            # TODO: don't seem to see the response after a suggestion appear on suggestor's screen

                            # while not self.suggestion_response_received:
                            #     print("no resp received")
                            #     await asyncio.sleep(0.1)
                            #     self.suggestion_response_received = False

                            # continue  # gives opportunity to see sugg resp??

                        while self.will_accuse is None:
                            # TODO: issue with getting stuck here and not sending a finished turn signal when not making an accusation....
                            await asyncio.sleep(0.1)
                        if self.will_accuse is True:
                            # TODO: this code is not hit when the bugs above happen with suggestion response info not seen
                            while self.accusation_value is None:
                                await asyncio.sleep(0.1)
                            print("send accus")
                            print(self.accusation_value)

                            msg = self.accusation_value
                            await websocket.send(json.dumps(msg))
                        else:
                            print("will not accuse")

                        print("MY TURN IS NOW OVER")
                        msg = {"type": "FINISHED_TURN"}
                        await websocket.send(json.dumps(msg))

                        (self.will_move, self.will_suggest, self.will_accuse) = (
                            None,
                            None,
                            None,
                        )
                        (
                            self.accusation_value,
                            self.suggestion_value,
                            self.tile_move,
                        ) = (
                            None,
                            None,
                            None,
                        )

                elif message_type == "SUGGESTION":
                    sugg = Suggestion(**message["data"])
                    print(
                        f"{sugg.player}, made a suggestion: Location: {sugg.location}, Weapon: {sugg.weapon}, Suspect: {sugg.suspect}"
                    )
                    self.game_info_bar.emit(
                        f"{sugg.player}, made a suggestion: Location: {sugg.location}, Weapon: {sugg.weapon}, Suspect: {sugg.suspect}"
                    )
                    print("Waiting for player responses...")

                ## SUGGESTION RESPONSE SENT TO ALL PLAYERS
                elif message_type == "PUBLIC_SUGGESTION_RESPONSE":
                    pub_sugg_resp = PublicSuggestionResponse(**message["data"])

                    if pub_sugg_resp.showed_card:
                        print(
                            f"Player {pub_sugg_resp.responding_player} showed a card!"
                        )
                        self.game_info_bar.emit(
                            f"Player {pub_sugg_resp.responding_player} showed a card!"
                        )
                        self.suggestion_response_received = True

                    else:
                        print(f"Player {pub_sugg_resp.responding_player} passed!")
                        self.game_info_bar.emit(
                            f"Player {pub_sugg_resp.responding_player} passed!"
                        )
                ## RESPONSE TO CURRENT PLAYER'S SUGGESTION
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
                elif message_type == "SUGGESTION_RESPONSE":
                    sugg_resp = SuggestionResponse(**message["data"])
                    # TODO: replace this text input with some sort of button/option on GUI

                    print("all the data provided in sugg resp")
                    accuser_details_dict = {
                        "found_cards": MY_PLAYER.check_accusation(
                            sugg_resp.weapon, sugg_resp.suspect, sugg_resp.location
                        ),
                        "accuser": sugg_resp.player
                    }

                    if len(accuser_details_dict["found_cards"]) > 0:

                        self.suggestion_response_options_signal.emit(accuser_details_dict)

                        while self.suggestion_response_value is None:
                            print("waiting on user to provide response to a suggestion")
                            await asyncio.sleep(0.1)

                        # # THIS IS THE PRIVATE MSG
                        msg = self.suggestion_response_value
                        msg["data"]["player"] = sugg_resp.player

                        msg["type"] = "SUGGESTION_RESPONSE"
                        print(msg)
                        await websocket.send(json.dumps(msg))

                    else:
                        empty_sugg_resp = SuggestionResponse(
                            respondent=MY_PLAYER.name,
                            player=sugg_resp.player,
                            location="",
                            weapon="",
                            suspect="",
                        )

                        print("returning same thing, has nothing to offer msg value: ")
                        msg = {
                            "type": "SUGGESTION_RESPONSE",
                            "data": empty_sugg_resp.to_dict(),
                        }

                        await websocket.send(json.dumps(msg))

                elif message_type == "ACCUSATION":
                    acc = Accusation(**message["data"])

                    if acc.correct:
                        print(
                            f"{acc.player}, made a CORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}"
                        )
                        print("Game over!")
                        self.game_info_bar.emit(
                            f"Game over!!! {acc.player}, made a CORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}"
                        )
                        GAME_OVER = True
                    else:
                        print(
                            f"{acc.player}, made an INCORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}"
                        )
                        self.game_info_bar.emit(
                            f"{acc.player}, made an INCORRECT accusation: Location: {acc.location}, Weapon: {acc.weapon}, Suspect: {acc.suspect}, {acc.player} is now out of the game!"
                        )
                        print(f"{acc.player} is now out of the game!")
