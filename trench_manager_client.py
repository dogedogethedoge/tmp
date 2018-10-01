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
        #self.d_start = (self.d) % 100
        self.d_end = (self.d + 6 + self.L) % 100
        self.curr_turn = 0
        self.probed_turn = 0
        self.starting_turn = 1

        #unknowns
        self.sub_coming_from = 0
        self.sub_tracker = -1
        self.bait_clicked = -1
        self.in_red_zone = -1
        self.in_crit_zone = -1
        self.sub_direction = 0
        self.sub_lost = 0
        self.just_entered_crit_zone = 0



        self.fake_d = (self.d + 50) % 100
        #self.fake_d_end = (self.d_end + 50) % 100
        #self.



    def play_game(self):
        while True:
            probes_to_send = self.send_probes()
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
        """
        PLACE YOUR PROBE ALGORITHM HERE

        As the trench manager, you have access to the start of the red alert region (self.d),
        the cost for yellow alerts (self.y), the cost for red alerts (self.r), how long is
        the game (self.m), the range of the probes (self.L), and the cost to deploy a probe (self.p)

        For this function, you must return an array of integers between 0 and 99 determining the
        location you would like to send the probes
        """
        #return [randint(0,99), randint(0,99), randint(0,99)]
        if self.starting_turn:
            #self.starting_turn = 0
            i = 0 + self.L
            result = []
            while i < 100:
                #if (i + 2 * self.L < 100):
                #    result.append(i)

                result.append(i)
                i = i + 2 * self.L

            return result

        if self.in_red_zone > 0:
            if self.L == 1:
                return [self.d + 1, self.d + 3, self.d + 5]
            if self.L == 2:
                return [self.d + 2, self.d + 6]

            return [self.d]

        #if self.in_crit_zone > 0 and (abs(self.curr_turn - (self.probed_turn)) >= self.L / 2):
        if self.in_crit_zone > 0:
            return [self.d, self.d_end]

        if self.curr_turn - (self.probed_turn) >= 2 * self.L:
            self.probed_turn = self.curr_turn
            return [self.d, self.d_end]

        self.curr_turn = self.curr_turn + 1

        return []

    def choose_alert(self, sent_probes, results):
        """
        PLACE YOUR ALERT-CHOOSING ALGORITHM HERE

        This function has access to the probes you just sent and the results. They look like:

        sent_probes: [x, y, z]
        results: [True, False, False]

        This means that deploying the probe x returned True, y returned False, and z returned False

        You must return one of two options: 'red' or 'yellow'
        """


        if self.starting_turn:

            self.starting_turn = 0
            count = 0

            for probe in results:
                if probe: #true

                    range = count * 2 * self.L + self.L

                    if range >= self.d and range <= self.d + 6:
                        self.in_red_zone = 1
                        return 'red'

                    if (range) % 100 >= (self.d - self.L) % 100 and (range) % 100 <= self.d:
                        self.in_crit_zone = 1
                        self.sub_coming_from = -1

                    if (range) % 100 >= (self.d_end - 2 * self.L) % 100 and (range) % 100 <= (self.d_end) % 100:
                        self.in_crit_zone = 1
                        self.sub_coming_from = 1

                    self.sub_tracker = range

                    if (self.in_red_zone < 1 and self.in_crit_zone < 1):
                        chill_time = min(abs(range - self.d), abs(range - self.d - 6))
                        self.probed_turn = self.probed_turn + chill_time

                    return 'yellow'

                count = count + 1


            return 'yellow'

        if len(results) > 0:

            count = 0
            for probe in results:
                range = sent_probes[count]
                if probe:
                    self.in_crit_zone = 0
                    if (range) % 100 >= self.d and (range) % 100 <= self.d + 6:
                        self.in_red_zone = 1
                        return 'red'

                    if (range) % 100 >= (self.d - self.L) % 100 and (range) % 100 <= self.d:
                        self.in_crit_zone = 1
                        self.sub_coming_from = -1

                    if (range) % 100 >= (self.d_end) % 100 and (range) % 100 <= (
                            self.d_end + self.L) % 100:
                        self.in_crit_zone = 1
                        self.sub_coming_from = 1
                count = count + 1

            #self.in_crit_zone = 0
            self.in_red_zone = 0


        return 'yellow'
