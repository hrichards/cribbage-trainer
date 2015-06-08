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
import time


class CardDeckMixin():
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


class Card(CardDeckMixin):
    """
    One of the 52 standard playing cards.

    Cards know their rank, suit, and how to be displayed.
    """
    # ANSI escape sequences for manipulating terminal color
    RED_ESCAPE_OPEN = u'\x1b[31m'
    RED_ESCAPE_CLOSE = u'\x1b[0m'

    def __init__(self, rank, suit):
        if rank not in self.RANKS.keys() or suit not in self.SUITS.keys():
            raise ValueError("No such card.")

        self.rank = rank
        self.suit = suit

    @property
    def colored_display(self):
        """
        Print a color version of the hand, suitable for CLI
        """
        if self.suit in self.RED_SUITS:
            escaped_template = (
                self.RED_ESCAPE_OPEN + "%s%s" + self.RED_ESCAPE_CLOSE)
            return escaped_template % (
                self.RANKS[self.rank], self.SUITS[self.suit])
        else:
            return "%s%s" % (self.RANKS[self.rank], self.SUITS[self.suit])

    @property
    def plaintext_display(self):
        """
        Print a plaintext version of the hand, suitable for logging
        """
        return "%s %s" % (self.RANKS[self.rank], self.suit)

    def __str__(self):
        return self.colored_display

    def __repr__(self):
        return self.plaintext_display


class Deck(CardDeckMixin):
    def __init__(self):
        self.cards = [
            Card(rank, suit)
            for rank, suit
            in itertools.product(self.RANKS.keys(), self.SUITS.keys())]

    def deal(self, num_cards):
        """
        Draw a hand of length <num_cards> and return as Card objects
        """
        indexes = random.sample(range(len(self.cards)), num_cards)
        dealt_cards = []
        for index in indexes:
            dealt_cards.append(self.cards.pop(index))
        return dealt_cards


class CribbageHand(CardDeckMixin):
    """
    A collection of five cards that the user is meant to score.
    """
    def __init__(self, cards):
        """
        Get a random hand of five cards.
        """
        self.fullhand = cards
        self.hand = self.fullhand[1:]
        self.starter = self.fullhand[0]

    @property
    def hand_as_prompt_display(self):
        """
        Print the cards in this deal using unicode card glyphs
        """
        return u"{starter_display} | {} {} {} {}:".format(
            *[card.colored_display for card in self.hand],
            starter_display=self.starter.colored_display)

    @property
    def hand_as_record_display(self):
        """
        Print the cards in this deal using plaintext
        """
        return u"{starter_display} | {} {} {} {}".format(
            *[card.plaintext_display for card in self.hand],
            starter_display=self.starter.plaintext_display)

    @staticmethod
    def is_run(hand):
        sorted_ranks = sorted(card.rank for card in hand)

        normed_sorted_ranks = [rank - sorted_ranks[0] for rank in sorted_ranks]

        return normed_sorted_ranks in (
            [0, 1, 2], [0, 1, 2, 3], [0, 1, 2, 3, 4])

    @property
    def score(self):
        """
        Score this hand for Cribbage

        The following patterns are searched for:

        Pairs - 2 for 2, 6 for 3 of a kind, 12 for 4 of a kind
        Fifteens - Any combinations totalling 15 exactly - 2pts each
        Runs - consecutive cards of any suit - 3 for 3, 4 for 4, etc.
        Flush - 4 for 4 in the hand, 5 for 5
        Nobs - J of same suit as starter

        The idea of the implementation is to consider all combinations of cards
        by twos, threes, fours, and fives, and exhaustively search for and
        tally matching combinations.
        """
        twos = list(itertools.combinations(self.fullhand, 2))
        threes = list(itertools.combinations(self.fullhand, 3))
        fours = list(itertools.combinations(self.fullhand, 4))
        fives = list(itertools.combinations(self.fullhand, 5))

        pairs = [2 for card1, card2 in twos if card1.rank == card2.rank]

        fifteens = [
            2 for combo in twos + threes + fours + fives
            if sum([self.VALUES[card.rank] for card in combo]) == 15]

        runs = [
            len(combo) for combo in threes + fours + fives
            if self.is_run(combo)]

        if len(set([card.suit for card in self.fullhand])) == 1:
            flushes = [5]
        elif len(set([card.suit for card in self.hand])) == 1:
            flushes = [4]
        else:
            flushes = []

        nobs = [
            1 for card in self.hand
            if card.rank == self.JACK and card.suit == self.starter.suit]

        return {
            'score': sum(pairs + fifteens + runs + flushes + nobs),
            'pairs': sum(pairs),
            'fifteens': sum(fifteens),
            'runs': sum(runs),
            'flushes': sum(flushes),
            'nobs': sum(nobs),
        }

    @property
    def score_breakdown(self):
        """
        Break down the score by type: runs, pairs, 15s, etc.
        """
        return """
        Actual score : {score}

        Pairs        : {pairs}
        Fifteens     : {fifteens}
        Runs         : {runs}
        Flushes      : {flushes}
        Nobs         : {nobs}
        """.format(**self.score)


HELP_CHAR = "?"
WELCOME_MESSAGE = (
    "Welcome to 'Cribbage Trainer'! ('{}' for help, 'Ctrl-C' to quit)"
    .format(HELP_CHAR))
HELP_MESSAGE = """
Deal random cribbage hand for the user to score.  At this point, the user can
either press '?' for help, or quit with Ctrl-C and the answer won't be logged.
"""

HAND_LENGTH = 5

CORRECT_MESSAGE = "Correct!"
INVALID_INPUT_MESSAGE = "Invalid input.  Score this hand again."
GOODBYE_MESSAGE = "Goodbye!"


def main():
    print WELCOME_MESSAGE

    current_hand = CribbageHand(Deck().deal(HAND_LENGTH))
    while True:
        print current_hand.hand_as_prompt_display,
        try:
            user_input = raw_input()
            assert user_input != HELP_MESSAGE
            user_score = int(user_input)
        except AssertionError:
            print HELP_MESSAGE
        except ValueError:
            print INVALID_INPUT_MESSAGE
        except (KeyboardInterrupt, EOFError):
            print '\n', GOODBYE_MESSAGE
            break
        else:
            with file(os.getenv("USER") + ".cribbage.log", 'a') as logfile:
                logfile.write(
                    "{time}\t{hand}\t{score}\n".format(
                        time=time.time(),
                        hand=current_hand.hand_as_record_display,
                        score=user_score
                    )
                )
            if current_hand.score['score'] == user_score:
                print CORRECT_MESSAGE
            else:
                print current_hand.score_breakdown
            current_hand = CribbageHand(Deck().deal(HAND_LENGTH))


if __name__ == "__main__":
    main()
