

LOCATIONS = ['Study', 'H1', 'Hall', 'H2', 'Lounge', 
             'H3','','H4','','H5',
             'Library', 'H6', 'Billiard Room', 'H7', 'Dining Room',
             'H8','','H9','','H10',
              'Conservatory', 'H11', 'Ballroom', 'H12','Kitchen']

PLAYER_LOCATIONS = {'Study':"", 'H1':"", 'Hall':"", 'H2':"MS", 'Lounge':"",
                    'H3':"PP", 'H4':"", 'H5':"CM", 
                    'Library':"", 'H6':"", 'Billiard Room':"", 'H7':"",'Dining Room':"",
                    'H8':"MP", 'H9':"", 'H10':"", 
                    'Conservatory':"", 'H11':"MG", 'Ballroom':"", 'H12':"MW",'Kitchen':"",
                    '':''}

PLAYER_TO_LOCATION = {
    "Miss Scarlet": 'H2', 
    "Professor Plum": 'H3', 
    "Colonel Mustard": 'H5', 
    "Mrs. Peacock": 'H8', 
    "Mrs. White": 'H8', 
    "Mr. Green": 'H11', 
}

# def draw_board(players):
#     size = 5  

#     location_count = 0
#     print("-" * 85)
#     for row in range(size):
#         str_row = ""
#         if row % 2 != 0:
#             str_row += "-" * 85 + "\n"
#         for col in range(size):
#             str_row += "|" + LOCATIONS[row*5 + col].center(15) + "|"
#         str_row += "\n"
#         for col in range(size):
#             str_row += "|" + players[LOCATIONS[row*5 + col]].center(15) + "|"

#         if row % 2 != 0:
#             str_row += "\n" + "-" * 85 
                
        
        
#         print(str_row)  # New line after each row
#     print("-" * 85)


def draw_board(players):
    size = 5  

    location_count = 0
    print("-" * 85)
    for row in range(size):
        str_row = ""
        if row % 2 != 0:
            str_row += "-" * 85 + "\n"
        locs = []
        inserted_players = {}
        for col in range(size):
            str_row += "|" + LOCATIONS[row*5 + col].center(15) + "|"
            locs.append(LOCATIONS[row*5 + col])
            inserted_players[LOCATIONS[row*5 + col]] = []
        str_row += "\n"

        for loc in locs:
            for player, location in players.items():
                if location == loc:
                    inserted_players[loc].append(player)
                else:
                    inserted_players[loc].append("")
        
        for i in range(len(players)):
            for col in range(size):
                str_row += "|" + inserted_players[LOCATIONS[row*5 + col]][i].center(15) + "|"
            str_row += "\n"

        if row % 2 != 0:
            str_row += "\n" + "-" * 85 
        
        print(str_row)  # New line after each row
    print("-" * 85)


#draw_board2(PLAYER_TO_LOCATION)