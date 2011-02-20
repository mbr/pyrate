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


class EloDict(defaultdict):
	def __init__(self, initial_average, *args, **kwargs):
		self.initial_average = initial_average
		super(EloDict, self).__init__(None, *args, **kwargs)

	def __missing__(self, player):
		if not self: return self.initial_average
		# calculate current average and return it
		return int(round(sum(self.values())/float(len(self))))


class EloScoring(object):
	def __init__(self, k_factors = { None: 32, 2100: 24, 2401: 12 }, initial_average = 1000, initial_scores = {}):
		self.k_factors = sorted(k_factors.iteritems()) # none gets sorted to the front, always
		self.initial_average = initial_average
		self.initial_scores = initial_scores

	def calculate_scores(self, games):
		points = EloDict(self.initial_average, )
		points.update(self.initial_scores)

		for game in games:
			(player_a, gamescore_a), (player_b, gamescore_b) = game.iteritems()

			# calculate result
			if gamescore_a > gamescore_b: result = 1.0
			elif gamescore_a < gamescore_b: result = 0.0
			else: result = 0.5

			# update points
			points[player_a], points[player_b] = self.calculate_single_match_score(points[player_a], points[player_b], result)

		return points


	def calculate_single_match_score(self, points_a, points_b, result):
		"""calculate the new elo rankings for a single match. points_a and points_b are the
		   players current ratings, result is 1.0 if player a won, 0.0 if player b won
		   and 0.5 on a draw"""
		expected = 1./(1+10**((points_b-points_a)/400.))

		# note: float conversion implicit, since expected is always a float
		return (int(round(points_a + self.get_k_factor_for(points_a) * (result - expected))),
		        int(round(points_b + self.get_k_factor_for(points_b) * (expected - result))))

	def get_k_factor_for(self, points):
		"""get the k factor for a player that has a certain amount of points"""
		# for a *lot* of k values this should be a search tree, but i really don't
		# expect that to be a common use case...
		for boundary, k_factor in self.k_factors:
			if boundary > points: break
			k = k_factor

		return k
