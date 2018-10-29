import socket
import utils
import argparse
import random
import numpy as np
from prey import ProbabilisticPrey



HOST = '127.0.0.1'
# dedicated ports for hunter, prey

class Client:
    def __init__(self, name, port, host=HOST):
        self.name = name
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.turn_last_wall_created = 0
        self.wall_cooldown = 0
        self.last_wall_direction = 0 #1 is horizontal, 2 is vertial
        self.curr_wall_num = 0
        self.offset = -1
        self.vertical_offset = 1
        self.direction = 1 #1 = southeast, 2 = northwest, 3 = southwest, 4 = northeast
        self.vertical_direction = -1
        self.horizontal_direction = -1
        self.last_x = 0
        self.last_y = 0
        #self.

        self.prey = ProbabilisticPrey()

    def playHunter(self):
        """
        Insert the hunter move logic here
        returns [wallTypeToAdd, wallsToDelete]
        wallTypeToAdd is:
            0 for no wall
            1 for horizontal wall
            2 for vertical wall
            3 for diagnoal wall
            4 for counter diagonal wall
        wallsToDelete is a list of indices(corresponding to self.gameState['walls']) of walls to delete. Can be []
        """
        wallsToDel = []
        wallType = 0

        if self.last_x - self.gameState['hunterXPos'] < 0:
            self.horizontal_direction = -1
            #print("yyy", self.last_x, self.gameState['hunterXPos'])
        else:
            self.horizontal_direction = 1

        self.last_x = self.gameState['hunterXPos']


        #reverse due to orientation
        if self.last_y - self.gameState['hunterYPos'] < 0:
            self.vertical_direction = -1
            #print("zzz", self.last_y, self.gameState['hunterYPos'])
        else:
            self.vertical_direction = 1

        self.last_y = self.gameState['hunterYPos']

        if self.wall_cooldown > 0:
            self.wall_cooldown = self.wall_cooldown - 1
            return [0, []]


        #figure out hunter direction to improve
        if self.last_wall_direction == 0 or self.last_wall_direction == 2:
            if self.gameState['hunterYPos'] == self.gameState['preyYPos'] + (1 * self.vertical_direction):
                wallType = 1
                self.last_wall_direction = 1
                self.curr_wall_num = self.curr_wall_num + 1
                self.wall_cooldown = self.gameState['wallPlacementDelay']

        elif self.last_wall_direction == 1:
            if self.gameState['hunterXPos'] == self.gameState['preyXPos'] + (1 * self.horizontal_direction):
                wallType = 2
                self.last_wall_direction = 2
                self.curr_wall_num = self.curr_wall_num + 1
                self.wall_cooldown = self.gameState['wallPlacementDelay']

        if self.curr_wall_num > self.gameState['maxWalls'] and self.curr_wall_num > 5:
            #print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
            wallsToDel.append(0)
            self.curr_wall_num = self.curr_wall_num - 1

        return [wallType, wallsToDel]

    def playPrey(self):
        """
        Insert the prey move logic here
        return pair (moveX, moveY)
        """

        h_pos = np.array([self.gameState['hunterXPos'], self.gameState['hunterYPos']])
        p_move = self.prey.move(h_pos, self.gameState['walls'])
        return (p_move[0], p_move[1])

    def playGame(self):
        stream = ""
        while True:
            stream, line = utils.recv(self.sock, stream)
            toSend = None
            if line == "done":
                break
            elif line == "hunter":
                self.hunter = True
            elif line == "prey":
                self.hunter = False
            elif line == "sendname":
                toSend = self.name + str(self.port)
            else:
                self.gameState = utils.stringToGame(line)
                if self.hunter:
                    move = self.playHunter()
                    toSend = utils.parseHunterMove(self.gameState, move)
                else:
                    move = self.playPrey()
                    toSend = utils.parsePreyMove(self.gameState, move)
            if toSend is not None:
                print("sending: " + toSend)
                self.sock.sendall(toSend + "\n")

        print("Done", self.gameState)

if __name__== "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--port', type=int, default= 9000, help='port')
    parser.add_argument('--name', type=str, default= "randomPlayer")
    args = parser.parse_args()

    port = args.port
    name = args.name

    player = Client(name, port)
    player.playGame()
