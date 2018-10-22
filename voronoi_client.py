import socket
import time
import random
import sys
import math
import json
#import numpy as np
#from itertools import combinations


class Client:

    """
    Perform steps 1-3 of the client-server protocol in constructor, 
    as they are only done once anyways
    """
    def __init__(self, host: str, port: int, name: str):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.grid_size = 1000
        self.min_dist = 66
        self.virtual_board_partition = 25
        self.virtual_dimension = int(self.grid_size / self.virtual_board_partition)
        self.virtual_board = [[0] * int(self.virtual_dimension) for i in range(int(self.virtual_dimension))]
        self.turn = 0
        self.first = False
        self.priority_coordinates = [[400, 400], [790, 790], [210, 790], [600, 400], [300, 500], [600, 600], [790, 210], [210, 210], [700, 500], [500, 700], [500, 300], [500, 400], [500,600]]
        self.num_priority_coordinates = len(self.priority_coordinates)
        self.curr_priority_index = 0
        self.opp_moves = []

        self.last_opponent_move = None

        #v_pull = {}
        #v_pull[-1] = np.zeros((100, 100))
        #v_pull[1] = np.zeros((100, 100))

        #self.v_pull = v_pull
        #self.v_grid = np.zeros((100, 100))


        back_up_coor = []

        for i in range(750, 250, -20):
            for j in range(750, 250, -20):
                back_up_coor.append([i, j])


        for i in range(150, 250, 10):
            for j in range(750, 250 - 10):
                back_up_coor.append([i, j])

        for i in range(750, 250, -10):
            for j in range(150, 250, 10):
                back_up_coor.append([i, j])

        for i in range(750, 850, 10):
            for j in range(750, 250, -10):
                back_up_coor.append([i, j])

        for i in range(750, 250, -10):
            for j in range(850, 750, -10):
                back_up_coor.append([i, j])




        self.back_up_coordinates = back_up_coor
        self.back_up_coordinates_length = len(back_up_coor)
        self.last_back_up_index = 0


        #print("KKK", self.back_up_coordinates)

        """
        Step 1. Connect to server
        """
        self.sock.connect((host, port))

        """
        Step 2. Receive game info from server
        """
        game_state = self.__receive_game_state()
        self.num_players = game_state["num_players"]
        self.num_stone = game_state["num_stones"]
        self.player_number = game_state["player_number"]

        self.grid = [[0] * self.grid_size for i in range(self.grid_size)]
        self.moves = []  # store history of moves

        """
        Step 3. Send your name to server
        """
        self.__send({
            "player_name": self.name
        })
        print("Client initialized! Player name:", self.name)

    def __reset(self):
        self.grid = [[0] * self.grid_size for i in range(self.grid_size)]
        self.moves = []
        self.virtual_board = [[0] * int(self.virtual_dimension) for i in range(int(self.virtual_dimension))]
        self.turn = 0
        self.first = False
        self.curr_priority_index = 0
        self.last_back_up_index = 0
        self.last_opponent_move = None
        self.opp_moves = []

        #v_pull = {}
        #v_pull[-1] = np.zeros((100, 100))
        #v_pull[1] = np.zeros((100, 100))

        #self.v_pull = v_pull

    def __receive_game_state(self) -> object:
        return json.loads(self.sock.recv(4096).decode("utf-8"))

    def __send(self, obj: object):
        self.sock.sendall(json.dumps(obj).encode("utf-8"))

    def __send_move(self, move_row: int, move_col: int):
        self.__send({
            "move_row": move_row,
            "move_col": move_col
        })

    """
    Checker methods
    This is also how they are implemented server-side, so you might want to use these
    methods to double check your move
    """
    def __compute_distance(self, row1: int, col1: int, row2: int, col2: int) -> float:
        return math.sqrt((row2 - row1)**2 + (col2 - col1)**2)

    def __is_valid_move(self, move_row: int, move_col: int) -> bool:
        for move in self.moves:
            if (self.__compute_distance(move_row, move_col, move[0], move[1])) < self.min_dist:
                return False
        return True

    """
    TODO: Your algorithm goes here
    A naive random algorithm is provided as a placeholder
    """
    def __getMove(self) -> (int, int):
        move_row = 0
        move_col = 0

        self.turn += 1

        if self.first == True and self.turn == 0:
            self.curr_priority_index += 1

            return 400, 400
        '''
        else:
            move_row = self.priority_coordinates[self.curr_priority_index][0]
            move_col = self.priority_coordinates[self.curr_priority_index][1]

            while self.__is_valid_move(move_row, move_col) == False:

                #check if surrounding is open
                if self.__is_valid_move(move_row + 25, move_col):
                    self.curr_priority_index += 1
                    return move_row + 25, move_col

                elif self.__is_valid_move(move_row + 25, move_col+ 25):
                    self.curr_priority_index += 1
                    return move_row + 25, move_col + 25

                elif self.__is_valid_move(move_row, move_col + 25):
                    self.curr_priority_index += 1
                    return move_row, move_col + 25

                elif self.__is_valid_move(move_row + 25, move_col + 25):
                    self.curr_priority_index += 1
                    return move_row + 25, move_col + 25

                #all is taken, move to next
                self.curr_priority_index += 1

                if self.curr_priority_index < self.num_priority_coordinates:
                    move_row = self.priority_coordinates[self.curr_priority_index][0]
                    move_col = self.priority_coordinates[self.curr_priority_index][1]

                #priorities are gone get whichever
                if self.curr_priority_index >= self.num_priority_coordinates:
                    curr_backup = 0

                    move_row = self.back_up_coordinates[curr_backup][0]
                    move_col = self.back_up_coordinates[curr_backup][1]

                    while self.__is_valid_move(move_row, move_col) == False:
                        if curr_backup >= self.back_up_coordinates_length:
                            #give up, return whatever
                            return 500, 999

                        curr_backup += 1

                    return move_row, move_col

            self.curr_priority_index += 1
            return move_row, move_col
'''
        if self.curr_priority_index < self.num_priority_coordinates:
            if self.last_opponent_move == None or self.turn > 0:
                move_row = self.priority_coordinates[self.curr_priority_index][0]
                move_col = self.priority_coordinates[self.curr_priority_index][1]

                while self.__is_valid_move(move_row, move_col) == False:

                    # check if surrounding is open
                    if self.__is_valid_move(move_row + 25, move_col):
                        self.curr_priority_index += 1
                        return move_row + 25, move_col

                    elif self.__is_valid_move(move_row + 25, move_col + 25):
                        self.curr_priority_index += 1
                        return move_row + 25, move_col + 25

                    elif self.__is_valid_move(move_row, move_col + 25):
                        self.curr_priority_index += 1
                        return move_row, move_col + 25

                    elif self.__is_valid_move(move_row + 25, move_col + 25):
                        self.curr_priority_index += 1
                        return move_row + 25, move_col + 25

                    # all is taken, move to next
                    self.curr_priority_index += 1

                    if self.curr_priority_index < self.num_priority_coordinates:
                        move_row = self.priority_coordinates[self.curr_priority_index][0]
                        move_col = self.priority_coordinates[self.curr_priority_index][1]

                    # priorities are gone get whichever
                    if self.curr_priority_index >= self.num_priority_coordinates:
                        curr_backup = 0

                        move_row = self.back_up_coordinates[curr_backup][0]
                        move_col = self.back_up_coordinates[curr_backup][1]

                        while self.__is_valid_move(move_row, move_col) == False:
                            if curr_backup >= self.back_up_coordinates_length:
                                # give up, return whatever
                                #print("nnnnn", curr_backup, self.back_up_coordinates_length)
                                return random.randint(80, 919), random.randint(80, 919)

                            curr_backup += 1

                        return move_row, move_col




                self.curr_priority_index += 1
                return move_row, move_col
            else:
                opponent_row = self.last_opponent_move[0]
                opponent_col = self.last_opponent_move[1]

                #isaac, need your center of mass here
                #return opponent_row + 50, opponent_col + 50

                #x = self.findCenters()
                #print("SSSSSSS", x)
                #return -1, -1


        if self.last_opponent_move == None:
            # priorities are gone get whichever
            if self.curr_priority_index >= self.num_priority_coordinates:
                curr_backup = 0

                move_row = self.back_up_coordinates[curr_backup][0]
                move_col = self.back_up_coordinates[curr_backup][1]

                while self.__is_valid_move(move_row, move_col) == False:
                    if curr_backup >= self.back_up_coordinates_length:
                        # give up, return whatever
                        #print("LUU", curr_backup, self.back_up_coordinates_length)
                        return random.randint(80, 919), random.randint(80, 919)

                    curr_backup += 1

                return move_row, move_col
        else:
            opponent_row = self.last_opponent_move[0]
            opponent_col = self.last_opponent_move[1]
            #print("LLLLLLLL")

            if opponent_row < 500 and opponent_col < 500:
                if self.__is_valid_move(opponent_row + 50, opponent_col + 50):
                    return opponent_row + 50, opponent_col + 50

                if self.__is_valid_move(opponent_row + 60, opponent_col + 50):
                    return opponent_row + 60, opponent_col + 50

                if self.__is_valid_move(opponent_row + 50, opponent_col + 60):
                    return opponent_row + 50, opponent_col + 60

                if self.__is_valid_move(opponent_row + 60, opponent_col + 60):
                    return opponent_row + 60, opponent_col + 60

            if opponent_row < 500 and opponent_col > 500:
                if self.__is_valid_move(opponent_row + 50, opponent_col - 50):
                    return opponent_row + 50, opponent_col - 50

                if self.__is_valid_move(opponent_row + 60, opponent_col - 50):
                    return opponent_row + 60, opponent_col - 50

                if self.__is_valid_move(opponent_row + 50, opponent_col - 60):
                    return opponent_row + 50, opponent_col - 60

                if self.__is_valid_move(opponent_row + 60, opponent_col - 60):
                    return opponent_row + 60, opponent_col - 60


            if opponent_row > 500 and opponent_col < 500:
                if self.__is_valid_move(opponent_row - 50, opponent_col + 50):
                    return opponent_row - 50, opponent_col + 50

                if self.__is_valid_move(opponent_row - 60, opponent_col + 50):
                    return opponent_row - 60, opponent_col + 50

                if self.__is_valid_move(opponent_row - 50, opponent_col + 60):
                    return opponent_row - 50, opponent_col + 60

                if self.__is_valid_move(opponent_row - 60, opponent_col + 60):
                    return opponent_row - 60, opponent_col + 60


            if opponent_row > 500 and opponent_col > 500:
                if self.__is_valid_move(opponent_row - 50, opponent_col - 50):
                    return opponent_row - 50, opponent_col - 50

                if self.__is_valid_move(opponent_row - 60, opponent_col - 50):
                    return opponent_row - 60, opponent_col - 50

                if self.__is_valid_move(opponent_row - 50, opponent_col - 60):
                    return opponent_row - 50, opponent_col - 60

                if self.__is_valid_move(opponent_row - 60, opponent_col - 60):
                    return opponent_row - 60, opponent_col - 60

            # isaac, need your center of mass here
            #return opponent_row + 50, opponent_col + 50

            #x = self.findCenters()
            #print("SSSSSSS2222222", x)
            #return -1, - 1

            #print(",,,,,,,,")
            if self.curr_priority_index >= self.num_priority_coordinates:
                curr_backup = 0

                move_row = self.back_up_coordinates[curr_backup][0]
                move_col = self.back_up_coordinates[curr_backup][1]

                while self.__is_valid_move(move_row, move_col) == False:
                    if curr_backup >= self.back_up_coordinates_length:
                        # give up, return whatever
                        #print("LUU", curr_backup, self.back_up_coordinates_length)
                        return random.randint(80, 919), random.randint(80, 919)

                    curr_backup += 1

                return move_row, move_col



        #print("here we are")
        #absolutely no moves
        return random.randint(80, 919), random.randint(80, 919)

    """
    Main game flow
    """

    def newMove(self, p, move):

        v_x = int(move[0] / 10)
        v_y = int(move[1] / 10)
        v_move = (v_x, v_y)

        for i in range(100):
            for j in range(100):
                if (i, j) == move:
                    self.v_pull[p][i, j] = 0
                else:
                    self.v_pull[p][i, j] += 1 / self.__compute_distance(i, j, move[0], move[1]) ** 2

    def createVirtualGrid(self, new_x, new_y):
        """SHOULD BE GENERATED AFTER THE FIRST TURN"""

        # find tthe pair with the new size to generate proper boxes
        #x_pair = int(10 / new_x)
        #y_pair = int(self.grid.shape[1] / new_y)
        x_pair = 10
        y_pair = 10

        # Init a new grid
        v_grid = np.zeros((new_x, new_y))

        # Init new pull dicts

        # Move throug new grid
        for i in range(new_x):
            r = i * x_pair
            r2 = r + x_pair
            for j in range(new_y):
                c = j * y_pair
                c2 = c + y_pair

                v_grid[i, j] = -1 if np.sum(self.grid[r:r2 + 1, c:c2 + 1]) <= 0 else 1
                #v_pull[-1][i, j] = np.average(pull[-1][r:r2 + 1, c:c2 + 1])
                #v_pull[1][i, j] = np.average(pull[1][r:r2 + 1, c:c2 + 1])


        # Save results
        self.v_grid = v_grid

    def updateVirtualGrid(self, p, move):

        for i in range(100):
            for j in range(100):
                if (i, j) == move:
                    self.v_pull[p][i, j] = 0
                    self.v_grid[i, j] = p
                else:
                    new_pull = self.v_pull[p][i, j] + 1 / self.__compute_distance(i, j, move[0], move[1]) ** 2

                    if new_pull > self.v_pull[-1 * p][i, j]:
                        self.v_grid[i, j] = p
                    self.v_pull[p][i, j] += 1 / self.__compute_distance(i, j, move[0], move[1]) ** 2

    def evaluateMove(self, move):
        """CHECK HOW GOOD A MOVE IS"""
        #p = self.p
        chng = 0

        for i in range(self.v_grid.shape[0]):
            for j in range(self.v_grid.shape[1]):
                if self.v_grid[i, j] == 1:
                    continue
                if (i, j) == move:
                    if self.v_pull[-1][i, j] > self.v_pull[1][i, j]:
                        chng += 1
                        continue
                else:
                    new_pull = self.v_pull[1][i, j] + (1 /  self.__compute_distance(i, j, move[0], move[1]) ** 2)
                    if new_pull > self.v_pull[-1][i, j]:
                        chng += 1

        return chng

    def findCenters(self):
        """ITERATE THROUGH ALL CENTERS"""
        best_move, best_chng = (0, 0), 0

        #print("findCenters", self.opp_moves)

        for m1, m2 in list(combinations(self.opp_moves, r = 2)):
            #print("MMMMM", m1, m2)

            x = int(np.sqrt((m1[0] ** 2 + m2[0] ** 2) / 2))
            y = int(np.sqrt((m1[1] ** 2 + m2[1] ** 2) / 2))

            x1 = int(np.sqrt((x ** 2 + m1[0] ** 2) / 2))
            y1 = int(np.sqrt((y ** 2 + m1[1] ** 2) / 2))

            x2 = int(np.sqrt((x ** 2 + m2[0] ** 2) / 2))
            y2 = int(np.sqrt((y ** 2 + m2[1] ** 2) / 2))

            # SINCE THIS IS USING V_GRID WE ONLY NEED TO CHECK A REDUCED DISTANCE
            #if self.isLegalMove((x, y)):
            chng = self.evaluateMove((x, y))
            #if self.isLegalMove((x1, y1)):
            chng1 = self.evaluateMove((x1, y1))
            #if self.isLegalMove((x2, y2)):
            chng2 = self.evaluateMove((x2, y2))

            if chng > best_chng:
                best_chng = chng
                best_move = (x, y)
            elif chng1 > best_chng:
                best_chng = chng1
                best_move = (x1, y1)
            elif chng2 > best_chng:
                best_chng = chng
                best_move = (x2, y2)

        return best_move

    # used for checking whether a move is valid from server
    def compute_distance(self, row1: int, col1: int, row2: int, col2: int) -> float:
        return math.sqrt((row2 - row1)**2 + (col2 - col1)**2)

    def check_move(self, row, col):
        for i in self.moves:
            move_row = i[0]
            move_column = i[1]

            if (self.compute_distance(row, col, move_row, move_column < self.min_dist)):
                return False

        return True

    def mark_virtual_board(self, row, col):
        self.virtual_board_partition

        current_partition_row = int(row / self.virtual_board_partition)
        current_partition_col = int(col / self.virtual_board_partition)

        left_max_row = int((row - self.min_dist) / self.virtual_board_partition)
        right_max_row = int((row + self.min_dist) / self.virtual_board_partition)
        bottom_max_column = int((col - self.min_dist) / self.virtual_board_partition)
        top_max_column = int((col + self.min_dist) / self.virtual_board_partition)

        curr_row = left_max_row

        while (curr_row <= right_max_row):
            if (curr_row < 0 or curr_row >= self.virtual_dimension):
                curr_row += 1
                continue

            curr_col = bottom_max_column

            while (curr_col <= top_max_column):
                if (curr_col < 0 or curr_col >= self.virtual_dimension):
                    curr_col += 1
                    continue

                print(curr_row, curr_col)
                self.virtual_board[curr_row][curr_col] = 1


                curr_col += 1

            curr_row += 1

    def check_opponent_move(self, move_row, move_col):
        move_row_range = abs(500 - move_row)
        move_col_range = abs(500 - move_col)

        if (move_row_range >= 350 or move_col_range >= 350):
            self.last_opponent_move = None
            return

        self.last_opponent_move = [move_row, move_col]


    def start(self):
        for p in range(self.num_players):
            while True:


                """
                Step 4: receive game update, once received, it is now my move!
                """
                game_state = self.__receive_game_state()
                
                """
                Step 6: check if game is over...
                If so, wait for another game update which will indicate that it is your turn again
                """
                if game_state["game_over"]:
                    print("Game over")
                    # reset state
                    self.grid = [[0] * self.grid_size for i in range(self.grid_size)]
                    self.moves = []
                    self.virtual_board = [[0] * int(self.virtual_dimension) for i in range(int(self.virtual_dimension))]
                    self.turn = 0
                    self.first = False
                    self.curr_priority_index = 0
                    self.last_back_up_index = 0
                    self.last_opponent_move = None
                    self.opp_moves = []

                    #v_pull = {}
                    #v_pull[-1] = np.zeros((100, 100))
                    #v_pull[1] = np.zeros((100, 100))

                    #self.v_pull = v_pull
                    break
                
                # scores
                scores = game_state["scores"]
                # new moves
                new_moves = game_state["moves"]
                # time
                self.remaining_time = game_state["remaining_time"]
                print("I have", self.remaining_time, "to make my move.")
                print("Current Scores:", scores)
                print("My Score:", scores[self.player_number - 1])
                print("New Moves:", new_moves)
                print()

                # insert new moves into the grid
                for i in range(len(new_moves)):
                    move_row = int(new_moves[i][0])
                    move_col = int(new_moves[i][1])
                    player = int(new_moves[i][2])
                    # sanity check, this should always be true
                    if player > 0:
                        self.grid[move_row][move_col] = player
                        #self.mark_virtual_board(move_row, move_col)
                        #print("------------------------------------------------------------------------")
                        #print(self.virtual_board)
                        self.check_opponent_move(move_row, move_col)
                        #self.updateVirtualGrid(-1, (move_row, move_col))
                        #self.opp_moves.append((move_row, move_col))
                        #print("JJJJJJJ", self.opp_moves)
                        self.moves.append([move_row, move_col, player])
                    else:
                        print("Error: player info incorrect")

                """
                Step 5: make my move
                """

                if len(self.moves) == 0:
                    self.first = True

                my_move_row, my_move_col = self.__getMove()



                self.moves.append(
                    [my_move_row, my_move_col, self.player_number])
                #self.mark_virtual_board(my_move_row, my_move_col)
                #print("------------------------------------------------------------------------")
                #print(self.virtual_board)
                self.__send_move(my_move_row, my_move_col)

                #self.updateVirtualGrid(1, (my_move_row, my_move_col))

                print("Played at row {}, col {}".format(
                    my_move_row, my_move_col))
                #print()

        self.sock.close()


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]
    # note: whoever connects to the server first plays first
    client = Client(host, port, name)
    client.start()
