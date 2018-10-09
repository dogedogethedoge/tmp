import json
from random import choice
from hps.clients import SocketClient
from time import sleep
import argparse
import math
HOST = 'localhost'
PORT = 3000


class NoTippingClient(object):
    def __init__(self, name, is_first):
        self.first_resp_recv = False
        self.name = name
        self.client = SocketClient(HOST, PORT)
        self.client.send_data(json.dumps({'name': self.name, 'is_first': is_first}))
        response = json.loads(self.client.receive_data())
        self.board_length = response['board_length']
        self.num_weights = response['num_weights']
        self.magic_point = min(int(self.num_weights), min(5, math.floor(int(self.num_weights) / 2)))
        self.myWeight = dict()
        self.place_turn = 0 #self turns
        self.remove_turn = 0 #self turns

        for i in range(1, int(self.num_weights) + 1):
            self.myWeight[i] = 1

    def play_game(self):
        # pass
        response = {}
        while True:
            response = json.loads(self.client.receive_data())
            if 'game_over' in response and response['game_over'] == "1":
                print("Game Over!")
                exit(0)

            self.board_state = [int(state) for state in filter(None, list(response['board_state'].split(' ')))]

            if response['move_type'] == 'place':
                position, weight = self.place(self.board_state)
                self.client.send_data(json.dumps({"position": position, "weight": weight}))
                self.place_turn = self.place_turn + 1
            else:
                position = self.remove(self.board_state)
                self.client.send_data(json.dumps({"position": position}))
                self.remove_turn = self.remove_turn + 1
                
            
    def check_balance(self, board_state):
        left_torque = 0
        right_torque = 0

        for i in range(0, 61):
            left_torque += (i - 30 + 3) * int(self.board_state[i])
            right_torque += (i - 30 + 1) * int(self.board_state[i])
        left_torque += 3 * 3
        right_torque += 1 * 3

        return left_torque >= 0 and right_torque <= 0

    def find_place_position(self, key, board_state):
        for i in range(0, 61):
            if self.board_state[i] == 0:
                self.board_state[i] = key
                if self.check_balance(self.board_state):
                    self.board_state[i] = 0
                    return i
                self.board_state[i] = 0
        return -100

    def possible_remove_moves(self, board):
        possible_positions = []

        for i in range(0, 61):
            if self.board_state[i] != 0:
                tempWeight = self.board_state[i]
                self.board_state[i] = 0

                if self.check_balance(self.board_state):
                    possible_positions.append(i - 30)
                self.board_state[i] = tempWeight

        if len(possible_positions) == 0:
            return 1

        best_position = 100

        for i in possible_positions:
            if abs(i) < abs(best_position):
                best_position = i

        self.board_state[i + 30] = 0

        return best_position

    #returns a list from right to left of the board weights in increasing order
    def possible_moves(self, board):
        moves = []
        potential_last_move = 0
        potential_last_weight = 0

        for i in range(0, 61):
            for j in self.myWeight:
                if self.myWeight[j] == 1:
                    potential_last_weight = j

                    if self.board_state[i] == '0' or self.board_state[i] == 0:
                        potential_last_move = i
                        self.board_state[i] = j

                        if self.check_balance(self.board_state):
                            move = {}
                            move['position'] = i
                            move['weight'] = j
                            moves.append(move)

                        self.board_state[i] = 0


        last_move = {"position": potential_last_move, "weight": potential_last_weight}
        moves.append(last_move)

        return moves




    def place(self, current_board_state):
        """
        PLACE YOUR PLACING ALGORITHM HERE
        
        Inputs:
        current_board_state - array of what weight is at a given position on the board

        Output:
        position (Integer), weight (Integer)
        """
        moves = self.possible_moves(self.board_state)

        #hope this works
        if (self.place_turn == self.magic_point):
            smallest_position = 100
            largest_weight = 0

            for i in moves:
                if abs(i['position'] - 30) < smallest_position:
                    smallest_position = i['position'] - 30

            for i in moves:
                if i['position'] - 30 == smallest_position:
                    if i['weight'] > largest_weight:
                        largest_weight = i['weight']

            self.myWeight[largest_weight] = 0
            return smallest_position, largest_weight


        target_move = moves[0] #should not be empty, and already furthest right with heaviest weight

        self.myWeight[target_move['weight']] = 0

        return target_move['position'] - 30, target_move['weight']

    def remove(self, current_board_state):
        """
        PLACE YOUR REMOVING ALGORITHM HERE
        
        Inputs:
        current_board_state - array of what weight is at a given position on the board

        Output:
        position (Integer)
        """

        moves = self.possible_remove_moves(self.board_state)

        return moves

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--first', action='store_true', default=False, help='Indicates whether client should go first')
    parser.add_argument('--ip', type=str, default= 'localhost')
    parser.add_argument('--port', type=int, default= 3000)
    parser.add_argument('--name', type=str, default= "Lily")
    args = parser.parse_args()


    HOST = args.ip
    PORT = args.port

    player = NoTippingClient(args.name, args.first)
    player.play_game()













