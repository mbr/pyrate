#!/usr/bin/env python
# coding=utf8

import unittest2 as unittest

from scoring import *

class TestTallyScoring(unittest.TestCase):
	def test_mario_kart_sample_data(self):
		race_1 = {
			'Toad': -1,
			'Peach': -2,
			'Donkey': -3,
			'Mario': -4,
			'Wario': -5,
		}

		race_2 = {
			'Peach': -1,
			'Toad': -2,
			'Mario': -3,
			'Luigi': -4,
			'Wario': -5,
			'Donkey': -6, # irregular number of participants
		}

		race_3 = {
			'Wario': -1,
			'Toad': -2,
			'Mario': -3,
			# less competitors then points
		}

		race_4 = {
			'Peach': -1,
			'Toad': -2,
			'Donkey': -3,
			'Mario': -4,
			'Wario': -5,
		}

		scoring_table = [9, 6, 3, 1]

		expected_scores = {
			'Toad': 27,
			'Peach': 24,
			'Donkey': 6,
			'Mario': 8,
			'Wario': 9,
			'Luigi': 1
		}

		games = [race_1, race_2, race_3, race_4]

		# instantiate scoring system
		scoring_system = TallyScoring(scoring_table)

		scores = scoring_system.calculate_scores(games)
		self.assertDictEqual(expected_scores, dict(scores))


class TestEloDict(unittest.TestCase):
	def test_elo_dict_initial_average(self):
		e = EloDict(1000)

		self.assertEqual(e['x'], 1000)
		self.assertEqual(e['y'], 1000)

	def test_elo_dict_average(self):
		e = EloDict(1000)
		e['a'] = 3
		e['b'] = 7

		self.assertEqual(e['c'], 5)

	def test_elo_dict_average_stays_same(self):
		e = EloDict(1000)

		e['a'] = 3
		e['b'] = 7

		self.assertEqual(e['c'], 5)
		self.assertEqual(e['d'], 5)

		e['c'] = 5
		self.assertEqual(e['d'], 5)


class TestEloScoringStatic(unittest.TestCase):
	def setUp(self):
		# example from http://de.wikipedia.org/wiki/Elo-Zahl
		self.kasparow = u'Garri Kasparov'
		self.polgar = u'Zsuzsa Polgár'

		elos = {
			self.kasparow: 2806,
			self.polgar: 2577,
		}

		k_factors = {None: 10}

		self.points = EloScoring(k_factors = k_factors, initial_scores = elos)

	def test_elo_polgar_win(self):
		expected = {
			self.kasparow: 2798,
			self.polgar: 2585,
		}
		result = self.points.calculate_scores([{self.kasparow: -999, self.polgar: 1123}])
		self.assertDictEqual(expected, result)

	def test_elo_kasparov_win(self):
		expected = {
			self.kasparow: 2808,
			self.polgar: 2575,
		}
		result = self.points.calculate_scores([{self.kasparow: 13999, self.polgar: 13998}])
		self.assertDictEqual(expected, result)

	def test_elo_draw_game(self):
		expected = {
			self.kasparow: 2803,
			self.polgar: 2580,
		}
		result = self.points.calculate_scores([{self.kasparow: -5.0, self.polgar: -5.0}])
		self.assertDictEqual(expected, result)
