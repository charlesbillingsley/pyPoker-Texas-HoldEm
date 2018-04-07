import random
import sys

from holdem import Poker

# TODO fill in documentation
""" Texas Hold Em AI Poker Bot.
This module . 

Example:
    The program can be run by the following command::
        $ python 
Authors:
    Charles Billingsley
    Josh Getter
    Adam Stewart
    Josh Techentin
"""


# NOTE: Our CPU will be player 0 throughout the entire program.
debug = False  # Set to True to see the debug statements
editor_mode = False  # Set True to see loads of print statements.
number_of_players = 2
dealer = 0  # Dealer will start by default to be player 0.
game_num = 1  # Will keep track of how many games have been played so far.
player_winnings = []
knowledge = {}
ai_scores = ""

i = 0
for i in range(0, number_of_players):
    player_winnings.append(0)

poker = Poker(number_of_players, debug)
if not poker:
    sys.exit(
        "*** ERROR ***: "
        "Invalid number of players. It must be between 2 and 22."
    )


# Check for an input file
if len(sys.argv) == 2:
    # Use knowledge to play.
    with open(sys.argv[1]) as file:
        knowledge = poker.convert_knowledge_to_dict(file.read())
elif len(sys.argv) < 2:
    print("Too few arguments provided")
    print("On EOS Try: python3 main.py input.txt {targetLevel}")
    sys.exit(2)
elif len(sys.argv) > 2:
    print("Too many arguments")
    print("On EOS Try: python3 main.py input.txt {targetLevel}")
    sys.exit(2)

action = input("Editor mode on? (y/n)\n")
if action.strip().lower() == "y":
    print("Editor mode on.")
    editor_mode = True
elif action.strip().lower() != "n":
    print("I don't know what you typed, but it's off.")

