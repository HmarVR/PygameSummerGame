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

        self.font = pygame.Font("assets/fonts/renogare/Renogare-Regular.otf", 20)

        self.fuelbar = pygame.image.load("assets/textures/fuelbar.png").convert_alpha()
        self.spaceship = pygame.image.load(
            "assets/textures/spaceship.png"
        ).convert_alpha()
        self.spaceship_cache = {}
        self.spaceship_rot = 0

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

    def send_tex(self):
        try:
            self.app.mesh.texture.del_texture("ui")
        except:
            pass
        self.app.mesh.texture.textures["ui"] = self.app.mesh.texture.from_surface(
            self.ui_surf
        )
        self.tex0 = self.app.mesh.texture.textures["ui"]
        self.vao.texture_bind(0, "T_ui", self.tex0)

    def update_surf(self):
        # self.ui_surf.fill((0,0,0,0))
        self.ui_surf.fill("black")
        h = self.fuelbar.height
        pos = (10, ((480 / 2) - (h / 2)))
        
        fuel_left = self.app.share_data["fuel"] / self.app.share_data["fuel_max"]  # normalized
        fuel_height = fuel_left * self.fuelbar.height
        rest = (1 - fuel_left) * self.fuelbar.height
        rect = pygame.Rect(
            pos[0],
            pos[1] + rest,
            self.fuelbar.width,
            fuel_height,
        )
        pygame.draw.rect(self.ui_surf, "green", rect)
        self.ui_surf.blit(self.fuelbar, pos)

        try:
            surf = self.spaceship_cache[self.spaceship_rot]
        except KeyError:
            surf = pygame.transform.rotate(self.spaceship, self.spaceship_rot)
            self.spaceship_cache[self.spaceship_rot] = surf
        r = pygame.Rect(0, 0, 640, 480)
        r.move_ip(
            -surf.width // 2, -surf.height // 2
        )  # im not refactoring this, dont touch
        self.ui_surf.blit(surf, r.center)
        pygame.draw.circle(
            self.ui_surf, "red", pygame.Rect(0, 0, 640, 480).center, 1.0
        )

    def update(self):
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
            self.app.share_data["spaceship"].fuel -= v.length() * 0.01
            a_rad = math.atan2(y, x)
            a_deg = math.degrees(a_rad)
            end_angle = a_deg

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
        self.app.mesh.texture.del_texture("ui")
