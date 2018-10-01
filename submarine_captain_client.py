import json
import math
from random import randint

from clients.client_abstract_class import Player

state = {}

class SubmarineCaptain(Player):
    def __init__(self, name):
        super(SubmarineCaptain, self).__init__(name=name, is_trench_manager=False)
        game_info = json.loads(self.client.receive_data())

        self.m = game_info['m']
        self.L = game_info['L']
        self.position = game_info['pos']
        self.probed_before = 0
        self.started_in_red = 0 #not sure how to find this out yet
        self.binary_lower_bound = -1 #don't know yet
        self.binary_upper_bound = -1 #don't know yet
        self.red_alert_proximity = -1 #don't know yet
        self.initial_pos = game_info['pos']
        self.direction = 1

    def play_game(self):
        response = {}
        turns = 0
        while True:
            turns = turns + 1
            move = self.your_algorithm(0 if not response else response['times_probed'], turns)
            self.client.send_data(json.dumps({"move": move}))
            self.position += move
            response = json.loads(self.client.receive_data())
            if 'game_over' in response:
                print(f"The trench manager's final cost is: {response['trench_cost']}. " +
                      f"The safety condition {'was' if response['was_condition_achieved'] else 'was not'} satisfied.")
                exit(0)
            self.m -= 1

    def your_algorithm(self, times_probed, turns):
        """
        PLACE YOUR ALGORITHM HERE

        As the submarine captain, you only ever have access to your position (self.position),
        the amount of times you were successfully probed (times_probed), how long is the game
        (self.m), and the range of the probes(self.L).

        You must return an integer between [-1, 1]
        """

        if turns < self.L:
            if times_probed > 0:
                self.started_in_red = 1 #different logic
                return 1


        if self.started_in_red:
            #we are no longer in probe range
            if times_probed:
                self.binary_lower_bound = self.initial_pos - (3 * self.L) #3L because 2L is the total range of the probe
                self.binary_upper_bound = self.initial_pos + (3 * self.L)

            if self.binary_lower_bound > 0 and self.binary_upper_bound > 0:
	    # what about position 0 and 100???
                if self.position < self.binary_lower_bound:
                    self.direction = 1
                elif self.position > self.binary_upper_bound:
                    self.direction = -1
               
            return self.direction

        else:

            if times_probed and self.probed_before < 1:
                self.probed_before = 1
                if self.binary_lower_bound < 0:
                    self.binary_lower_bound = self.position + 3 #because L/2
                    
            elif self.probed_before > 0:
                #we are not in probe range anymore
                if self.binary_upper_bound < 0 and self.probed_before:
            	    self.binary_upper_bound = self.position + (2 * self.L)

                if self.binary_lower_bound >= 0 and self.binary_upper_bound >= 0:
                    
                    if self.position < self.binary_lower_bound:
                        self.direction = 1
                    elif self.position > self.binary_upper_bound:
                        self.direction = -1
                   
        return self.direction
