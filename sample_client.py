import atexit

from client import Client
import time
import random
import sys

def check_game_status(state):
    if state['finished']:
        exit(0)


'''
The client will receive the following initial states from server.
    'artists_num': number of artists
    'required_count': number of items for artist to win
    'auction_items': list of auction items
    'player_count': number of players in the auction
-------------------------------------------------------------------
Then for each round, you will receive the game_state and current wealth,
game_state: 'finished': whether the game has finished
            'bid_item': auction item in last round
            'bid_winner': winner in last round (player_name(str))
            'winning_bid': winning bid in last round
            'remain_time': the time you have left
-------------------------------------------------------------------
You should return a whole number as the bid per turn.
'''
### TODO Put your bidding algorithm here
def calculate_bid(game_state, wealth, wealth_table, target, acquired):
    '''
    'game_state': current game state
    'wealth': your current wealth
    'wealth_table': dictionary of wealth of each player like {'player_name': wealth, ...}
                    *Notice that player_name is a string. Invalid player will have wealth of -1.*
    '''

    x = random.randrange(0, wealth)

    
    return x


if __name__ == '__main__':

    ip = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3] if len(sys.argv) == 4 else 'vin'

    client = Client(name, (ip, port))
    atexit.register(client.close)

    artists_num = client.artists_num
    required_count = client.required_count
    auction_items = client.auction_items
    player_count = client.player_count
    wealth_table = client.wealth_table

    item_map = {}
    item_turns = []

    target_name = ""
    second_target = ""

    for i in range(0, artists_num):
        item_map["t" + str(i)] = 0

    for item in auction_items:

        count = item_map[item]
        count += 1

        if count == required_count and target_name == "":
            target_name = item
            item_map[item] = count
            continue

        # this will be the second one


        if target_name != "" and count == required_count:
            second_target = item
            break

        item_map[item] = count



    current_round = 0
    curr_acquired = 0
    threshold_acquired = required_count - 1

    wealth = 100

    bid = int(100 / required_count)

    testing_peak = True
    test_bid_cast = False

    while True:


        if test_bid_cast == False and auction_items[current_round] == target_name and curr_acquired == 0:
            time.sleep(10)
            bid_amt = bid
            test_bid_cast = True

        if auction_items[current_round] == target_name:
            if curr_acquired == threshold_acquired:
                bid_amt = wealth

            bid_amt = bid
        else:
            bid_amt = 0

        client.make_bid(auction_items[current_round], bid_amt)

        # after sending bid, wait for other player
        game_state = client.receive_round()
        game_state['remain_time'] = game_state['remain_time'][name]


        if testing_peak and test_bid_cast:
            testing_peak = False

            if game_state['bid_winner'] != name:
                target_name = second_target

        if game_state['bid_winner'] == name:

            if testing_peak:
                testing_peak = False

            wealth -= game_state['winning_bid']
            curr_acquired += 1
        check_game_status(game_state)

        current_round += 1
