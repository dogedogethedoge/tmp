import json
import random
import time
import math

from clients.client import Player


class Player(Player):
    def __init__(self, name):
        super(Player, self).__init__(name=name, is_player=True)
        game_info = json.loads(self.client.receive_data())
        print('Player', game_info)
        self.n = game_info['n']
        self.weight_history = []
        self.time_left = 120
        self.candidate_history = []
        self.turn = 0
        self.change_counter = 0

        pos_num = 0
        neg_num = 0
        initial_weights = []
        pos_map = {}
        neg_map = {}


        pos_counter = 0
        neg_counter = 0




        if self.n >= 0:

            pos_dist = 10

            if self.n >= 40 and self.n < 50:
                pos_dist = 20
            elif self.n >= 50 and self.n < 100:
                pos_dist = 25
            elif self.n >= 100 and self.n < 150:
                pos_dist = 50
            elif self.n >= 150:
                pos_dist = 100

            while pos_counter < pos_dist:
                target = random.randint(0, self.n - 1)
                #print(pos_counter)
                if not target in pos_map:
                    #print("not in dic")
                    pos_map[target] = 1
                    pos_counter += 1

            print("YYYY")
            print(pos_map, pos_counter)

            while neg_counter < 10:
                target = random.randint(0, self.n - 1)

                if not target in pos_map and not target in neg_map:
                    neg_map[target] = 1
                    neg_counter += 1

            print(neg_map)

            pos_value = round(1 / pos_dist, 2)

            x = 0

            for i in range(0, self.n):
                if i in pos_map:
                    initial_weights.append(pos_value)
                    x += 1
                elif i in neg_map:
                    initial_weights.append(-.1)
                else:
                    initial_weights.append(0)

        self.neg_map = neg_map
        self.pos_map = pos_map




        print(initial_weights)

        self.initial_weights = initial_weights


        print("aaaaaaaa", self.n)
        print("game_info", game_info)

    def play_game(self):
        response = {}
        while True:
            new_weights = self.your_algorithm(0 if not response else self.candidate_history)
            print("LLLL", new_weights)
            print(json.dumps(new_weights))
            time.sleep(1)
            self.client.send_data(json.dumps(new_weights))


            self.current_weights = new_weights



            response = json.loads(self.client.receive_data(size=32368*2))

            if 'game_over' in response:
                print("######## GAME OVER ########")
                if response['match_found']:
                    print("Perfect Candidate Found :D")
                    print("Total candidates used = ", response['num_iterations'])
                else:
                    print("Sorry player :( Perfect candidate not found for you, gotta live with ",
                          response['final_score']*100, "% match... Sighhh")
                    print("Final Score of the best match = ", response['final_score'])
                exit(0)
            else:
                self.time_left = response['time_left']
                self.candidate_history.append(response['new_candidate'])
                self.weight_history = response['weight_history']

    def your_algorithm(self, candidate_history):
        """
        PLACE YOUR ALGORITHM HERE
        As the player, you have access to the number of attributes (self.n),
        the history of candidates (candidate_history)
        and clock time left (self.time_left).
        You must return an array of weights.
        The weights may be positive or negative ranging from -1 to 1 and
        specified as decimal values having at most two digits to the right of the decimal point, e.g. 0.13 but not 0.134
        Also the sum of negative weights must be -1 and the sum of positive weights must be 1.
        """


        self.turn += 1
        print("KKKKK")
        print(self.turn, candidate_history)






        #return [-.89,.89,-.11,.11] + [0 for i in range(self.n - 4)]

        if candidate_history == 0:
            return self.initial_weights

        #for hist in candidate_history:
         #   print("EEEEEEEEEEEEEEEEEEEEEEEEE")
        #    for i in hist:
         ##       print("lol")
         #       print(i)

        num_attribute_change = math.floor(.05 * self.n)

        print("OOOOOOO", len(candidate_history))

        if num_attribute_change > 1:

            curr_history = candidate_history[len(candidate_history) - 1]
            #check positive/negative

            matched_neg = []
            unmatched_neg = []



            if self.turn <= 8:

                for i in self.neg_map:
                    if curr_history[i] > .5:
                        unmatched_neg.append(i)
                    else:
                        matched_neg.append(i)


            else:
                for i in self.neg_map:
                    if curr_history[i] < .5:
                        unmatched_neg.append(i)
                    else:
                        matched_neg.append(i)

                curr_neg_change = 0
                total_change_option = int(num_attribute_change / 2)


                lower_array = min(len(unmatched_neg), len(matched_neg))

                swap_count = min(lower_array, num_attribute_change)

                unmatched_target = random.sample(set(unmatched_neg), swap_count)
                matched_target = random.sample(set(matched_neg), swap_count)



                for i in range(0, swap_count):
                    limit = round(self.initial_weights[unmatched_target[i]] * .2, 2)
                    self.current_weights[unmatched_target[i]] = round(self.initial_weights[unmatched_target[i]] + limit, 2)
                    self.current_weights[matched_target[i]] = round(self.initial_weights[matched_target[i]] - limit, 2)
















                '''
    
                if self.change_counter < self.n - 2:
                    if self.initial_weights[self.change_counter] == self.initial_weights[self.change_counter + 1] and self.initial_weights[self.change_counter] != 0:
                        #percentage = random.choice([.15, .16, .17, .18, .19, .20])
                        percentage = .2
                        limit = round(self.initial_weights[self.change_counter] * percentage, 2)
                        self.current_weights[self.change_counter] = round(self.initial_weights[self.change_counter] + limit, 2)
                        self.current_weights[self.change_counter + 1] = round(self.initial_weights[self.change_counter + 1] - limit, 2)
                    else:
                        num_attribute_change += 2
                        self.change_counter += 2
                        continue
                        
                    self.current_weights[self.change_counter]
                '''




        #start = random.choice([[1,-1],[-1,1]])
        #v1 = [-.91,.91,-.09,.09] + [0 for i in range(self.n - 4)]
        #v2 = [-.89,.89,-.11,.11] + [0 for i in range(self.n - 4)]
        #return random.choice([v2])
        return self.current_weights
        #return self.initial_weights

