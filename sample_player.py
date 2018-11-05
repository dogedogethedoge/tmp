#!/usr/bin/python
import sys, random
from copy import deepcopy
from client import Client
from getopt import getopt, GetoptError


import math
import numpy as np
from scipy.spatial import distance_matrix
from matching.algorithms import galeshapley
from ga import Teams
from scipy.spatial.distance import cdist

"""
python3 sample_player.py -H <host> -p <port> <-c|-s>
"""
def process_file(file_data):
	"""read in input file"""
	dancers = {}
	dancer_id = -1
	f = file_data.split("\n")
	for line in f:
		print(line)
		tokens = line.split()
		if len(tokens) == 2:
			dancer_id+=1
			dancers[dancer_id] = (int(tokens[0]), int(tokens[1]), latest_color)
		elif len(tokens)>2:
			latest_color = int(tokens[-1])
	return dancers

def print_usage():
	print("Usage: python3 sample_player.py -H <host> -p <port> [-c/-s]")

def get_args():
	host = None
	port = None
	player = None
	##########################################
	#PLEASE ADD YOUR TEAM NAME#
	##########################################
	name = "MY TEAM NAME"
	##########################################
	#PLEASE ADD YOUR TEAM NAME#
	##########################################
	try:
		opts, args = getopt(sys.argv[1:], "hcsH:p:", ["help"])
	except GetoptError:
		print_usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print_usage()
			sys.exit()
		elif opt == "-H":
			host = arg
		elif opt == "-p":
			port = int(arg)
		elif opt == "-c":
			player = "c"
		elif opt == "-s":
			player = "s"
	if host is None or port is None or player is None:
		print_usage()
		sys.exit(2)
	return host, port, player, name

def get_buffer_stars(stars):
	stars_str = ""
	for s in stars:
		stars_str += (str(s[0]) + " " + str(s[1]) + " ")
	return stars_str

