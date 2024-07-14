from enum import auto, Enum
from typing import TYPE_CHECKING
import sys
import math

import pygame

import zengl

import struct

if TYPE_CHECKING:
    from main import Game


def state(func):
    def wrapper(self, *args, **kwargs):
        if self.app.share_data["state"] == "space":
            return func(self, *args, **kwargs)
        else:
            return None

    return wrapper


class SpaceMenu:
    def __init__(
        self, app: "Game", vao_name="space_menu", pos=(0, 0, 0), roll=0, scale=(1, 1)
    ):
        self.app = app
        self.ctx: zengl.context = app.ctx
        self.vao_name = vao_name

        self.app.share_data["space_menu"] = self

        self.ui_surf = pygame.surface.Surface(
            (640, 480)
        ).convert_alpha()  # make rgba8unorm
        self.ui_surf.set_colorkey("black")
        
        self.init_map()

        pygame.mixer.music.load("assets/sounds/silver_universe.ogg")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1, fade_ms=500)

        self.font = pygame.Font("assets/fonts/renogare/Renogare-Regular.otf", 20)

        self.pg_snake = pygame.image.load_sized_svg(
            "assets/textures/pygame-ce.svg", (180, 90)
        ).convert_alpha()

        self.fuelbar = pygame.image.load("assets/textures/fuelbar.png").convert_alpha()
        self.spaceship = pygame.image.load(
            "assets/textures/spaceship.png"
        ).convert_alpha()
        self.spaceship_cache = {
            rot: pygame.transform.rotate(self.spaceship, rot)
            for rot in range(0, 360 + 1)
        }
        self.spaceship_rot = 0
        
        self.since_no_fuel = -1

        self.vao = app.mesh.vao.get_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["ui"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap={"u_plsdriver": "vec3"},  # some drivers want this
            tmap=["T_ui"],
        )
        app.mesh.vao.vaos[self.vao_name] = self.vao
        # self.update_surf()
        self.send_tex()

    def no_stuck(self):
        if self.since_no_fuel > 0.5:
            r = self.pg_snake.get_rect()
            r.center = pygame.Rect(0,0,*self.app.WIN_SIZE.xy).center
            r.move_ip(0, -100)
            print(r.topleft)
            self.ui_surf.blit(self.pg_snake, r.topleft)
            surf = self.font.render("The pygame-ce snake is\n helping you by giving you\n just enough fuel to reach your\n target!", True, "white")
            r2 = surf.get_rect()
            r2.center = pygame.Rect(0,0,*self.app.WIN_SIZE.xy).center
            r2.move_ip(0, 80)
            self.ui_surf.blit(surf, r2.topleft)
        elif self.since_no_fuel > 2:
            self.app.share_data["spaceship"].fuel = 1000
            self.app.share_data["spaceship"].fuel_max = 1000
            self.app.camera.freemove = True

    def init_map(self):
        self.map_area = pygame.Rect(0,0,1,1)
        planet_manager = self.app.share_data["planet_manager"]
        for body in planet_manager.bodies.values():
            pos: pygame.Vector2 = body["bodyPos"]
            rad = body["bodyRadius"]
            rect = pygame.Rect(*pos, rad, rad)
            self.map_area.union_ip(rect)
        self.map_area.inflate_ip(1000, 1000)
        # print(self.map_area)

    def draw_map(self):
        screen_area = pygame.Rect(0,0, 100,100)
        screen_area.topleft = [self.app.WIN_SIZE[0] - screen_area.w, self.app.WIN_SIZE[1] - screen_area.h]  # move to bottomleft
        screen_area.move_ip(-10, -10)
        pygame.draw.rect(self.ui_surf, "#0b132d", screen_area)
        
        planet_manager = self.app.share_data["planet_manager"]
        for body in planet_manager.bodies.values():
            pos:pygame.Vector2 = body["bodyPos"]
            normalizedx = pos.x / self.map_area.w  # this doesnt take x into account but whatever
            normalizedy = pos.y / self.map_area.h
            normalizedy = 1.0 - normalizedy  # pygame & opengl orientation is diff vertically
            screen_pos = (screen_area.x + normalizedx * screen_area.w, screen_area.y + normalizedy * screen_area.h)
            pygame.draw.circle(self.ui_surf, body["uiColor"], screen_pos, 2.0)
        
        # draw player
        pos:pygame.Vector2 = self.app.camera.position.xy
        normalizedx = pos.x / self.map_area.w  # this doesnt take x into account but whatever
        normalizedy = pos.y / self.map_area.h
        normalizedy = 1.0 - normalizedy  # pygame & opengl orientation is diff vertically
        screen_pos = (screen_area.x + normalizedx * screen_area.w, screen_area.y + normalizedy * screen_area.h)
        pygame.draw.circle(self.ui_surf, "blue", screen_pos, 3.0)

    def send_tex(self):
        try:
            self.app.mesh.texture.del_texture("space_ui")
        except:
            pass
        self.app.mesh.texture.textures["space_ui"] = self.app.mesh.texture.from_surface(
            self.ui_surf
        )
        self.tex0 = self.app.mesh.texture.textures["space_ui"]
        self.vao.texture_bind(0, "T_ui", self.tex0)

    def update_surf(self):
        # self.ui_surf.fill((0,0,0,0))
        self.ui_surf.fill("black")
        h = self.fuelbar.get_height()
        pos = (10, ((480 / 2) - (h / 2)))

        fuel_left = (
            self.app.share_data["fuel"] / self.app.share_data["fuel_max"]
        )  # normalized
        fuel_height = fuel_left * self.fuelbar.get_height()
        rest = (1 - fuel_left) * self.fuelbar.get_height()
        rect = pygame.Rect(
            pos[0],
            pos[1] + rest,
            self.fuelbar.get_width(),
            fuel_height,
        )
        pygame.draw.rect(self.ui_surf, "green", rect)
        self.ui_surf.blit(self.fuelbar, pos)

        try:
            surf = self.spaceship_cache[round(self.spaceship_rot)]
        except KeyError:
            surf = pygame.transform.rotate(self.spaceship, self.spaceship_rot)
            self.spaceship_cache[round(self.spaceship_rot)] = surf
        r = pygame.Rect(0, 0, 640, 480)
        r.move_ip(
            -surf.get_width() // 2, -surf.get_height() // 2
        )  # im not refactoring this, dont touch
        self.ui_surf.blit(surf, r.center)
        pygame.draw.circle(self.ui_surf, "red", pygame.Rect(0, 0, 640, 480).center, 1.0)

        self.draw_map()
        
        self.no_stuck()

    def update(self):
        if self.since_no_fuel != -1:
            self.since_no_fuel += self.app.delta_time
        keys = pygame.key.get_pressed()
        self.move(keys)
        self.render()
        # self.render()

    def move(self, keys):
        x = 0
        y = 0
        if keys[pygame.K_a]:
            x = 1
        if keys[pygame.K_d]:
            x = -1
        if keys[pygame.K_w]:
            y = -1
        if keys[pygame.K_s]:
            y = 1
        if x == 0 and y == 0:
            end_angle = self.spaceship_rot
        else:
            v = pygame.Vector2(x, y)
            v = v.normalize()
            # self.app.share_data["spaceship"].fuel -= v.length() * self.app.share_data["fuel_usage"]
            a_rad = math.atan2(y, x)
            a_deg = math.degrees(a_rad)
            end_angle = a_deg
            if self.app.share_data["spaceship"].fuel <= 0:
                self.app.camera.freemove = False
                self.since_no_fuel = 0

        start_angle = self.spaceship_rot % 360
        end_angle = end_angle % 360
        diff = end_angle - start_angle

        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        interpolated_angle = start_angle + diff * 0.1
        interpolated_angle = interpolated_angle % 360
        self.spaceship_rot = interpolated_angle

    @state
    def render(self):
        self.update_surf()
        self.send_tex()
        self.vao.render()

    def destroy(self):
        self.app.mesh.vao.del_vao(self.vao_name)
        self.app.mesh.texture.del_texture("space_ui")
