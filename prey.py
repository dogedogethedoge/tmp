import numpy as np
from numpy.linalg import lstsq, norm

class ProbabilisticPrey():

    p_pos = np.array([230, 200])
    old_h_pos = np.array([0,0])
    h_pos = np.array([0,0])
    eq = np.array([0,0])
    directions = [np.array([0,0]), np.array([0,1]), np.array([1,1]),
                  np.array([1,0]), np.array([1,-1]), np.array([0,-1]),
                  np.array([-1,-1]), np.array([-1,0]), np.array([-1,0])]
    corners = [np.array([0,0]), np.array([0, 300]),
               np.array([300,0]), np.array([300, 300])]


    def __init__(self):
        return

    def move(self, new_h_pos, walls):
        self.h_pos = new_h_pos
        self.walls = walls
        pred_h_pos = self.__hunterTrajectory__()
        move =  self.__chooseMove__(pred_h_pos)
        self.old_h_pos = self.h_pos
        return move

    def __eqOfLine__(self, p1, p2):
        x_coords, y_coords = zip(*[p1, p2])
        A = np.vstack([x_coords, np.ones(len(x_coords))]).T
        return lstsq(A, y_coords, rcond=-1)[0]

    def __hunterTrajectory__(self):

        eq = self.__eqOfLine__(self.old_h_pos, self.h_pos)

        if eq[0] == 0:
            if self.old_h_pos[0] == self.h_pos[0]:
                new_pos = (self.h_pos[0], self.h_pos[1] + 2)
            else:
                new_pos = (self.h_pos[0] + 2, self.h_pos[1])
        else:
            x_move = -2 if self.h_pos[0] - self.old_h_pos[0] < 0 else 2
            y_move = -2 if self.h_pos[1] - self.old_h_pos[1] < 0 else 2
            new_pos = np.array((self.h_pos[0] + x_move, self.h_pos[1] + y_move))

        return new_pos

    def __chooseMove__(self, pred_h_pos):
        dists = np.zeros(len(self.directions))

        for i, d in enumerate(self.directions):
            if self.__goodMove__(self.p_pos + d):
                new_p_pos = self.p_pos + d
                dist =  norm(new_p_pos-pred_h_pos)
                dists[i] = 0 if dist < 4 else dist

        if dists.sum() == 0:
            choice = self.directions[int(np.random.choice(np.arange(9), size=1))]
        else:
            probs = dists/dists.sum()
            choice = self.directions[int(np.random.choice(np.arange(9), size=1, p=probs))]
        return choice

    def __goodMove__(self, move):
        if (move.any() < 0) or (move.any() > 300):
                return False

        for wall in self.walls:
                if wall[0] == 0:
                        if (wall[1] == move[1]) and (wall[2] <= move[0] <= wall[3]):
                                return False
                elif wall[0] == 1:
                        if (wall[0] == move[0]) and (wall[2] <= move[1] <= wall[3]):
                                return False
                else:
                        line = self.__eqOfLine__(np.array([wall[1], wall[3]]), np.array([wall[2], wall[4]]))
                        if ((line[0] * move[0] + line[1]) - move[1]) < 0.00001:
                                return False
        return True