# Time to play the game!
while True:
    print("Starting game #" + str(game_num) + ".  Dealer is player " + str(dealer) + ".  Entry fee is $50 per player.")
    player_statuses = {}
    i = 0
    for i in range(0, number_of_players):
        player_statuses[i] = [50, "hold"]

    highest_bid = 50

    print("1. Shuffling")
    poker.shuffle()

    print("2. Cutting")
    if not poker.cut(random.randint(1, 51)):
        # Cannot cut 0, or the number of cards in the deck
        sys.exit("*** ERROR ***: Invalid amount entered to cut the deck.")

    print("3. Distributing")
    players_hands = poker.distribute()
    if not players_hands:
        sys.exit("*** ERROR ***: Insufficient cards to distribute.")

    print("4. Hands")
    print("-----------------------")
    poker.print_all_hands(players_hands, editor_mode)

    ai_scores = str(poker.score(players_hands[0])[0])
    chances_of_winning = poker.get_winning_odds(ai_scores, knowledge)

    if editor_mode:
        print("PHASE ZERO ODDS: " + str(chances_of_winning))

    # Bidding
    highest_bid = poker.bidding(dealer, player_statuses, highest_bid, int(chances_of_winning*100), 0)


    print("-----------------------")
    # Gets and prints the community cards
    print("5. Community Cards")
    print("-----------------------")

    # Gets the flop
    card = poker.get_flop()
    if not card:
        sys.exit("*** ERROR ***: Insufficient cards to distribute.")
    community_cards = card

    # Re-print hands.
    poker.print_all_hands(players_hands, editor_mode)

    # Print community cards.
    text = "Community - "
    for card in community_cards:
        text += str(card) + "  "
    print(text)

    total = players_hands[0] + community_cards
    total.sort(key=lambda x: x.value)
    ai_scores = ai_scores +  "," + str(poker.score(total)[0])
    chances_of_winning = poker.get_winning_odds(ai_scores, knowledge)
    if editor_mode:
        print("PHASE ONE ODDS: " + str(chances_of_winning))

    # Bidding
    highest_bid = poker.bidding(dealer, player_statuses, highest_bid, int(chances_of_winning*100), 1)

    # Gets the Turn
    card = poker.get_one()
    if not card:
        sys.exit("*** ERROR ***: Insufficient cards to distribute.")
    community_cards.extend(card)

    # Re-print hands.
    poker.print_all_hands(players_hands, editor_mode)

    # Print community cards.
    text = "Community - "
    for card in community_cards:
        text += str(card) + "  "
    print(text)

    total = players_hands[0] + community_cards
    total.sort(key=lambda x: x.value)
    ai_scores = ai_scores + "," + str(poker.score(total)[0])
    chances_of_winning = poker.get_winning_odds(ai_scores, knowledge)
    if editor_mode:
        print("PHASE TWO ODDS: " + str(chances_of_winning))

    # Bidding
    highest_bid = poker.bidding(dealer, player_statuses, highest_bid, int(chances_of_winning*100), 2)

    # Gets the River
    card = poker.get_one()
    if not card:
        sys.exit("*** ERROR ***: Insufficient cards to distribute.")
    community_cards.extend(card)

    # Re-print hands.
    poker.print_all_hands(players_hands, editor_mode)

    # Print community cards.
    text = "Community - "
    for card in community_cards:
        text += str(card) + "  "
    print(text)

    total = players_hands[0] + community_cards
    total.sort(key=lambda x: x.value)
    ai_scores = ai_scores + "," + str(poker.score(total)[0])
    chances_of_winning = poker.get_winning_odds(ai_scores, knowledge)
    if editor_mode:
        print("PHASE THREE ODDS: " + str(chances_of_winning))
    temp = community_cards
    temp.sort(key=lambda x: x.value)
    if poker.score(total)[0] == poker.score(temp)[0]:
        ai_scores = ai_scores + "," + str(1)
    else:
        ai_scores = ai_scores + "," + str(0)

    chances_of_winning = poker.get_winning_odds(ai_scores, knowledge)
    if editor_mode:
        print("PHASE FOUR ODDS: " + str(chances_of_winning))

    # Bidding
    highest_bid = poker.bidding(dealer, player_statuses, highest_bid, int(chances_of_winning*100), 3)

    print("-----------------------")
    print("6. Determining Score")
    try:
        results = poker.determine_score(community_cards, players_hands)
    except:
        sys.exit("*** ERROR ***: Problem determining the score.")

    print("7. Determining Winner")
    try:
        winner = poker.determine_winner(results)
    except:
        sys.exit("*** ERROR ***: Problem determining the winner.")

    # Checks to see if the hand has ended in tie and displays the appropriate message
    tie = True
    try:
        len(winner)
    except:
        tie = False

    # Code only works for 2 players.
    p0 = player_statuses.get(0)[1]
    p1 = player_statuses.get(1)[1]

    if p0 == "fold" and p1 == "fold":
        print("There are no winners. (??)")
    elif p0 == "fold" and p1 != "fold":
        i = 0
        print("-------- Winner has Been Determined By Fold --------")
        for hand in players_hands:
            if i != 0:
                text = "Winner ** Player " + str(i) + " ** "
                player_winnings[i] += player_statuses.get((i+1) % number_of_players)[0]  # Transfer winnings.
            else:
                text = "Loser  -- Player " + str(i) + " -- "
                player_winnings[i] -= player_statuses.get(i)[0]  # Subtract losses.
            for c in hand:
                text += str(c) + "  "

            text += " --- " + poker.name_of_hand(results[i][0])
            i += 1
            print(text)
    elif p0 != "fold" and p1 == "fold":
        i = 0
        print("-------- Winner has Been Determined By Fold --------")
        for hand in players_hands:
            if i != 1:
                text = "Winner ** Player " + str(i) + " ** "
                player_winnings[i] += player_statuses.get((i+1) % number_of_players)[0]  # Transfer winnings.
            else:
                text = "Loser  -- Player " + str(i) + " -- "
                player_winnings[i] -= player_statuses.get(i)[0]  # Subtract losses.
            for c in hand:
                text += str(c) + "  "

            text += " --- " + poker.name_of_hand(results[i][0])
            i += 1
            print(text)
    elif not tie:
        counter = 0
        print("-------- Winner has Been Determined --------")
        for hand in players_hands:
            if counter == winner:
                text = "Winner ** Player " + str(counter) + " ** "
                player_winnings[counter] += player_statuses.get((counter+1) % number_of_players)[0]  # Transfer winnings.
            else:
                text = "Loser  -- Player " + str(counter) + " -- "
                player_winnings[counter] -= player_statuses.get(counter)[0]  # Subtract losses.
            for c in hand:
                text += str(c) + "  "

            text += " --- " + poker.name_of_hand(results[counter][0])
            counter += 1
            print(text)
    else:
        counter = 0
        print("--------- Tie has Been Determined --------")
        for hand in players_hands:
            if counter in winner:
                text = "Winner ** Player " + str(counter) + " ** "
                player_winnings[counter] += player_statuses.get((counter+1) % number_of_players)[0]  # Transfer winnings.
            else:
                text = "Loser  -- Player " + str(counter) + " -- "
                player_winnings[counter] -= player_statuses.get(counter)[0]  # Subtract losses.
            for c in hand:
                text += str(c) + "  "

            text += " --- " + poker.name_of_hand(results[counter][0])
            counter += 1
            print(text)
            break;

    pot = 0
    for player in player_statuses:
        pot += int(player_statuses[player][0])
    print("Pot won: $" + str(pot) + ".")

    action = input("Keep playing? (y/n)\n")
    if action.strip().lower() == "n":
        # Get total winnings.
        i = 0
        for winnings in player_winnings:
            print("Player " + str(i) + " Winnings: " + str(winnings))
            i += 1
        break
    elif action.strip().lower() != "y":
        print("I don't know what you typed, but we're just going to play again.")

    # Increment stuff.
    dealer = (dealer + 1) % number_of_players
    game_num += 1
