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

    def test_score(self):
        pass

    def test_score_breakdown(self):
        pass


class TestMainMethod(unittest.TestCase):
    def test_main_method(self):
        pass
