#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Presents the user with cribbage hands for scoring practice.

The user is notified if their answer is correct.  Incorrect answers return the
actual score of the hand, broken down by number of each score type (runs,
pairs, etc.).  Hands, scores, and timestamps are logged for later analysis.
"""
import itertools
import os
import random
import sys
import time
import types

HELP_CHAR = "?"
WELCOME_MESSAGE = (
    "Welcome to 'Cribbage Trainer'! ('{}' for help, 'Ctrl-C' to quit)"
    .format(HELP_CHAR))
HELP_MESSAGE = """
Deal random cribbage hand for the user to score.  At this point, the user can
either press '?' for help, or quit with Ctrl-C and the answer won't be logged.
"""

HAND_LENGTH = 5

SPADES = 'spades'
HEARTS = 'hearts'
DIAMONDS = 'diamonds'
CLUBS = 'clubs'

RED_SUITS = [HEARTS, DIAMONDS]
BLACK_SUITS = [SPADES, CLUBS]

SUITS = {
    SPADES:   u'♠',
    HEARTS:   u'♥',
    DIAMONDS: u'♦',
    CLUBS:    u'♣',
}

KING = 13
QUEEN = 12
JACK = 11
ACE = 1

RANKS = {
    KING: u'K',
    QUEEN: u'Q',
    JACK: u'J',
    10: u'T',
    9: u'9',
    8: u'8',
    7: u'7',
    6: u'6',
    5: u'5',
    4: u'4',
    3: u'3',
    2: u'2',
    ACE: u'A',
}

VALUES = {
    KING: 10,
    QUEEN: 10,
    JACK: 10,
    10: 10,
    9: 9,
    8: 8,
    7: 7,
    6: 6,
    5: 5,
    4: 4,
    3: 3,
    2: 2,
    ACE: 1,
}

# ANSI escape sequences for manipulating terminal color
RED_ESCAPE_OPEN = u'\x1b[31m'
RED_ESCAPE_CLOSE = u'\x1b[0m'

LOGFILE_NAME = os.getenv("USER") + ".cribbage.log"

CORRECT_MESSAGE = "Correct!"
INVALID_INPUT_MESSAGE = "Invalid input.  Score this hand again."
# Because user doesn't press return after ^C, must include one in this message
GOODBYE_MESSAGE = "\nGoodbye!"

SHOW_TEMPLATE = """
Actual score: {score}

