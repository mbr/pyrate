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
