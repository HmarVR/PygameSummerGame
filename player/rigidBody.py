import pygame as pg

neighbor_offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

class RigidBody:
    def __init__(self):
        self.rect = pg.FRect(0, 0, 16, 16)
        self.velocity = [0, 0]
        self.collision_types = {'bottom': False, 'top': False, 'right': False, 'left': False}
        self.coyote_time = 0
        self.elasticity = 0
        self.friction = 0.1

    def get_neighboring_tiles(self, tilemap):
        tiles = []
        loc = (round(self.rect.x // 16), round(self.rect.y // 16))

        for offset in neighbor_offsets:
            around_loc = f'{offset[0] + loc[0]};{offset[1] + loc[1]}'
            if around_loc in tilemap:
                if tilemap[around_loc][1]:
                    x, y = around_loc.split(';')
                    x = (int(x)) * 16
                    y = (int(y)) * 16
                    r = pg.Rect(x, y, 16, 16)
                    tiles.append(r)

        return tiles

    def collision_test(self, rect, tileset):
        hit_list = []
        
        for tile in self.get_neighboring_tiles(tileset):
            if rect.colliderect(tile):
                hit_list.append(tile)

        return hit_list

    def apply_physics(self, tilemap, dt):
        self.collision_types = {'bottom': False, 'top': False, 'right': False, 'left': False}

        self.rect.x += self.velocity[0] * dt

        hit_list = self.collision_test(self.rect, tilemap)

        for block in hit_list:
            if self.velocity[0] > 0:
                self.rect.right = block.left
                self.collision_types['left'] = True

            if self.velocity[0] < 0:
                self.rect.left = block.right
                self.collision_types['right'] = True

            self.velocity[1] /= self.friction ** dt
            self.velocity[0] = -self.velocity[0] * self.elasticity

            break

        self.rect.y += self.velocity[1] * dt

        hit_list = self.collision_test(self.rect, tilemap)
        
        for block in hit_list:
            if self.velocity[1] > 0:
                self.rect.bottom = block.top
                self.collision_types['bottom'] = True
                self.coyote_time = 0

            if self.velocity[1] < 0:
                self.rect.top = block.bottom
                self.collision_types['top'] = True

            self.velocity[0] /= self.friction ** dt
            self.velocity[1] = -self.velocity[1] * self.elasticity
            break

        self.coyote_time += dt