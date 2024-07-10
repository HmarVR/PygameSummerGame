import pygame as pg
import math
import time 

from player.rigidBody import RigidBody
from bindings import *

class Player(RigidBody):
    def __init__(self):
        super().__init__()
        self.elasticity = 0.3
        self.friction = 50
        self.reach = 30
        self.start_mining = None
        self.block_mining = None
        self.mining_amp = 1

    def check(self, keys):
        self.velocity[0] = 0

        if keys[bindings['left']] and keys[bindings['right']]:
            self.velocity[0] = 0

        elif keys[bindings['right']]:
            self.velocity[0] = 120

        elif keys[bindings['left']]:
            self.velocity[0] = -120

        if self.coyote_time < 0.1 and keys[bindings['jump']]:
            self.velocity[1] = -350
            self.coyote_time = 100

    def mine(self, direction, tilemap, pressed):
        if pressed:
            collided_tiles = []

            new_pos = [*self.rect.center]
            new_pos[0] += math.cos(direction) * self.reach
            new_pos[1] += math.sin(direction) * self.reach

            for tile in tilemap:
                pos = tile.split(';')
                pos[0] = 16 * int(pos[0])
                pos[1] = 16 * int(pos[1])
                
                r = pg.Rect(pos[0], pos[1], 16, 16)
                if r.clipline(self.rect.center, new_pos):
                    collided_tiles.append((tile, r))

            closest_tile = [None, float('inf')]        

            for tile, rect in collided_tiles:
                dist = math.hypot(rect.y - self.rect.y, rect.x - self.rect.x)

                if dist < closest_tile[1]:
                    closest_tile = [tile, dist]

            del collided_tiles

            if tilemap[tile][1]:
                if self.block_mining != tile:
                    self.start_mining = time.time()
                    self.block_mining = tile

                if not self.start_mining:
                    self.start_mining = time.time()
                    self.block_mining = tile
                    
                if (time.time() - self.start_mining) * self.mining_amp > tilemap[tile][5]:
                    self.start_mining = 0
                    return closest_tile[0]
        
        else:
            self.start_mining = 0

        return None