Pairs       : {pairs}
Fifteens    : {fifteens}
Runs        : {runs}
Flushes     : {flushes}
Nobs        : {nobs}
"""


class Card():
    """
    One of the 52 standard playing cards.

    Cards know their suit, rank, and how to be displayed.
    """
    def __init__(self, rank, suit):
        """
        """
        if rank not in RANKS.keys() or suit not in SUITS.keys():
            raise ValueError("No such card.")

        self.rank = rank
        self.suit = suit

    @property
    def colored_print(self):
        """
        Print a color version of the hand, suitable for CLI
        """
        if self.suit in RED_SUITS:
            escaped_template = RED_ESCAPE_OPEN + "%s%s" + RED_ESCAPE_CLOSE
            return escaped_template % (RANKS[self.rank], SUITS[self.suit])
        else:
            return "%s%s" % (RANKS[self.rank], SUITS[self.suit])

    @property
    def plaintext_print(self):
        """
        Print a plaintext version of the hand, suitable for logging
        """
        return "%s %s" % (RANKS[self.rank], self.suit)

    def __str__(self):
        return self.colored_print

    def __repr__(self):
        return self.plaintext_print


class Deck():
    @staticmethod
    def draw(num_cards):
        """
        Draw a hand of length <num_cards> and return as Card objects
        """
        if num_cards < 0 or num_cards > 52:
            raise ValueError
        else:
            full_deck = list(itertools.product(RANKS.keys(), SUITS.keys()))
            return [
                Card(rank, suit)
                for rank, suit
                in random.sample(full_deck, num_cards)]


class Deal():
    """
    A collection of five cards that the user is meant to score.
    """
    def __init__(self):
        """
        Get a random hand of five cards.
        """
        self.fullhand = Deck.draw(HAND_LENGTH)
        self.hand = self.fullhand[1:]
        self.starter = self.fullhand[0]
        self.score_dict = {
            'pairs': 0,
            'fifteens': 0,
            'runs': 0,
            'flushes': 0,
            'nobs': 0,
        }

    @property
    def prompt(self):
        """ Print the cards in this deal using unicode card glyphs
        """
        color_cards = [card.colored_print for card in self.hand]
        return self.starter.colored_print + " | " + \
            ' '.join(color_cards) + ": "

    @property
    def record(self):
        """ Print the cards in this deal using plaintext
        """
        plaintext_cards = [card.plaintext_print for card in self.hand]
        return self.starter.plaintext_print + " | " + \
            ' '.join(plaintext_cards) + ": "
        return ', '.join(plaintext_cards)

    @staticmethod
    def is_run(hand):
        ranks = [card.rank for card in hand]

        ranks.sort()

        for i in range(len(ranks) - 1):
            if ranks[i + 1] - ranks[i] != 1:
                return False

        return True

    # TODO: add testing to this method
    @property
    def score(self):
        """ Score the hand in this Deal

        The following patterns are searched for:

        Pairs - 2 for 2, 6 for 3 of a kind, 12 for 4 of a kind
        Fifteens - Any combinations totalling 15 exactly - 2pts each
        Runs - consecutive cards of any suit - 3 for 3, 4 for 4, etc.
        Flush - 4 for 4 in the hand, 5 for 5
        Nobs - J of same suit as starter
        """

        twos = list(itertools.combinations(self.fullhand, 2))
        threes = list(itertools.combinations(self.fullhand, 3))
        fours = list(itertools.combinations(self.fullhand, 4))
        fives = list(itertools.combinations(self.fullhand, 5))

        # TODO: you can change this area to keep track of pairs, runs, etc for
        # method "show"
        pairs = [2 for pair in twos if pair[0].rank == pair[1].rank]

        fifteens = [2
                    for combo
                    in twos + threes + fours + fives
                    if sum([VALUES[card.rank] for card in combo]) == 15]

        runs = [len(combo) for combo in threes + fours + fives if
                Deal.is_run(combo)]

        if len(set([card.suit for card in self.fullhand])) == 1:
            flushes = [5]
        elif len(set([card.suit for card in self.hand])) == 1:
            flushes = [4]
        else:
            flushes = []

        nobs = [1
                for card
                in self.hand
                if card.rank == JACK and card.suit == self.starter.suit]

        assert sum(nobs) in [0, 1]

        score = sum(pairs + fifteens + runs + flushes + nobs)

        self.score_dict['score'] = score
        self.score_dict['pairs'] = sum(pairs)
        self.score_dict['fifteens'] = sum(fifteens)
        self.score_dict['runs'] = sum(runs)
        self.score_dict['flushes'] = sum(flushes)
        self.score_dict['nobs'] = sum(nobs)

        return score

    @property
    def show(self):
        """ Break down the score by type: runs, pairs, 15s, etc.
        """
        return SHOW_TEMPLATE.format(**self.score_dict)


def log_result(hand, score):
    """ Log the time, the hand, and user answer in user-specific logfile
    """
    with file(LOGFILE_NAME, 'a') as logfile:
        logfile.write("%f\t%s\t%s\n" % (time.time(), hand, score))


def main(args):
    """
    """
    # TODO: write docstring

    print WELCOME_MESSAGE

    repeat_flag = True

    while repeat_flag:
        # deal random hand as a sort of CLI prompt
        # prompt for the score of the hand from the user
        # at this point, the user can either press '?' for help, or quit
        # with Ctrl-C and the answer won't be logged.
        current_hand = Deal()

        user_score = ''
        while not isinstance(user_score, types.IntType):
            sys.stdout.write(current_hand.prompt)

            try:
                user_score = int(raw_input())
            except ValueError:
                if user_score == HELP_CHAR:
                    print HELP_MESSAGE
                else:
                    print INVALID_INPUT_MESSAGE
            except (KeyboardInterrupt, EOFError):
                print GOODBYE_MESSAGE
                repeat_flag = False
                break
            else:
                log_result(current_hand.record, user_score)
                if current_hand.score == user_score:
                    # if the user's input is correct, show "correct" in some
                    # kind of pleasing way
                    print CORRECT_MESSAGE
                else:
                    # if the user's input is incorrect, display the correct
                    # answer along with the breakdown of the score along each
                    # type of scorable pattern
                    print current_hand.show


if __name__ == "__main__":
    main(sys.argv)
