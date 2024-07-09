import pygame as pg
import json

from player.player import Player

class Game:
    def __init__(self):
        self.running = True
        self.resolution = (1280/2, 720/2)
        self.fps = 60
        self.display = pg.display.set_mode(self.resolution, vsync = 1)
        self.clock = pg.time.Clock()

        with open('file.json') as file:
            self.tilemap = json.load(file)

    def run(self):
        player = Player()
        player.rect.x = 3*16
        player.rect.y = 9*16
        player.rect.w = 10
        player.rect.h = 13

        while self.running:
            dt = self.clock.tick(self.fps) / 1000
            self.display.fill((0, 0, 0))

            player.velocity[1] += 800 * dt

            #player.apply_physics(self.objects, dt)
            for x in self.tilemap['0']:
                pos = x.split(';')
                pos_x = int(pos[0]) * 16
                pos_y = int(pos[1]) * 16
                pg.draw.rect(self.display, (255, 0, 0), (pos_x, pos_y, 16, 16))
        
            player.apply_physics(self.tilemap['0'], dt)

            player.check(pg.key.get_pressed())

            pg.draw.rect(self.display, (255, 255, 255), player.rect)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    player.rect.x, player.rect.y = pg.mouse.get_pos()

            pg.display.update()

if __name__ == '__main__':
    Game().run()

    
