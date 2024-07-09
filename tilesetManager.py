import os

import pygame as pg
from pygame.math import Vector2

SW = 640
SH = 640

# These are for accessing tile datas via the id
class Tile:
	sprite = None

class TestTile(Tile):
	sprite = None

class TestTile_2(Tile):
	sprite = None

# A dictionary in a class to map the id to the classes so we can get the tile datas
class Tiles:
	tiles = {
		0: TestTile,
		1: TestTile_2
	}

# Tileset class
class Tileset:
	# Init:
	# - Tile_size in pixels
	# - Tileset is for the datas
	def __init__(self, tile_size : int = 16):
		self.tileset      = {}
		self.tile_size = tile_size
		
		self.texture_list = []

	def add_tile(self, pos     : Vector2,
					  tile_id : int):
		self.tileset[tuple(pos)] = tile_id

	# Load data from a list
	def load_list(self, data : list[list[int]]):
		for y in range(len(data)):
			for x in range(len(data[0])):
				self.tileset[(x, y)] = data[y][x]

	# Render it
	def render(self, screen : pg.Surface,
				  center : Vector2):
		for y in range(center.y - SH / self.tile_size):
			for x in range(center.x - SW / self.tile_size):
				if (x, y) not in self.tileset: continue
	
				screen.blit(Tiles.tiles[self.tileset[(x, y)]].sprite, (x * self.tile_size, y * self.tile_size))
