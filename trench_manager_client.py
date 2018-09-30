import numpy as np
import itertools
from functools import reduce

import json
from random import randint, choice

from clients.client_abstract_class import Player


class TrenchManager(Player):
    def __init__(self, name):
        super(TrenchManager, self).__init__(name=name, is_trench_manager=True)
        game_info = json.loads(self.client.receive_data())
        self.d = game_info['d']
        self.y = game_info['y']
        self.r = game_info['r']
        self.m = game_info['m']
        self.L = game_info['L']
        self.p = game_info['p']

        self.cost = 0
        self.l_cost = (self.m * self.r) + (5 * self.m * self.p)
        self.y_cost = lambda p, n: (p * self.l_cost) + ((1 - p) * (self.cost + self.y + n * self.p))
        self.r_cost = lambda n: self.cost + self.r + n * self.p

        self.first_turn = True
        self.r_zone = np.arange(self.d, self.d + 6) % 100
        self.d_zone = reduce(np.append, [np.arange(self.r_zone[0] - self.L, self.r_zone[0]), self.r_zone,
                                         np.arange(self.r_zone[-1] + 1, self.r_zone[-1] + self.L)])
        self.prob_arr = np.array([1 / 100] * 100)
        self.neighbors = np.array([np.arange(i - 1, i + 2) for i in range(100)])

        self.T = self.l_cost
        self.T_min = 2.5
        self.interval = 10

    def play_game(self):
        while True:
            print('+++++++++++++++TRENCH TURN+++++++++++++++')
            probes_to_send = self.send_probes()
            print(probes_to_send)
            self.client.send_data(json.dumps({"probes": probes_to_send}))
            response = json.loads(self.client.receive_data())
            alert = self.choose_alert(probes_to_send, response['probe_results'])
            self.client.send_data(json.dumps({"region": alert}))
            response = json.loads(self.client.receive_data())
            if 'game_over' in response:
                print(f"Your final cost is: {response['trench_cost']}. " +
                      f"The safety condition {'was' if response['was_condition_achieved'] else 'was not'} satisfied.")
                exit(0)
            self.m -= 1

    def send_probes(self):
        # Propogate probes
        if self.first_turn:
            self.first_turn = False
            return self.__first_probes__()

        self.prob_arr = 1 / 3 * np.take(self.prob_arr, self.neighbors, mode='wrap').sum(axis=1)

        if self.prob_arr[self.d_zone].sum() == 0:
            return []

        # Find best probe
        probe, probe_cost = self.__simulate_annealing__()
        self.cost += probe.shape[0] * self.p

        return probe.tolist()
        # Find cost of no probe
        # no_probe_cost = min(self.y_cost(self.prob_arr[self.r_zone].sum(), 0), self.r_cost(0))

        # print('Cost of Probes: {}'.format(probe_cost))
        # print('Cost of No Probes: {}'.format(no_probe_cost))

        # return probe or no probes
        # if probe_cost < no_probe_cost:
        #    self.cost += probe.shape[0] * self.p
        #    return probe.tolist()
        # else:
        #    return[]

    def choose_alert(self, probes, probe_mask):
        # update prob_arr with probe results

        if len(probes) > 0:
            if sum(probe_mask) > 0:
                self.prob_arr = self.__probe_success__(probes, probe_mask)
            else:
                self.prob_arr = self.__probe_failure__(probes)

        if self.y_cost(self.prob_arr[self.r_zone].sum(), 0) < self.r_cost(0):
            return 'yellow'
        else:
            return 'red'

    def fix_range(self, r):
        # fix the range for array
        r[r > 99] = r[r > 99] % 100
        r[r < 0] = 100 + r[r < 0]

        return r

    def state_space(self):
        not_zero = np.where(self.prob_arr != 0)[0]
        return [np.asarray(i) for i in np.asarray(
            list(itertools.chain.from_iterable(itertools.combinations(not_zero, r) for r in range(1, 3))))]

    def init_prob(self):
        return np.zeros(100)

    def __state_cost__(self, state):
        possibilities = np.asarray(list(itertools.product([True, False], repeat=state.shape[0])))

        total_cost = 0
        probs = 0
        info_gain = 0

        for poss in possibilities:
            if poss.sum() == 0:
                probe_ranges = np.array(
                    [self.fix_range(np.arange(probe - self.L, probe + self.L + 1)) for probe in state])
                arr = self.__probe_failure__(state)
                prob = 1 - self.prob_arr[self.fix_range(np.unique(probe_ranges.flatten()))].sum()
                total_cost += prob * min(self.y_cost(arr[self.r_zone].sum(), state.shape[0]),
                                         self.r_cost(state.shape[0]))

                info_gain += prob * np.sum(arr * np.ma.log(
                    np.divide(arr, self.prob_arr, out=np.zeros_like(arr, dtype=float),
                              where=self.prob_arr != 0)).filled(0))

            else:
                probe_ranges = np.array(
                    [self.fix_range(np.arange(probe - self.L, probe + self.L + 1)) for probe in state[poss]])
                sub_range = reduce(np.intersect1d, probe_ranges)
                arr = self.__probe_success__(state, poss)
                prob = self.prob_arr[sub_range].sum()
                total_cost += prob * min(self.y_cost(arr[self.r_zone].sum(), state.shape[0]),
                                         self.r_cost(state.shape[0]))

                info_gain += prob * np.sum(arr * np.ma.log(
                    np.divide(arr, self.prob_arr, out=np.zeros_like(arr, dtype=float),
                              where=self.prob_arr != 0)).filled(0))

            probs += prob

        info_gain = 1 if info_gain == 0 else info_gain

        return total_cost / info_gain

    def __simulate_annealing__(self):
        # define state space
        state_space = self.state_space()
        # np.random.shuffle(state_space)
        tries = len(state_space)

        # define initial state
        state = state_space.pop()
        cost = self.__state_cost__(state)

        T = cost + 1
        interval = self.interval
        break_anneal = False

        # anneal
        for i in range(tries):
            if len(state_space) <= interval:
                interval = len(state_space)
                break_anneal = True
            for it in range(interval):
                # proposed state
                prop_state = state_space.pop()
                prop_cost = self.__state_cost__(prop_state)
                # prob of change

                alpha = min(1, np.exp((cost - prop_cost) / T))
                # change state
                if (prop_cost < cost) or (np.random.uniform() < alpha):
                    state = prop_state
                    cost = prop_cost
            # adjust temp
            T = max(T * 0.8, 1.2)
            interval = int(1.2 * interval)

            if break_anneal:
                break

        return state, cost

    def __first_probes__(self):
        probe_L = (self.d + 2 - self.L) % 100
        probe_R = (self.d + 3 + self.L) % 100

        probes = [probe_L, probe_R]
        covered = self.L * 4
        while covered < 50:
            probe_L = (probe_L - 2 * self.L - 1) % 100
            probe_R = (probe_R + 2 * self.L + 1) % 100

            probes.append(probe_L)
            probes.append(probe_R)
            covered *= 2
        return probes

    def __probe_success__(self, probes, probe_mask):
        # probes to np array
        probes = np.array(probes) if type(probes) != np.ndarray else probes
        probe_mask = np.array(probe_mask) if type(probe_mask) != np.ndarray else probe_mask
        # overlapping probe range
        sub_range = reduce(np.intersect1d, np.array(
            [self.fix_range(np.arange(probe - self.L, probe + self.L + 1)) for probe in probes[probe_mask]]))

        if probe_mask.sum() != probe_mask.shape[0]:
            sub_fail_range = reduce(np.intersect1d, np.array(
                [self.fix_range(np.arange(probe - self.L, probe + self.L + 1)) for probe in probes[~probe_mask]]))
            sub_range = np.setdiff1d(sub_range, sub_fail_range)

        if (sub_range.shape[0] == 0) | (self.prob_arr[sub_range].sum() == 0):
            return self.prob_arr

        # new arr
        new_prob_arr = self.init_prob()
        # Bayes update
        new_prob_arr[sub_range] = self.prob_arr[sub_range] / self.prob_arr[sub_range].sum()

        # not in range - 0
        mask = np.ones(self.prob_arr.shape[0], bool)
        mask[sub_range] = False
        new_prob_arr[mask] = 0

        return new_prob_arr

    def __probe_failure__(self, probes):
        # probes to np array
        probes = np.array(probes) if type(probes) != np.ndarray else probes
        # overlapping probe range
        probe_ranges = np.array([self.fix_range(np.arange(probe - self.L, probe + self.L + 1)) for probe in probes])
        # unique probe range
        sub_not_range = np.unique(probe_ranges.flatten())
        # new arr
        new_prob_arr = self.init_prob()
        # mask - not in range
        mask = np.ones(self.prob_arr.shape[0], bool)
        mask[sub_not_range] = False
        # Bayes update
        if self.prob_arr[mask].sum() == 0:
            return self.prob_arr

        new_prob_arr[mask] = self.prob_arr[mask] / self.prob_arr[mask].sum()

        return new_prob_arr






