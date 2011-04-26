#!/usr/bin/env python
# coding=utf8

def assign_ranks_by_rating(ratings, first_rank = 1, descending = True, key = lambda t: t[1]):
	ranks = {}

	current_rank = first_rank-1
	current_group = []
	current_group_rating = None
	sorted_players = sorted(ratings.items(), key = key, reverse = descending)

	while sorted_players:
		# get next player
		player, rating = sorted_players.pop(0)

		# finished a group, add ranks
		if not rating == current_group_rating:
			current_rank += len(current_group)
			for p in current_group:
				ranks[p] = current_rank
			current_group = []

		# add player to group
		current_group.append(player)
		current_group_rating = rating

	# finalize the last group
	current_rank += len(current_group)
	for player in current_group:
		ranks[player] = current_rank

	return ranks