class Player:
	def __init__(self, board_size, num_color, k, dancers):
		self.board_size = board_size
		self.num_color = num_color
		# k dancers for each color
		self.k = k
		# self.dancers is a dictionary with key as the id of the dancers
		# with value as the tuple of 3 (x, y, c)
		# where (x,y) is initial position of dancer
		# c is the color id of the dancer
		self.dancers = dancers
		self.teams = Teams(dancers, num_color, 50, 100, 0.9, 0.1, 1)

	def get_average_manhattan_coordinate(self):
		x_total = 0
		y_total = 0
		num_dancers = 0

		for dancer in self.dancers:
			curr_dancer = self.dancers[dancer]
			x_total = curr_dancer[0] + x_total
			y_total = curr_dancer[1] + y_total
			num_dancers = num_dancers + 1

		return (int(x_total / num_dancers), int(y_total / num_dancers))

	def check_center_groupings(self):
		dancer_colors = [0] * self.num_color
		center = self.get_average_manhattan_coordinate()

		dancers_left = []
		dancers_right = []
		dancers_up = []
		dancers_down = []

		left_included = False
		right_included = False
		up_included = False
		down_included = False

		center_x = center[0]
		center_y = center[1]

		dancer_left = 0
		dancer_right = 0
		dancer_up = 0
		dancer_down = 0

		#check left
		for dancer in self.dancers:
			curr_dancer = self.dancers[dancer]

			if curr_dancer[0] <= center_x:
				dancer_colors[curr_dancer[2] - 1] = dancer_colors[curr_dancer[2] - 1] + 1
				dancers_left.append(curr_dancer)


		common_number = dancer_colors[0]
		for i in dancer_colors:
			if i != common_number:
				left_included = True
				break

		dancer_colors = [0] * self.num_color


		#check right
		for dancer in self.dancers:
			curr_dancer = self.dancers[dancer]

			if curr_dancer[0] >= center_x:
				dancer_colors[curr_dancer[2] - 1] = dancer_colors[curr_dancer[2] - 1] + 1
				dancers_right.append(curr_dancer)

		common_number = dancer_colors[0]
		for i in dancer_colors:
			if i != common_number:
				right_included = True
				break

		dancer_colors = [0] * self.num_color


		#check up
		for dancer in self.dancers:
			curr_dancer = self.dancers[dancer]

			if curr_dancer[0] >= center_y:
				dancer_colors[curr_dancer[2] - 1] = dancer_colors[curr_dancer[2] - 1] + 1
				dancers_up.append(curr_dancer)

		common_number = dancer_colors[0]
		for i in dancer_colors:
			if i != common_number:
				up_included = True
				break

		dancer_colors = [0] * self.num_color


		#check down
		for dancer in self.dancers:
			curr_dancer = self.dancers[dancer]

			if curr_dancer[0] <= center_y:
				dancer_colors[curr_dancer[2] - 1] = dancer_colors[curr_dancer[2] - 1] + 1
				dancers_down.append(curr_dancer)

		common_number = dancer_colors[0]
		for i in dancer_colors:
			if i != common_number:
				down_included = True
				break




		#print("LLLLLL", left_included, right_included, up_included, down_included)

		curr_max = 0
		curr_max_group = -1 #1 = left 2 = right 3 = up 4 = down

		CONST_LEFT_GROUP = 1
		CONST_RIGHT_GROUP = 2
		CONST_UP_GROUP = 3
		CONST_DOWN_GROUP = 4

		if left_included:
			length = len(dancers_left)
			if length > curr_max:
				curr_max = length
				curr_max_group = 1


		if right_included:
			length = len(dancers_right)
			if length > curr_max:
				curr_max = length
				curr_max_group = 2

		if up_included:
			length = len(dancers_up)
			if length > curr_max:
				curr_max = length
				curr_max_group = 3


		if down_included:
			length = len(dancers_down)
			if length > curr_max:
				curr_max = length
				curr_max_group = 4

		#print("aaaaaaaaaaaaaaaaaaaaa", curr_max, curr_max_group)


		if curr_max == 0:
			return center
		else:
			num_dancers = 0
			x_total = 0
			y_total = 0


			if curr_max_group == CONST_LEFT_GROUP:
				for i in dancers_left:
					curr_dancer = self.dancers[dancer]
					x_total = curr_dancer[0] + x_total
					y_total = curr_dancer[1] + y_total
					num_dancers = num_dancers + 1

				new_x = int(x_total / num_dancers)
				new_y = int(y_total / num_dancers)

				return (int((new_x + center[0]) / 2), int((new_y + center[1]) / 2))

			elif curr_max_group == CONST_RIGHT_GROUP:
				for i in dancers_right:
					curr_dancer = self.dancers[dancer]
					x_total = curr_dancer[0] + x_total
					y_total = curr_dancer[1] + y_total
					num_dancers = num_dancers + 1

				new_x = int(x_total / num_dancers)
				new_y = int(y_total / num_dancers)

				return (int((new_x + center[0]) / 2), int((new_y + center[1]) / 2))

			elif curr_max_group == CONST_UP_GROUP:
				for i in dancers_up:
					curr_dancer = self.dancers[dancer]
					x_total = curr_dancer[0] + x_total
					y_total = curr_dancer[1] + y_total
					num_dancers = num_dancers + 1

				new_x = int(x_total / num_dancers)
				new_y = int(y_total / num_dancers)

				return (int((new_x + center[0]) / 2), int((new_y + center[1]) / 2))

			elif curr_max_group == CONST_DOWN_GROUP:
				for i in dancers_down:
					curr_dancer = self.dancers[dancer]
					x_total = curr_dancer[0] + x_total
					y_total = curr_dancer[1] + y_total
					num_dancers = num_dancers + 1

				new_x = int(x_total / num_dancers)
				new_y = int(y_total / num_dancers)

				return (int((new_x + center[0]) / 2), int((new_y + center[1]) / 2))


	# TODO add your method here
	# Add your stars as a spoiler
	def get_stars(self):
		#
		#
		# You need to return a list of coordinates representing stars
		# Each coordinate is a tuple of 2 values (x, y)
		#
		#
		stars = []
		center = self.check_center_groupings()
		x = center[0]
		y = center[1]

		tmpx = 0
		tmpy = 0

		#print("YYY", center)

		occupied = set()
		for id in self.dancers:
			occupied.add((self.dancers[id][0], self.dancers[id][1]))


		curr_stars = 0
		min_distance = self.num_color + 1
		straight_distance_offset = min_distance
		diagonal_distance_offset = int(math.ceil((min_distance) / 2))

		#print("AAA", diagonal_distance_offset)

		if (x, y) not in occupied:
			stars.append((x, y))
			occupied.add((x, y))
			curr_stars = curr_stars + 1


		oddColor = True

		if self.num_color % 2 == 1:
			oddColor = True

		# 0, 1, 2, 3: north, east, south, west
		# 4, 5, 6, 7: NE, SE, SW, NW

		CONST_NORTH = 0
		CONST_EAST = 1
		CONST_SOUTH = 2
		CONST_WEST = 3
		CONST_NORTHEAST = 4
		CONST_SOUTHEAST = 5
		CONST_SOUTHWEST = 6
		CONST_NORTHWEST = 7

		valid_north = True
		valid_east = True
		valid_south = True
		valid_west = True
		valid_northeast = True
		valid_southeast = True
		valid_southwest = True
		valid_northwest = True

		curr_direction = 0

		'''
		if oddColor:
			while curr_stars < self.k:

				curr_direction = curr_direction % 8 # 0 to 7

				print(len(stars), stars)

				if curr_direction == CONST_NORTH and valid_north:
					tmpx = x
					tmpy = y + straight_distance_offset

					if tmpy >= self.board_size:
						valid_north = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1



				elif curr_direction == CONST_EAST and valid_east:
					tmpx = x + straight_distance_offset
					tmpy = y

					if tmpx >= self.board_size:
						valid_east = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1


				elif curr_direction == CONST_SOUTH and valid_south:
					tmpx = x
					tmpy = y - straight_distance_offset

					if tmpy < 0:
						valid_south = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1

				elif curr_direction == CONST_WEST and valid_west:
					tmpx = x - straight_distance_offset
					tmpy = y
					if tmpx < 0:
						valid_west = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1

				elif curr_direction == CONST_NORTHEAST and valid_northeast:
					tmpx = x + straight_distance_offset
					tmpy = y + straight_distance_offset

					if tmpx >= self.board_size or tmpy >= self.board_size:
						valid_northeast = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1

				elif curr_direction == CONST_SOUTHEAST and valid_southeast:
					tmpx = x + straight_distance_offset
					tmpy = y - straight_distance_offset

					if tmpx >= self.board_size or tmpy < 0:
						valid_southeast = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1

				elif curr_direction == CONST_SOUTHWEST and valid_southwest:
					tmpx = x - straight_distance_offset
					tmpy = y - straight_distance_offset

					if tmpx < 0 or tmpy < 0:
						valid_southwest = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1

				elif curr_direction == CONST_NORTHWEST and valid_northwest:
					tmpx = x - straight_distance_offset
					tmpy = y + straight_distance_offset

					if tmpx < 0 or tmpy >= self.board_size:
						valid_northwest = False
					else:
						if (tmpx, tmpy) not in occupied:
							# check manhattan distance with other stars
							ok_to_add = True

							# KEEPING THIS AS A JUST IN CASE SCENARIO
							for s in stars:
								if abs(tmpx - s[0]) + abs(tmpy - s[1]) < min_distance:
									ok_to_add = False
									break
							if ok_to_add:
								stars.append((tmpx, tmpy))
								occupied.add((tmpx, tmpy))
								curr_stars = curr_stars + 1

				if valid_north == False and valid_east == False and valid_south == False and valid_west == False and valid_northeast == False and valid_southeast == False and valid_southwest == False and valid_northwest == False:
					break;


				if curr_direction == CONST_NORTHWEST:
					straight_distance_offset = straight_distance_offset + min_distance
					diagonal_distance_offset = diagonal_distance_offset + min_distance

				curr_direction = curr_direction + 1
		'''


		horizontal_points = [x]
		vertical_points = [y]

		tmpx = x - min_distance
		tmpy = y - min_distance


		#make the order from the middle!!!

		while tmpx > 0:
			horizontal_points.append(tmpx)
			tmpx = tmpx - min_distance

		tmpx = x + min_distance

		while tmpx < self.board_size - 1:
			horizontal_points.append(tmpx)
			tmpx = tmpx + min_distance

		while tmpy > 0:
			vertical_points.append(tmpy)
			tmpy = tmpy - min_distance

		tmpy = y + min_distance

		while tmpy < self.board_size - 1:
			vertical_points.append(tmpy)
			tmpy = tmpy + min_distance


		#print("YOYOYO")
		#print(horizontal_points)

		for i in horizontal_points:
			for j in vertical_points:
				#print(i, j)
				curr_x = i
				curr_y = j

				if curr_stars >= self.k:
					break

				if (curr_x, curr_y) not in occupied:
					# check manhattan distance with other stars
					ok_to_add = True
					for s in stars:
						if abs(curr_x - s[0]) + abs(curr_y - s[1]) < self.num_color + 1:
							ok_to_add = False
							break
					if ok_to_add:
						stars.append((curr_x, curr_y))
						occupied.add((curr_x, curr_y))
						curr_stars = curr_stars + 1

		#print("FFFFOUND", curr_stars)

		#just in case if stars is not full yet, should not happen
		while curr_stars < self.k:


			for i in range(self.board_size):
				for j in range(self.board_size):
					x = i
					y = j


					if (x, y) not in occupied:
						# check manhattan distance with other stars
						ok_to_add = True
						for s in stars:
							if abs(x - s[0]) + abs(y - s[1]) < self.num_color + 1:
								ok_to_add = False
								break
						if ok_to_add:
							stars.append((x, y))
							occupied.add((x, y))
							curr_stars = curr_stars + 1

					if curr_stars >= self.k:
						#print("ZZZ222", len(stars))
						return stars




		#print("ZZZ", len(stars))
		#print(stars)

		#stars = [(25, 25)]

		#stars.append((13, 13))
		return stars

	def groupDancers(self, dancers, colors):
		# Dancers Per Color, Colors
		size = (int(len(dancers) / colors), colors)
		# Final Array
		teams = np.zeros(size, dtype=int)
		# Separate groups by color
		color_groups = [[(d[0], d[1]) for d in dancers.values() if d[2] == i] for i in range(1, size[1] + 1)]
		# Order to add colors
		order = np.random.choice(np.arange(size[1]), size[1], replace=False)

		for i in range(size[1] - 1):
			# Distance matrix for two colors
			dists = distance_matrix(color_groups[order[i]], color_groups[order[i + 1]], p=1)

			# Prefernces for the two colors - max_dist_dancer - dist_dancer
			c1_pref = {m: (np.argsort(np.max(dists[m, :]) - dists[m, :])[::-1]).tolist() for m in range(size[0])}
			c2_pref = {w: (np.argsort(np.max(dists[:, w]) - dists[:, w])[::-1]).tolist() for w in range(size[0])}

			# stable marriage algorithm
			pairs = galeshapley(c1_pref, c2_pref)

			# Add to final teams
			if i == 0:
				teams[:, order[i]] = np.array(list(pairs.keys()))
			else:
				# Order by previous input
				teams[:, order[i]] = np.array(list(pairs.values()))[teams[:, order[i - 1]]]

		# Final input
		teams[:, order[-1]] = np.array(list(pairs.values()))[teams[:, order[-2]]]

		# Fix id's
		for o in order:
			teams[:, o] += size[0] * o

		return teams


	# TODO add your method here
	# Add your moves as a choreographer
	def get_moves(self, stars):
		#
		#
		# You need to return a list of moves from the beginning to the end of the game
		# Each move is a dictionary with key as the id of the dancer you want to move
		# with value as a tuple of 2 values (x, y) representing the new position of the dancer
		#
		#

		# pick 5 random dancers from dancers

		self.teams.evolve()
		teams, centers = self.teams.returnBest()

		print("JJJJJJ", teams)
		print("JJJJJ2222", centers)
		print(len(teams))

		#return []

		xxx = []
		for i in teams:
			for z in i:
				xxx.append(z)

		print(sorted(xxx))

		min_distance = self.num_color + 1

		moves = []
		occupied = set()
		destination_map = set()
		star_set = set()

		for id in self.dancers:
			occupied.add((self.dancers[id][0], self.dancers[id][1]))
		for star in stars:
			occupied.add(star)
			destination_map.add(star)
			star_set.add(star)

		#if (x, y) not in destination_map:

		#figureout destination lines

		bad_index_list = []
		processed_centers = []
		dancer_target_location = {}

		#for i in range(len(teams)):

		testset = set()
		# try vertical
		for i in range(len(teams)):

			dancer_list = teams[i]
			team_center = centers[i]
			dancer_length = len(dancer_list)


			tmp_center = team_center
			tmp_center[1] = tmp_center[1] - int(min_distance / 2)

			currently_good = True

			for j in range(dancer_length):
				if (tmp_center[0], tmp_center[1] + j) in destination_map or tmp_center[1] + j < 0 or tmp_center[1] + j >= self.board_size:
					currently_good = False
					bad_index_list.append(i)
					break

			#it went in


			if currently_good:
				processed_centers.append(i)
				for j in range(dancer_length):
					destination_map.add((tmp_center[0], tmp_center[1] + j))
					dancer_target_location[int(dancer_list[j])] = (tmp_center[0], tmp_center[1] + j)

					if (tmp_center[0], tmp_center[1] + j) in testset:
						print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", i)
					else:
						testset.add((tmp_center[0], tmp_center[1] + j))


		#print("PPPPP", len(bad_index_list))
		#print(len(testset))
		#print(processed_centers)
		#print(bad_index_list)
		#print(len(destination_map))

		bad_index_list = []

		#vertical subtraction
		for i in range(len(teams)):

			if i in processed_centers:
				continue

			dancer_list = teams[i]
			team_center = centers[i]
			dancer_length = len(dancer_list)

			tmp_center = team_center
			tmp_center[1] = tmp_center[1] - int(min_distance / 2)

			currently_good = True

			for j in range(dancer_length):
				if (tmp_center[0], tmp_center[1] - j) in destination_map or tmp_center[1] - j < 0 or tmp_center[1] - j >= self.board_size:
					currently_good = False
					bad_index_list.append(i)
					break

			# it went in
			if currently_good:
				processed_centers.append(i)
				for j in range(dancer_length):
					destination_map.add((tmp_center[0], tmp_center[1] - j))
					dancer_target_location[int(dancer_list[j])] = (tmp_center[0], tmp_center[1] - j)

					if (tmp_center[0], tmp_center[1] - j) in testset:
						print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb2222222", i)
					else:
						testset.add((tmp_center[0], tmp_center[1] - j))

		#print("PPPPP222", len(bad_index_list))
		#print(len(testset))
		#print(len(processed_centers))
		#print(bad_index_list)
		#print(len(destination_map))

		bad_index_list = []
		#try horizontal
		for i in range(len(teams)):

			if i in processed_centers:
				continue

			dancer_list = teams[i]
			team_center = centers[i]
			dancer_length = len(dancer_list)

			tmp_center = team_center
			tmp_center[0] = tmp_center[0] - int(min_distance / 2)

			currently_good = True

			for j in range(dancer_length):
				if (tmp_center[0] + j, tmp_center[1]) in destination_map or tmp_center[0] + j < 0 or tmp_center[0] + j >= self.board_size:
					currently_good = False
					bad_index_list.append(i)
					break

			# it went in
			if currently_good:
				processed_centers.append(i)
				for j in range(dancer_length):
					destination_map.add((tmp_center[0] + j, tmp_center[1]))
					dancer_target_location[int(dancer_list[j])] = (tmp_center[0] + j, tmp_center[1])

					if (tmp_center[0] + j, tmp_center[1]) in testset:
						print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb3333333", i)
					else:
						testset.add((tmp_center[0] + j, tmp_center[1]))

		#print("PPPPP333", len(bad_index_list))
		#print(len(testset))
		#print(len(processed_centers))
		#print(bad_index_list)
		#print(len(destination_map))

		bad_index_list = []

		#try horizontal left
		for i in range(len(teams)):

			if i in processed_centers:
				continue

			dancer_list = teams[i]
			team_center = centers[i]
			dancer_length = len(dancer_list)

			tmp_center = team_center
			tmp_center[0] = tmp_center[0] - int(min_distance / 2)

			currently_good = True

			for j in range(dancer_length):
				if (tmp_center[0] - j, tmp_center[1]) in destination_map or tmp_center[0] - j < 0 or tmp_center[0] - j >= self.board_size:
					currently_good = False
					bad_index_list.append(i)
					break

			# it went in
			if currently_good:
				processed_centers.append(i)
				for j in range(dancer_length):
					destination_map.add((tmp_center[0] - j, tmp_center[1]))
					dancer_target_location[int(dancer_list[j])] = (tmp_center[0] - j, tmp_center[1])

					if (tmp_center[0] - j, tmp_center[1]) in testset:
						print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb4444", i)
					else:
						testset.add((tmp_center[0] - j, tmp_center[1]))

		#print("PPPPP444", len(bad_index_list))
		#print(len(testset))
		#print(len(processed_centers))
		#print(bad_index_list)
		#print(len(destination_map))
				#try others


		#print(dancer_target_location)
		arrx = []
		arry = []
		for d in dancer_target_location:
			arrx.append(dancer_target_location[d][0])
			arry.append(dancer_target_location[d][1])

		#print("________________aaaaa______________________")
		#print(sorted(arrx))
		#print(sorted(arry))
		#print(testset)

		# fix bad index
		#this should find the spot
		for i in bad_index_list:
			dancer_list = teams[i]
			team_center = centers[i]
			dancer_length = len(dancer_list)

			horizontal_offset = 1
			vertical_offset = 1

			#positive_horizontal_flag = True
			#positive_vertical_flag = True
			offset_stage = 1 #1, 2, 3, 4

			break_to_next = False

			while horizontal_offset < self.board_size:
				#print("eee", horizontal_offset, i)

				if break_to_next:
					break

				if offset_stage == 1:
					tmp_center = team_center
					tmp_center[0] = tmp_center[0] + horizontal_offset
					offset_stage = 2

					currently_good = True

					for j in range(dancer_length):
						if (tmp_center[0], tmp_center[1] + j) in destination_map or tmp_center[1] + j < 0 or tmp_center[
							0] + j >= self.board_size:
							currently_good = False
							# bad_index_list.append(i)
							break

					# it went in
					if currently_good:
						processed_centers.append(i)
						break_to_next = True
						for j in range(dancer_length):
							destination_map.add((tmp_center[0], tmp_center[1] + j))
							dancer_target_location[int(dancer_list[j])] = (tmp_center[0], tmp_center[1] + j)

							if (tmp_center[0], tmp_center[1] + j) in testset:
								print("cccccc", i)
							else:
								testset.add((tmp_center[0], tmp_center[1] + j))
					else:
						currently_good = True

						for j in range(dancer_length):
							if (tmp_center[0], tmp_center[1] - j) in destination_map or tmp_center[1] - j < 0 or \
									tmp_center[
										0] - j >= self.board_size:
								currently_good = False
								# bad_index_list.append(i)
								break

						# it went in
						if currently_good:
							break_to_next = True
							processed_centers.append(i)
							for j in range(dancer_length):
								destination_map.add((tmp_center[0], tmp_center[1] - j))
								dancer_target_location[int(dancer_list[j])] = (tmp_center[0], tmp_center[1] - j)

								if (tmp_center[0], tmp_center[1] - j) in testset:
									print("cccccc11111", i)
								else:
									testset.add((tmp_center[0], tmp_center[1] - j))


				elif offset_stage == 2:
					tmp_center = team_center
					tmp_center[0] = tmp_center[0] - horizontal_offset
					offset_stage = 3

					currently_good = True

					for j in range(dancer_length):
						if (tmp_center[0], tmp_center[1] + j) in destination_map or tmp_center[1] + j < 0 or tmp_center[
							0] + j >= self.board_size:
							currently_good = False
							# bad_index_list.append(i)
							break

					# it went in
					if currently_good:
						break_to_next = True
						processed_centers.append(i)
						for j in range(dancer_length):
							destination_map.add((tmp_center[0], tmp_center[1] + j))
							dancer_target_location[int(dancer_list[j])] = (tmp_center[0], tmp_center[1] + j)

							if (tmp_center[0], tmp_center[1] + j) in testset:
								print("cccccc2222222", i)
							else:
								testset.add((tmp_center[0], tmp_center[1] + j))

					else:
						currently_good = True

						for j in range(dancer_length):
							if (tmp_center[0], tmp_center[1] - j) in destination_map or tmp_center[1] - j < 0 or \
									tmp_center[
										0] - j >= self.board_size:
								currently_good = False
								# bad_index_list.append(i)
								break

						# it went in
						if currently_good:
							break_to_next = True
							processed_centers.append(i)
							for j in range(dancer_length):
								destination_map.add((tmp_center[0], tmp_center[1] - j))
								dancer_target_location[int(dancer_list[j])] = (tmp_center[0], tmp_center[1] - j)

								if (tmp_center[0], tmp_center[1] - j) in testset:
									print("cccccc3333", i)
								else:
									testset.add((tmp_center[0], tmp_center[1] - j))

				elif offset_stage == 3:
					tmp_center = team_center
					tmp_center[1] = tmp_center[1] + vertical_offset
					offset_stage = 4

					currently_good = True

					for j in range(dancer_length):
						if (tmp_center[0] + j, tmp_center[1]) in destination_map or tmp_center[0] + j < 0 or tmp_center[0] + j >= self.board_size:
							currently_good = False
							#bad_index_list.append(i)
							break

					# it went in
					if currently_good:
						break_to_next = True
						processed_centers.append(i)
						for j in range(dancer_length):
							destination_map.add((tmp_center[0] + j, tmp_center[1]))
							dancer_target_location[int(dancer_list[j])] = (tmp_center[0] + j, tmp_center[1])

							if (tmp_center[0] + j, tmp_center[1]) in testset:
								print("cccccc44444", i)
							else:
								testset.add((tmp_center[0] + j, tmp_center[1]))


					else:
						currently_good = True

						for j in range(dancer_length):
							if (tmp_center[0] - j, tmp_center[1]) in destination_map or tmp_center[0] - j < 0 or \
									tmp_center[0] - j >= self.board_size:
								currently_good = False
								# bad_index_list.append(i)
								break

						# it went in
						if currently_good:
							break_to_next = True
							processed_centers.append(i)
							for j in range(dancer_length):
								destination_map.add((tmp_center[0] - j, tmp_center[1]))
								dancer_target_location[int(dancer_list[j])] = (tmp_center[0] - j, tmp_center[1])

								if (tmp_center[0] - j, tmp_center[1]) in testset:
									print("cccccc5555", i)
								else:
									testset.add((tmp_center[0] - j, tmp_center[1]))



				elif offset_stage == 4:
					tmp_center = team_center
					tmp_center[1] = tmp_center[1] - vertical_offset
					offset_stage = 1
					horizontal_offset = horizontal_offset + 1
					vertical_offset = vertical_offset + 1

					currently_good = True

					for j in range(dancer_length):
						if (tmp_center[0] + j, tmp_center[1]) in destination_map or tmp_center[0] + j < 0 or tmp_center[
							0] + j >= self.board_size:
							currently_good = False
							# bad_index_list.append(i)
							break

					# it went in
					if currently_good:
						break_to_next = True
						processed_centers.append(i)
						for j in range(dancer_length):
							destination_map.add((tmp_center[0] + j, tmp_center[1]))
							dancer_target_location[int(dancer_list[j])] = (tmp_center[0] + j, tmp_center[1])

							if (tmp_center[0] + j, tmp_center[1]) in testset:
								print("cccccc66666", i)
							else:
								testset.add((tmp_center[0] + j, tmp_center[1]))

					else:
						currently_good = True

						for j in range(dancer_length):
							if (tmp_center[0] - j, tmp_center[1]) in destination_map or tmp_center[0] - j < 0 or \
									tmp_center[0] - j >= self.board_size:
								currently_good = False
								# bad_index_list.append(i)
								break

						# it went in
						if currently_good:
							break_to_next = True
							processed_centers.append(i)
							for j in range(dancer_length):
								destination_map.add((tmp_center[0] - j, tmp_center[1]))
								dancer_target_location[int(dancer_list[j])] = (tmp_center[0] - j, tmp_center[1])

								if (tmp_center[0] - j, tmp_center[1]) in testset:
									print("cccccc77777", i)
								else:
									testset.add((tmp_center[0] - j, tmp_center[1]))







			if horizontal_offset > self.board_size:
				print("Something went wrong, no possible winning formation")
		#move


		#print("PPPPPxxx", len(bad_index_list))
		#print(len(processed_centers))
		#print(bad_index_list)
		#print(len(destination_map))
		#print(dancer_target_location)
		#print("QQQQQ", len(testset))

		#count = 0



		not_finished_flag = True
		loop_counter = 0
		finished_set = set()

		while not_finished_flag:
			loop_counter = loop_counter + 1
			curr_move = {}

			#print("set length", len(occupied))

			backward = False


			for dancer in self.dancers:
				x, y, color = self.dancers[dancer]
				x2, y2 = dancer_target_location[dancer]
				if dancer in curr_move:
					continue
				#c = random.sample([(1, 0), (-1, 0), (0, 1), (0, -1)], 1)[0]
				#x2 = x + c[0]
				#y2 = y + c[1]

				x_distance = x2 - x
				y_distance = y2 - y

				tmp_x = x
				tmp_y = y

				#print("ORIGINAL XY", x, y)

				#visited_x = False


				if backward:
					# will try y if not in moveset already
					if y_distance != 0:

						if y_distance < 0:
							tmp_y = tmp_y - 1
						else:
							tmp_y = tmp_y + 1

						#print("rrrrrryyyyyyy", dancer, (tmp_x, tmp_y) not in star_set)

						if dancer in curr_move:
							continue

						if (tmp_x, tmp_y) not in star_set:
							# occupied will be a person

							if (tmp_x, tmp_y) in occupied:
								for p in self.dancers:
									xp, yp, colorp = self.dancers[p]

									if xp == tmp_x and yp == tmp_y:

										if p in curr_move:
											break

										curr_move[p] = (x, y)
										curr_move[dancer] = (tmp_x, tmp_y)
										self.dancers[p] = ((x, y, self.dancers[p][2]))
										self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
										break
							else:
								curr_move[dancer] = (tmp_x, tmp_y)
								self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
								occupied.remove((x, y))
								occupied.add((tmp_x, tmp_y))

						else:
							if x_distance == 0:
								tmp_y = y

								if tmp_x - 1 > 0:
									tmp_x = tmp_x - 1

									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

								elif tmp_x + 1 < self.board_size:
									tmp_x = tmp_x + 1

									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))
					tmp_x = x
					tmp_y = y

					if x_distance != 0:

						if x_distance < 0:
							tmp_x = tmp_x - 1
						else:
							tmp_x = tmp_x + 1

						#print("REEEEEEEEEEEEEEEEEE", dancer, (tmp_x, tmp_y) not in star_set)

						if dancer in curr_move:
							continue

						if (tmp_x, tmp_y) not in star_set:
							# occupied will be a person

							if (tmp_x, tmp_y) in occupied:
								for p in self.dancers:
									xp, yp, colorp = self.dancers[p]

									if xp == tmp_x and yp == tmp_y:

										if p in curr_move:
											break
										curr_move[p] = (x, y)
										curr_move[dancer] = (tmp_x, tmp_y)
										self.dancers[p] = ((x, y, self.dancers[p][2]))
										self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
										break

							else:
								curr_move[dancer] = (tmp_x, tmp_y)
								self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
								occupied.remove((x, y))
								occupied.add((tmp_x, tmp_y))
						# continue

						else:
							if y_distance == 0:
								tmp_x = x

								if tmp_y - 1 > 0:
									tmp_y = tmp_y - 1

									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

								elif tmp_y + 1 < self.board_size:
									tmp_y = tmp_y + 1
									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

					else:
						finished_set.add(dancer)
						#print("Rzzzzzzz", dancer)
						continue





				else:
					if x_distance != 0:

						if x_distance < 0:
							tmp_x = tmp_x - 1
						else:
							tmp_x = tmp_x + 1

						#print("REEEEEEEEEEEEEEEEEE", dancer, (tmp_x, tmp_y) not in star_set)

						if dancer in curr_move:
							continue

						if (tmp_x, tmp_y) not in star_set:
							# occupied will be a person

							if (tmp_x, tmp_y) in occupied:
								for p in self.dancers:
									xp, yp, colorp = self.dancers[p]

									if xp == tmp_x and yp == tmp_y:

										if p in curr_move:
											break
										curr_move[p] = (x, y)
										curr_move[dancer] = (tmp_x, tmp_y)
										self.dancers[p] = ((x, y, self.dancers[p][2]))
										self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
										break

							else:
								curr_move[dancer] = (tmp_x, tmp_y)
								self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
								occupied.remove((x, y))
								occupied.add((tmp_x, tmp_y))
						# continue

						else:
							if y_distance == 0:
								tmp_x = x

								if tmp_y - 1 > 0:
									tmp_y = tmp_y - 1

									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

								elif tmp_y + 1 < self.board_size:
									tmp_y = tmp_y + 1
									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

					tmp_x = x
					tmp_y = y
					# will try y if not in moveset already
					if y_distance != 0:

						if y_distance < 0:
							tmp_y = tmp_y - 1
						else:
							tmp_y = tmp_y + 1

						#print("rrrrrryyyyyyy", dancer, (tmp_x, tmp_y) not in star_set)

						if dancer in curr_move:
							continue

						if (tmp_x, tmp_y) not in star_set:
							# occupied will be a person

							if (tmp_x, tmp_y) in occupied:
								for p in self.dancers:
									xp, yp, colorp = self.dancers[p]

									if xp == tmp_x and yp == tmp_y:

										if p in curr_move:
											break

										curr_move[p] = (x, y)
										curr_move[dancer] = (tmp_x, tmp_y)
										self.dancers[p] = ((x, y, self.dancers[p][2]))
										self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
										break
							else:
								curr_move[dancer] = (tmp_x, tmp_y)
								self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
								occupied.remove((x, y))
								occupied.add((tmp_x, tmp_y))

						else:
							if x_distance == 0:
								tmp_y = y

								if tmp_x - 1 > 0:
									tmp_x = tmp_x - 1

									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

								elif tmp_x + 1 < self.board_size:
									tmp_x = tmp_x + 1

									if (tmp_x, tmp_y) not in star_set:
										# occupied will be a person

										if (tmp_x, tmp_y) in occupied:
											for p in self.dancers:
												xp, yp, colorp = self.dancers[p]

												if xp == tmp_x and yp == tmp_y:

													if p in curr_move:
														break

													curr_move[p] = (x, y)
													curr_move[dancer] = (tmp_x, tmp_y)
													self.dancers[p] = ((x, y, self.dancers[p][2]))
													self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
													break
										else:
											curr_move[dancer] = (tmp_x, tmp_y)
											self.dancers[dancer] = ((tmp_x, tmp_y, self.dancers[dancer][2]))
											#print("RRRRRRRRRRRRRR", occupied)
											occupied.remove((x, y))
											occupied.add((tmp_x, tmp_y))

					else:
						finished_set.add(dancer)
						#print("Rzzzzzzz", dancer)
						continue





			moves.append(curr_move)

			#check if dancers are done
			not_finished_flag = False

			#star_set




			count = 0

			for dancer in self.dancers:
				#print("WWW222", dancer)
				curr_dancer = self.dancers[dancer]
				target_dancer = dancer_target_location[dancer]
				#print(curr_dancer, target_dancer)

				if (curr_dancer[0] != target_dancer[0] or curr_dancer[1] != target_dancer[1]):
					not_finished_flag = True
					#break
				else:
					count = count + 1

			#print("FINISHED", count, len(finished_set))
			#print(len(curr_move))

			if loop_counter > 1000:
				print("STUCK IN A LOOP")				
				print("THIS SHOULD HAVE BEEN THE END RESULT")
				print(dancer_target_location)
				print("**FLIPS TABLE**")
				return []

			if backward:
				backward = False
			else:
				backward = True



		'''
						if (x2, y2) in occupied:
							continue
						if x2 not in range(self.board_size) or y2 not in range(self.board_size):
							continue
		'''
		#print("www222", count)

		#moves.append({0: (1, 2)})
		#moves.append({0: (2, 2)})
		#moves.append({0: (2, 3)})
		#moves.append({0: (3, 3), 1: (2, 3)})

		'''
		for i in range(100): # do 20 turns, each turn pick 5 random dancers
			move = {}
			count = 0
			while count < 5:
				# pick random dancers
				picked = random.sample(self.dancers.keys(), 5 - count)
				for id in picked:
					x, y, color = self.dancers[id]
					if id in move:
						continue
					c = random.sample([(1, 0), (-1, 0), (0, 1), (0, -1)], 1)[0]
					x2 = x + c[0]
					y2 = y + c[1]
					if (x2, y2) in occupied:
						continue
					if x2 not in range(self.board_size) or y2 not in range(self.board_size):
						continue
					move[id] = (x2, y2)
					self.dancers[id] = ((x2, y2, self.dancers[id][2]))
					occupied.remove((x, y))
					occupied.add((x2, y2))
					count += 1
			moves.append(move)
			
		'''

		return moves

