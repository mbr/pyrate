#!/usr/bin/env python
# coding=utf8

from collections import defaultdict
from itertools import combinations

# interfaces
class RatingSystem(object):
	def calculate_ratings(self, games):
		"""return ratings for all player
		   games is an iterable that returns all games in order.

		   a game must support a dict-like interface (iterating over
		   keys returns players any order, their values being that
		   player's points in the game. points determine win/loss/draw)"""
		raise NotImplementedError


class TallyRating(object):
	def __init__(self, rating_table = [10, 8, 6, 5, 4, 3, 2, 1]):
		self.rating_table = rating_table

	def calculate_ratings(self, games):
		player_ratings = defaultdict(lambda: 0)

		for game in games:
			winner_iter = iter(sorted(game.iteritems(), key = lambda t: t[1], reverse = True))
			for current_rating in self.rating_table:
				try:
					player, gamepoints = winner_iter.next()
					player_ratings[player] += current_rating
				except StopIteration:
					break

		return player_ratings


class EloDict(defaultdict):
	def __init__(self, initial_average, *args, **kwargs):
		self.initial_average = initial_average
		super(EloDict, self).__init__(None, *args, **kwargs)

	def __missing__(self, player):
		if not self: return self.initial_average
		# calculate current average and return it
		return sum(self.values())/float(len(self))


class EloRating(object):
	def __init__(self, k_factors = { None: 32, 2100: 24, 2401: 12 }, initial_average = 1000, initial_ratings = {}):
		self.k_factors = sorted(k_factors.iteritems()) # none gets sorted to the front, always
		self.initial_average = initial_average
		self.initial_ratings = initial_ratings

	def calculate_ratings(self, games):
		points = EloDict(self.initial_average, )
		points.update(self.initial_ratings)

		for game in games:
			adj = defaultdict(lambda: 0)

			# cartesian product players X players, omitting equals
			for player_a, player_b in combinations(game.keys(), 2):
				gamescore_a, gamescore_b = game[player_a], game[player_b]

				# calculate result
				if gamescore_a > gamescore_b: result = 1.0
				elif gamescore_a < gamescore_b: result = 0.0
				else: result = 0.5

				# update adjustments
				adj_a, adj_b = self.calculate_single_match_adjustment(points[player_a], points[player_b], result)
				adj[player_a] += adj_a
				adj[player_b] += adj_b

			# round values and update
			for player, val in adj.iteritems():
				points[player] += val
		return points


	def calculate_single_match_adjustment(self, points_a, points_b, result):
		"""calculate the new elo rankings for a single match. points_a and points_b are the
		   players current ratings, result is 1.0 if player a won, 0.0 if player b won
		   and 0.5 on a draw"""
		expected = 1./(1+10**((points_b-points_a)/400.))

		# note: float conversion implicit, since expected is always a float
		return (self.get_k_factor_for(points_a) * (result - expected),
		        self.get_k_factor_for(points_b) * (expected - result))

	def get_k_factor_for(self, points):
		"""get the k factor for a player that has a certain amount of points"""
		# for a *lot* of k values this should be a search tree, but i really don't
		# expect that to be a common use case...
		for boundary, k_factor in self.k_factors:
			if boundary > points: break
			k = k_factor

		return k


class GlickoRating(object):
	def calc_c_squared(self, t, typical_rd = 50):
		"""c_squared is a constant that indicates how much weight is given to inactivity. The details are found
		in [1].

		This function calculates c_squared and updates it on the instance. `t` should be the number of
		rating periods after which a players rating is as unreliable as a new players. `typical_rd` is median-ish
		RD."""
		self.c_squared = (self.initial_rd**2 - typical_rd**2)/float(t)

	def __init__(self, c_squared = 0, rd_floor = 30, initial_rating = 1500, initial_rd = 350):
		"""The glicko rating system is named after Mark E. Glickman, Ph. D. Information about it can be found at
		http://glicko.net, specifically [1], and of course in http://en.wikipedia.org/wiki/Glicko_rating_system

		The system uses "rating periods" - all games during a rating period are applied at the same time, a players
		rating can only change after a period. It is possible, however, to use a rating period of 'one game', as is
		done by the FICS (Free Internet Chess Server). In the original paper, a rating period that encompasses a
		"moderate" of games, i.e. 5-10 on average, is recommended [1].

		c_squared is a constant, see the calc_c_squared() method for details. It is recommended to call calc_c_squared()
		after instantiating this rating system.

		As suggested in [1], rd_floor is a value below rd may never fall. Otherwise a player could get 'stuck'
		at a certain rating without being able to improve upon, becaues his RD is very small.

		The initial_rating and initial_rd parameters are not normally changed, this is different from
		the ELO system.

		[1]: http://www.glicko.net/glicko/glicko.doc/glicko.html"""
		self.initial_rating = initial_rating
		self.initial_rd = initial_rd
		self.rd_floor = rd_floor
		self.c_squared = c_squared
