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
			self.kasparow: 2798.1111293179,
			self.polgar: 2584.8888706821,
		}
		result = self.points.calculate_scores([{self.kasparow: -999, self.polgar: 1123}])
		self.assertAlmostEqual(expected[self.kasparow], result[self.kasparow])
		self.assertAlmostEqual(expected[self.polgar], result[self.polgar])

	def test_elo_kasparow_win(self):
		expected = {
			self.kasparow: 2808.1111293179,
			self.polgar: 2574.8888706821,
		}
		result = self.points.calculate_scores([{self.kasparow: 13999, self.polgar: 13998}])
		self.assertAlmostEqual(expected[self.kasparow], result[self.kasparow])
		self.assertAlmostEqual(expected[self.polgar], result[self.polgar])

	def test_elo_draw_game(self):
		expected = {
			self.kasparow: 2803.1111293179,
			self.polgar: 2579.8888706821,
		}
		result = self.points.calculate_scores([{self.kasparow: -5.0, self.polgar: -5.0}])
		self.assertAlmostEqual(expected[self.kasparow], result[self.kasparow])
		self.assertAlmostEqual(expected[self.polgar], result[self.polgar])


class TestEloScoringMultiplayer(unittest.TestCase):
	def setUp(self):
		# for verification, use http://elo.divergentinformatics.com/
		self.p1 = 'Player One'
		self.p2 = 'Player Two'
		self.p3 = 'Player Three'
		self.p4 = 'Player Four'

		elos = {
			self.p1: 1392,
			self.p2: 1455,
			self.p3: 1200,
			self.p4: 1533
		}

		# [-inf, 1200): 32
		# [1200, 1500]: 24
		# (1500, inf): 12
		k_factors = { None: 32, 1200: 24, 1501: 12 }

		self.scores = EloScoring(k_factors = k_factors, initial_scores = elos)

	def test_with_one_match(self):
		game = {
			self.p1: -3, # third place
			self.p2: -1,
			self.p3: -4,
			self.p4: -2,
		}

		expected = {
			self.p1: 1381,
			self.p2: 1484,
			self.p3: 1186,
			self.p4: 1531,
		}

		points = self.scores.calculate_scores([game])

		self.assertDictEqual(expected, points)
