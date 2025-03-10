from clue.server_side import initialize_game
from clue.server_side import turn

if __name__ == '__main__':
    game_code = input('Enter the game code for an existing game or N to start a new game.')
    host = False

    if game_code != 'N':
        # TODO: check if there is already a game with that code, start a new game if not

        # TODO: if a game is found, spin up client side functions
        print('Sorry, we are unable to find a new game with that code. '
              'Starting a new game...')
        game_code = 'N'

    if game_code == 'N':
        host = True
        all_players, all_non_players, all_locations, solution = initialize_game()
        solved = False
        while not solved:
            for active_player in all_players:
                if not active_player.skip_turns:
                    all_players, all_non_players, all_locations, solved = turn(active_player,
                                                                               all_players,
                                                                               all_non_players,
                                                                               all_locations,
                                                                               solution)
                if solved:
                    break
