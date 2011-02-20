#!/usr/bin/env python
# coding=utf8

from collections import defaultdict

# interfaces
class ScoringSystem(object):
	def calculate_scores(self, games):
		"""return scores for all player
		   games is an iterable that returns all games in order.

		   a game must support a dict-like interface (iterating over
		   keys returns players any order, their values being that
		   player's points in the game. points determine win/loss/draw)"""
		raise NotImplementedError


class TallyScoring(object):
	def __init__(self, scoring_table = [10, 8, 6, 5, 4, 3, 2, 1]):
		self.scoring_table = scoring_table

	def calculate_scores(self, games):
		player_scores = defaultdict(lambda: 0)

		for game in games:
			winner_iter = iter(sorted(game.iteritems(), key = lambda t: t[1], reverse = True))
			for current_score in self.scoring_table:
				try:
					player, gamepoints = winner_iter.next()
					player_scores[player] += current_score
				except StopIteration:
					break

		return player_scores
