#!/usr/bin/env python
# coding=utf8

import unittest2 as unittest

from pyrate.rating import *

class TestTallyRating(unittest.TestCase):
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

		rating_table = [9, 6, 3, 1]

		expected_ratings = {
			'Toad': 27,
			'Peach': 24,
			'Donkey': 6,
			'Mario': 8,
			'Wario': 9,
			'Luigi': 1
		}

		games = [race_1, race_2, race_3, race_4]

		# instantiate rating system
		rating_system = TallyRating(rating_table)

		ratings = rating_system.calculate_ratings(games)
		self.assertDictEqual(expected_ratings, dict(ratings))


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


class TestEloRatingStatic(unittest.TestCase):
	def setUp(self):
		# example from http://de.wikipedia.org/wiki/Elo-Zahl
		self.kasparow = u'Garri Kasparov'
		self.polgar = u'Zsuzsa Polgár'

		elos = {
			self.kasparow: 2806,
			self.polgar: 2577,
		}

		k_factors = {None: 10}

		self.points = EloRating(k_factors = k_factors, initial_ratings = elos)

	def test_elo_polgar_win(self):
		expected = {
			self.kasparow: 2798.1111293179,
			self.polgar: 2584.8888706821,
		}
		result = self.points.calculate_ratings([{self.kasparow: -999, self.polgar: 1123}])
		self.assertAlmostEqual(expected[self.kasparow], result[self.kasparow])
		self.assertAlmostEqual(expected[self.polgar], result[self.polgar])

	def test_elo_kasparow_win(self):
		expected = {
			self.kasparow: 2808.1111293179,
			self.polgar: 2574.8888706821,
		}
		result = self.points.calculate_ratings([{self.kasparow: 13999, self.polgar: 13998}])
		self.assertAlmostEqual(expected[self.kasparow], result[self.kasparow])
		self.assertAlmostEqual(expected[self.polgar], result[self.polgar])

	def test_elo_draw_game(self):
		expected = {
			self.kasparow: 2803.1111293179,
			self.polgar: 2579.8888706821,
		}
		result = self.points.calculate_ratings([{self.kasparow: -5.0, self.polgar: -5.0}])
		self.assertAlmostEqual(expected[self.kasparow], result[self.kasparow])
		self.assertAlmostEqual(expected[self.polgar], result[self.polgar])


class TestEloRatingMultiplayer(unittest.TestCase):
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

		self.ratings = EloRating(k_factors = k_factors, initial_ratings = elos)

	def test_with_one_match(self):
		game = {
			self.p1: -3, # third place
			self.p2: -1,
			self.p3: -4,
			self.p4: -2,
		}

		expected = {
			self.p1: 1380.74174645,
			self.p2: 1483.9915497,
			self.p3: 1186.45850528,
			self.p4: 1530.90409929,
		}

		points = self.ratings.calculate_ratings([game])

		for player in expected:
			self.assertAlmostEqual(expected[player], points[player])

class TestGlickoInternal(unittest.TestCase):
	def test_q(self):
		self.assertAlmostEqual(0.00575646273248511, GlickoRating.q)

	def test_g(self):
		RD = 65.0
		self.assertAlmostEqual(0.979377963908954, GlickoRating.g(RD))

	def test_e(self):
		self.assertAlmostEqual(0.429991057458172, GlickoRating.E(1250.0, 1300.0, 65.0))

	def test_paper_examples(self):
		r = 1500
		RD = 200

		r_j = 1400
		RD_j = 30
		expected_g = 0.9955
		decimal_places_g = 4
		expected_E = 0.639
		decimal_places_E = 3
		self.assertAlmostEqual(GlickoRating.g(RD_j), expected_g, decimal_places_g)
		self.assertAlmostEqual(GlickoRating.E(r, r_j, RD_j), expected_E, decimal_places_E)

		r_j = 1550
		RD_j = 100
		expected_g = 0.9531
		expected_E = 0.432

		self.assertAlmostEqual(GlickoRating.g(RD_j), expected_g, decimal_places_g)
		self.assertAlmostEqual(GlickoRating.E(r, r_j, RD_j), expected_E, decimal_places_E)

		r_j = 1700
		RD_j = 300
		expected_g = 0.7242
		expected_E = 0.303

		self.assertAlmostEqual(GlickoRating.g(RD_j), expected_g, decimal_places_g)
		self.assertAlmostEqual(GlickoRating.E(r, r_j, RD_j), expected_E, decimal_places_E)


class TestGlickRating(unittest.TestCase):
	def setUp(self):
		pass

	def test_c_squared_calculation(self):
		glicko = GlickoRating()
		glicko.calc_c_squared(30)

		self.assertAlmostEqual(4000.0, glicko.c_squared)

	def test_calc_current_rd(self):
		glicko = GlickoRating()
		glicko.calc_c_squared(30)

		self.assertAlmostEqual(211.896201004171, glicko.calc_current_rd(70.0, 10))
		self.assertAlmostEqual(350, glicko.calc_current_rd(70.0, 10000000))

	def test_paper_example(self):
		# example taken from paper
		glicko = GlickoRating()

		r = 1500
		rd = 200

		results = [
			(1400, 30, 1),
			(1550, 100, 0),
			(1700, 300, 0),
		]

		new_rating, new_rd = glicko.calculate_single_period_rating(r, rd, results)

		self.assertAlmostEqual(1464, new_rating, 0)
		self.assertAlmostEqual(151.4, new_rd, 1)