def main():
	host, port, p, name = get_args()
	# create client
	client = Client(host, port)
	# send team name
	client.send(name)
	# receive other parameters
	parameters = client.receive()
	parameters_l = parameters.split()
	board_size = int(parameters_l[0])
	num_color = int(parameters_l[1])
	k = int(parameters_l[2]) # max num of stars
	# receive file data
	file_data = client.receive()
	# process file
	dancers = process_file(file_data) # a set of initial dancers
	__dancers = deepcopy(dancers)
	player = Player(board_size, num_color, k, dancers)
	# now start to play
	if p == "s":
		#print("Making stars")
		stars = player.get_stars()
		#print(stars)
		# send stars
		client.send(get_buffer_stars(stars))
	else: # choreographer
		# receive stars from server
		stars_str = client.receive()
		stars_str_l = stars_str.split()
		stars = []
		for i in range(int(len(stars_str_l)/2)):
			stars.append((int(stars_str_l[2*i]), int(stars_str_l[2*i+1])))

		moves = player.get_moves(stars)
		for move in moves: # iterate through all the moves
			print(move)
			move_str = str(len(move))
			for id in move: # for each dancer id in this move
				x, y, color = __dancers[id]
				nx, ny = move[id]
				move_str += " " + str(x) + " " + str(y) + " " + str(nx) + " " + str(ny)
				__dancers[id] = (nx, ny, color)

			client.send(move_str)

		# send DONE flag
		client.send("DONE")
		client.send(getLines(num_color, __dancers))

	# close connection
	client.close()

