from collections import Counter

import numpy as np
from scipy.spatial.distance import cdist


class Teams():
    """
        Class to determine teams and centers for dancing-without-stars
        Inputs:
            dancers - Dictionary of dancer locations and colors
            colors - Int number of colors
            gen_size - Int size of ga generation
            max_iter - Int number of iterations to run
            cross_pct - Float pct of gen to get from crossover
            mut_pct - Float pct of gen to mutate
            penalty - Int penalty for overlapping centers
    """

    def __init__(self, dancers, colors, gen_size, max_iter, cross_pct, mut_pct, penalty):
        self.d_dict = dancers
        self.d_p_c = int(len(dancers) / colors)
        self.c = colors
        self.params = {"max_iter": max_iter, "gen_size": gen_size,
                       "save_k": gen_size - int(cross_pct * gen_size) if int(
                           cross_pct * gen_size) % 2 == 0 else gen_size - int(cross_pct * gen_size) - 1,
                       "cross_k": int(cross_pct * gen_size) if int(cross_pct * gen_size) % 2 == 0 else int(
                           cross_pct * gen_size) + 1,
                       "mut_k": int(mut_pct * gen_size)}
        self.penalty = penalty

    def evolve(self):
        self.gen = [self.__generateChrmsm__() for _ in range(self.params['gen_size'])]
        self.best_chrm, self.best_score = None, 1000
        countdown = 5

        for i in range(self.params['max_iter']):
            gen_score = self.__genScore__()
            if abs(gen_score.min() - self.best_score) <= 0.0001:
                if countdown == 0:
                    break
                else:
                    countdown -= 1
            else:
                countdown = 5

            if gen_score.min() < self.best_score:
                self.best_chrm = self.gen[gen_score.argmin()]
                self.best_score = gen_score.min()
            new_gen = self.__selection__(gen_score)
            new_gen += [self.gen[i] for i in gen_score.argsort()[:self.params['save_k']]]
            self.gen = new_gen
            self.__mutate__()

    def __generateChrmsm__(self):
        """
            Generate Chromosome
            Output:
                chrm - matrix of size Dancers Per Color x Colors
        """
        chrm = np.zeros((self.d_p_c, self.c))
        for i in range(self.c):
            chrm[:, i] = np.random.choice((self.d_p_c * i) + np.arange(self.d_p_c, dtype=int), self.d_p_c,
                                          replace=False)
        return chrm

    def __genScore__(self):
        """
            Score generation
            Output:
                chrm_scores - array of scores
        """
        chrm_scores = np.zeros(self.params['gen_size'])
        for c, chrm in enumerate(self.gen):
            centers = [0 for x in range(self.d_p_c)]
            scores = np.zeros(len(chrm))
            for i, team in enumerate(chrm):
                locs = np.array([[self.d_dict[t][0], self.d_dict[t][1]] for t in team])
                rot = np.array([(locs[:, 0] - locs[:, 1]) / np.sqrt(2), (locs[:, 0] + locs[:, 1]) / np.sqrt(2)])
                loc_c = (rot.max(axis=1) + rot.min(axis=1)) / 2
                center = [[(loc_c[0] + loc_c[1]) / 2, (-loc_c[0] + loc_c[1]) / 2]]
                if center in centers:
                    scores[i] = cdist(locs, center, 'cityblock').max() + self.penalty
                else:
                    scores[i] = cdist(locs, center, 'cityblock').max()
                centers[i] = center
            chrm_scores[c] = np.average(scores)

        return chrm_scores

    def __selection__(self, gen_score):
        """
            Do Crossover
            Inputs:
                gen_score - array of scores per generation
            Output:
                new_gen - array of new chromosomes with size gen_size x cross_pct
        """
        new_gen = [[] for i in range(self.params['cross_k'])]
        probs = (gen_score.max() + 1 - gen_score) / ((gen_score.max() + 1 - gen_score).sum())

        for i in range(0, len(new_gen), 2):
            p1, p2 = np.random.choice(np.arange(0, self.params['gen_size']), 2, p=probs)
            chrm1, chrm2 = self.__crossover__(self.gen[p1], self.gen[p2])
            new_gen[i] = chrm1
            new_gen[i + 1] = chrm2

        return new_gen

    def __repair__(self, chrm):
        """
            Repair crossover chromosomes
            Input:
                chrm - chromosome
            Output:
                chrm - repaired chrm
        """
        for col in range(self.c):
            num_add = np.setdiff1d((self.d_p_c * col) + np.arange(self.d_p_c), chrm[:, col])
            d = {}
            for p, j in enumerate(chrm[:, col]):
                if j in d:
                    curr_locs = np.array(
                        [[self.d_dict[t][0], self.d_dict[t][1]] for i, t in enumerate(chrm[:, col]) if i != p])
                    add_locs = np.array([[self.d_dict[t][0], self.d_dict[t][1]] for t in num_add])
                    dists = cdist(add_locs, curr_locs, 'cityblock').sum(axis=1)
                    chrm[p, col] = num_add[dists.argmin()]
                    num_add = np.delete(num_add, dists.argmin())
                else:
                    d[j] = 1
        return chrm

    def __crossover__(self, chrm1, chrm2):
        """
            Crossover then repair new chromosomes
            Input:
                chrm1 - chromosome
                chrm2 - chromosome
            Output:
                cc1 - chromosome
                cc2 - chromosome
        """
        new_chrm1 = np.zeros((self.d_p_c, self.c))
        new_chrm2 = np.zeros((self.d_p_c, self.c))
        for i in range(new_chrm1.shape[0]):
            choice = np.random.randint(2)
            new_chrm1[i, :] = chrm1[i, :] if choice == 0 else chrm2[i, :]
            new_chrm2[i, :] = chrm1[i, :] if choice == 1 else chrm2[i, :]

        cc1 = self.__repair__(new_chrm1)
        cc2 = self.__repair__(new_chrm2)

        return cc1, cc2

    def __mutate__(self):
        """
            Mutate chromosomes
        """
        mutated = np.random.choice(np.arange(self.params['gen_size'], dtype=int), self.params['mut_k'], replace=False)
        for i in mutated:
            p1, p2 = np.random.choice(np.arange(self.d_p_c), 2, replace=False)
            col = np.random.choice(self.c, 1)
            self.gen[i][p1, col], self.gen[i][p2, col] = self.gen[i][p2, col], self.gen[i][p1, col]

    def returnBest(self):
        """
            Find center for best chromosomes
            Output:
                best_chrm - best chrosome
                centers - array of centers for best chromosome
        """
        centers = [[] for i in range(self.d_p_c)]
        for i, team in enumerate(self.best_chrm):
            locs = np.array([[self.d_dict[t][0], self.d_dict[t][1]] for t in team])
            rot = np.array([(locs[:, 0] - locs[:, 1]) / np.sqrt(2), (locs[:, 0] + locs[:, 1]) / np.sqrt(2)])
            loc_c = (rot.max(axis=1) + rot.min(axis=1)) / 2
            centers[i] = [int((loc_c[0] + loc_c[1]) / 2), int((-loc_c[0] + loc_c[1]) / 2)]

        return self.best_chrm, centers

    def checkIfLegal(self, chrm):
        for col in range(self.c):
            d = {(self.d_p_c * col) + i: 0 for i in np.arange(self.d_p_c)}
            for j in chrm[:, col]:
                try:
                    d[int(j)] += 1
                except:
                    print(chrm[:, col])

            col_legal = [k for k, v in d.items() if v != 1]
            if len(col_legal) > 0:
                print("Broken")
                print("Column ", col)
                print(col_legal)
                return False
        return True