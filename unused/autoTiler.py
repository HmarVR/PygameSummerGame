import os

import pygame as pg
import random

hash_map = {
    (0, 0, 0,
    0, 1, 1,
    0, 1, 0): 0,
    (0, 0, 0,
    1, 1, 1,
    0, 1, 0): 1,
    (0, 0, 0,
    1, 1, 0,
    0, 1, 0): 2,
    (0, 0, 0,
    0, 1, 0,
    0, 1, 0): 3,
    (0, 1, 0,
    0, 1, 1,
    0, 1, 0): 4,
    (0, 1, 0,
    1, 1, 1,
    0, 1, 0): 5,
    (0, 1, 0,
    1, 1, 0,
    0, 1, 0): 6,
    (0, 1, 0,
    0, 1, 0,
    0, 1, 0): 7,
    (0, 1, 0,
    0, 1, 1,
    0, 0, 0): 8,
    (0, 1, 0,
    1, 1, 1,
    0, 0, 0): 9,
    (0, 1, 0,
    1, 1, 0,
    0, 0, 0): 10,
    (0, 1, 0,
    0, 1, 0,
    0, 0, 0): 11,
    (0, 0, 0,
    0, 1, 1,
    0, 0, 0): 12,
    (0, 0, 0,
    1, 1, 1,
    0, 0, 0): 13,
    (0, 0, 0,
    1, 1, 0,
    0, 0, 0): 14,
    (0, 0, 0,
    0, 1, 0,
    0, 0, 0): 15,
}

def check(tilemap, pos):
    if pos in tilemap and tilemap[pos]:
        return 1
    return 0

def get_neighboring_tiles(tilemap, tile):
    origin_tile = tile.split(';')
    x = int(origin_tile[0])
    y = int(origin_tile[1])
    n = (
        0, check(tilemap, f'{x};{y-1}'), 0,
        check(tilemap, f'{x-1};{y}'), check(tilemap, f'{x};{y}'), check(tilemap, f'{x+1};{y}'),
        0, check(tilemap, f'{x};{y+1}'), 0)

    return hash_map[n]# if n in hash_map else 15

if __name__ == '__main__':
    textures = {}
    amount_of_textures = 24
    for x in range(amount_of_textures):
        textures[x] = pg.image.load(os.path.join(os.getcwd(), 'tiles', f'Albasee{x}.png'))

    run = True
    display = pg.display.set_mode((500, 500))

    map_ = {}

    for x in range(10):
        for y in range(10):
            map_[f'{x};{y}'] = 0

    tile_size = 32

    while run:
        display.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                pos = f"{mouse_pos[0]//32};{mouse_pos[1]//32}"
                map_[pos] = 1

        for tile in map_:
            if map_[tile]:
                origin_tile = tile.split(';')
                x = int(origin_tile[0])
                y = int(origin_tile[1])
                display.blit(textures[get_neighboring_tiles(map_, tile)], (x*tile_size, y*tile_size))

        pg.display.update()