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
def calculate_bid(game_state, wealth, wealth_table):
    '''
    'game_state': current game state
    'wealth': your current wealth
    'wealth_table': dictionary of wealth of each player like {'player_name': wealth, ...}
                    *Notice that player_name is a string. Invalid player will have wealth of -1.*
    '''

    x = random.randrange(0, wealth)

    #if x > 19:
    #    x = 19

    return x


if __name__ == '__main__':

    ip = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3] if len(sys.argv) == 4 else 'aaaaa'

    client = Client(name, (ip, port))
    atexit.register(client.close)

    artists_num = client.artists_num
    required_count = client.required_count
    auction_items = client.auction_items
    player_count = client.player_count
    wealth_table = client.wealth_table

    current_round = 0
    wealth = 100
    while True:
        if current_round == 0:
            bid_amt = calculate_bid(None, wealth, wealth_table)
        else:
            bid_amt = calculate_bid(game_state, wealth, game_state['wealth_table'])
        client.make_bid(auction_items[current_round], bid_amt)

        # after sending bid, wait for other player
        game_state = client.receive_round()
        game_state['remain_time'] = game_state['remain_time'][name]
        if game_state['bid_winner'] == name:
            wealth -= game_state['winning_bid']
        check_game_status(game_state)

        current_round += 1
