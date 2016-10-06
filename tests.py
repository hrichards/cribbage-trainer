#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from cribbage_trainer import Card
from cribbage_trainer import CardDeckMixin
from cribbage_trainer import CribbageHand
from cribbage_trainer import Deck


class TestCard(unittest.TestCase):
    def test_cant_make_nonexistent_card(self):
        with self.assertRaises(ValueError):
            Card(-1, -1)

    def test_colored_display(self):
        card = Card(CardDeckMixin.ACE, CardDeckMixin.HEARTS)
        self.assertEqual(card.colored_display, u'\x1b[31mA♥\x1b[0m')
        card = Card(CardDeckMixin.ACE, CardDeckMixin.SPADES)
        self.assertEqual(card.colored_display, u'A♠')

    def test_plaintext_display(self):
        card = Card(CardDeckMixin.ACE, CardDeckMixin.HEARTS)
        self.assertEqual(card.plaintext_display, 'A hearts')
        card = Card(CardDeckMixin.ACE, CardDeckMixin.SPADES)
        self.assertEqual(card.plaintext_display, 'A spades')


class TestDeck(unittest.TestCase):
    def test_deck_building(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        for card in deck.cards:
            self.assertTrue(isinstance(card, Card))

    def test_dealing_five_cards(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)

        hand1 = deck.deal(5)
        self.assertEqual(len(hand1), 5)
        self.assertEqual(len(deck.cards), 52 - 5)

        hand2 = deck.deal(5)
        self.assertEqual(len(hand2), 5)
        self.assertEqual(len(deck.cards), 52 - 5 - 5)

        self.assertFalse(set(deck.cards) & set(hand1) & set(hand2))


class TestCribbageHand(unittest.TestCase):
    def test_init(self):
        deck = Deck()
        too_many_cards = deck.deal(10)
        with self.assertRaises(AssertionError):
            CribbageHand(too_many_cards)

        deck = Deck()
        five_cards = deck.deal(5)
        hand = CribbageHand(five_cards)

        self.assertEqual(len(hand.fullhand), 5)
        self.assertEqual(len(hand.hand), 4)
        self.assertTrue(isinstance(hand.starter, Card))

    def test_prompt_display(self):
        pass

    def test_record_display(self):
        pass

    def test_is_run(self):
        pass

    def test_score_breakdown(self):
        pass


class TestCribbageHand(unittest.TestCase, CardDeckMixin):
    def test_pair(self):
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.ACE, self.HEARTS),
            Card(self.TWO, self.SPADES),
            Card(self.FOUR, self.SPADES),
            Card(self.SIX, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 2,
                'pairs': 2,
                'fifteens': 0,
                'runs': 0,
                'flushes': 0,
                'nobs': 0,
            }
        )

    def test_three_of_a_kind(self):
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.ACE, self.HEARTS),
            Card(self.ACE, self.DIAMONDS),
            Card(self.FOUR, self.SPADES),
            Card(self.SIX, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 6,
                'pairs': 6,
                'fifteens': 0,
                'runs': 0,
                'flushes': 0,
                'nobs': 0,
            }
        )

    def test_four_of_a_kind(self):
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.ACE, self.HEARTS),
            Card(self.ACE, self.DIAMONDS),
            Card(self.ACE, self.CLUBS),
            Card(self.SIX, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 12,
                'pairs': 12,
                'fifteens': 0,
                'runs': 0,
                'flushes': 0,
                'nobs': 0,
            }
        )

    def test_fifteens(self):
        hand = CribbageHand([
            Card(self.FIVE, self.SPADES),
            Card(self.TEN, self.HEARTS),
            Card(self.KING, self.DIAMONDS),
            Card(self.SIX, self.CLUBS),
            Card(self.NINE, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 6,
                'pairs': 0,
                'fifteens': 6,
                'runs': 0,
                'flushes': 0,
                'nobs': 0,
            }
        )

    def test_runs(self):
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.TWO, self.HEARTS),
            Card(self.THREE, self.DIAMONDS),
            Card(self.SIX, self.CLUBS),
            Card(self.SEVEN, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 5,
                'pairs': 0,
                'fifteens': 2,
                'runs': 3,
                'flushes': 0,
                'nobs': 0,
            }
        )
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.TWO, self.HEARTS),
            Card(self.THREE, self.DIAMONDS),
            Card(self.FOUR, self.CLUBS),
            Card(self.SEVEN, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 6,
                'pairs': 0,
                'fifteens': 2,
                'runs': 4,
                'flushes': 0,
                'nobs': 0,
            }
        )
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.TWO, self.HEARTS),
            Card(self.THREE, self.DIAMONDS),
            Card(self.FOUR, self.CLUBS),
            Card(self.FIVE, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 7,
                'pairs': 0,
                'fifteens': 2,
                'runs': 5,
                'flushes': 0,
                'nobs': 0,
            }
        )
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.ACE, self.HEARTS),
            Card(self.TWO, self.HEARTS),
            Card(self.THREE, self.DIAMONDS),
            Card(self.FOUR, self.CLUBS),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 10,
                'pairs': 2,
                'fifteens': 0,
                'runs': 8,
                'flushes': 0,
                'nobs': 0,
            }
        )

    def test_four_flush(self):
        hand = CribbageHand([
            Card(self.ACE, self.HEARTS),
            Card(self.THREE, self.SPADES),
            Card(self.FIVE, self.SPADES),
            Card(self.SEVEN, self.SPADES),
            Card(self.NINE, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 8,
                'pairs': 0,
                'fifteens': 4,
                'runs': 0,
                'flushes': 4,
                'nobs': 0,
            }
        )
        hand = CribbageHand([
            Card(self.THREE, self.SPADES),
            Card(self.FIVE, self.SPADES),
            Card(self.SEVEN, self.SPADES),
            Card(self.NINE, self.SPADES),
            Card(self.ACE, self.HEARTS),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 4,
                'pairs': 0,
                'fifteens': 4,
                'runs': 0,
                'flushes': 0,
                'nobs': 0,
            }
        )

    def test_five_flush(self):
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.THREE, self.SPADES),
            Card(self.FIVE, self.SPADES),
            Card(self.SEVEN, self.SPADES),
            Card(self.NINE, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 9,
                'pairs': 0,
                'fifteens': 4,
                'runs': 0,
                'flushes': 5,
                'nobs': 0,
            }
        )

    def test_nobs(self):
        hand = CribbageHand([
            Card(self.ACE, self.SPADES),
            Card(self.THREE, self.HEARTS),
            Card(self.FIVE, self.DIAMONDS),
            Card(self.SEVEN, self.CLUBS),
            Card(self.JACK, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 5,
                'pairs': 0,
                'fifteens': 4,
                'runs': 0,
                'flushes': 0,
                'nobs': 1,
            }
        )

    def test_highest_hand(self):
        hand = CribbageHand([
            Card(self.FIVE, self.SPADES),
            Card(self.FIVE, self.HEARTS),
            Card(self.FIVE, self.DIAMONDS),
            Card(self.FIVE, self.CLUBS),
            Card(self.JACK, self.SPADES),
        ])
        self.assertEqual(
            hand.score,
            {
                'score': 29,
                'pairs': 12,
                'fifteens': 16,
                'runs': 0,
                'flushes': 0,
                'nobs': 1,
            }
        )


class TestMainMethod(unittest.TestCase):
    def test_main_method(self):
        pass