def getLines(num_color, dancers):
	nonvis = {}
	for x,y,c in dancers.values():
		nonvis[(x, y)] = c
	lines = []
	dx = [1, -1, 0, 0]
	dy = [0, 0, 1, -1]
	while True:
		if len(nonvis) == 0:
			break
		removing = set()
		endpoints = set()
		for x, y in nonvis:
			cnt = 0
			dir = -1
			for i in range(4):
				xx = x + dx[i]
				yy = y + dy[i]
				if (xx, yy) in nonvis:
					cnt += 1
					dir = i
			if cnt == 0:
				return "0 0 0 0"
			elif cnt == 1:
				nx = x + dx[dir]*(num_color-1)
				ny = y + dy[dir]*(num_color-1)
				if (nx, ny) not in endpoints and (x,y) not in endpoints:
					isGood = True
					colors = set()
					for cc in range(num_color):
						ix = x + dx[dir]*cc
						iy = y + dy[dir]*cc
						if (ix, iy) not in nonvis:
							isGood = False
						else:
							colors.add(nonvis[(ix, iy)])
					if len(colors) != num_color:
						isGood = False
					if isGood:
						endpoints.add((nx, ny))
						endpoints.add((x, y))
						lines.append((x, y, nx, ny))
						for cc in range(num_color):
							ix = x + dx[dir]*cc
							iy = y + dy[dir]*cc
							removing.add((ix, iy))
		if len(removing) == 0:
			break
		for x,y in removing:
			del nonvis[(x,y)]
	if len(lines) == 0:
		return "0 0 0 0"
	res = ""
	for line in lines:
		for coor in line:
			res += str(coor) + " "
	return res

if __name__ == "__main__":
	main()
