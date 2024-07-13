from enum import auto, Enum
from typing import TYPE_CHECKING
import sys

import pygame

import zengl
import math
import struct

WEB = True if sys.platform in ("wasi", "emscripten") else False

if TYPE_CHECKING:
    from main import Game


def state(func):
    def wrapper(self, *args, **kwargs):
        if self.app.share_data["state"] == "main_menu":
            return func(self, *args, **kwargs)
        else:
            return None

    return wrapper


class MainMenu:
    def __init__(
        self, app: "Game", vao_name="main_menu", pos=(0, 0, 0), roll=0, scale=(1, 1)
    ):
        self.app = app
        self.ctx: zengl.context = app.ctx

        self.app.share_data["main_menu"] = self

        self.ui_surf = pygame.surface.Surface(
            (640, 480)
        ).convert_alpha()  # make rgba8unorm
        self.button_width = 100
        self.button_height = 50
        
        pygame.mixer.music.load("assets/sounds/great_space_expedition.ogg")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1, fade_ms=500)

        self.pg_snake = pygame.image.load_sized_svg(
            "assets/textures/pygame-ce.svg", (180, 90)
        ).convert_alpha()
        if not WEB:
            pygame.transform.hsl(self.pg_snake, 0, -0.1, -0.2, self.pg_snake)

        self.font = pygame.Font("assets/fonts/renogare/Renogare-Regular.otf", 24)
        self.midfont = pygame.Font("assets/fonts/renogare/Renogare-Regular.otf", 28)
        self.bigfont = pygame.Font("assets/fonts/renogare/Renogare-Regular.otf", 36)

        self.buttons = {"play": {"func": self.play}, "exit": {"func": self.exit}}
        self.selected = list(self.buttons.keys())[0]
        self.get_button_rects()

        self.vao = app.mesh.vao.get_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["main_menu_ui"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap={
                "u_plsdriver": "vec3",
                "time": "float",
                "screenResolution": "vec2",
            },  # some drivers want this
            tmap=["T_ui"],
        )
        app.mesh.vao.vaos["main_menu"] = self.vao
        self.vao.uniform_bind("screenResolution", struct.pack("ff", *(640, 480)))
        self.update_surf()
        self.send_tex()

    def send_uniforms(self):
        self.vao.uniform_bind("time", struct.pack("f", self.app.elapsed_time))

    def send_tex(self):
        # print(sys.getsizeof(self.app.mesh.texture.textures))
        try:
            self.app.mesh.texture.del_texture("ui")
            del self.tex0
            # print("deleting texture")
        except:
            pass
            # print("no texture :(")
        self.app.mesh.texture.textures["ui"] = self.app.mesh.texture.from_surface(
            self.ui_surf
        )
        # print("set new texture")
        self.tex0 = self.app.mesh.texture.textures["ui"]
        self.vao.texture_bind(0, "T_ui", self.tex0)

    def get_button_rects(self):
        i = 0
        for name, item in self.buttons.items():
            center = pygame.Vector2(self.app.WIN_SIZE[0] / 2, self.app.WIN_SIZE[1] / 2)
            pos = center - pygame.Vector2(
                self.button_width / 2, -i * (self.button_height + 10)
            )
            rect = pygame.Rect(*pos, self.button_width, self.button_height)
            item["rect"] = rect
            i += 1

    def play(self):
        self.app.scene_manager.load_scene("space")
        self.app.share_data["state"] = "space"

    def exit(self):
        if sys.platform in ("emscripten", "wasi"):
            pass  # prob shouldnt exit in a browser tab
        else:
            self.app.mesh.destroy()
            pygame.quit()
            raise SystemExit

    @state
    def click(self):
        button = self.buttons[self.selected]
        button["func"]()

    def update(self):
        self.render()
        # self.render()

    @state
    def move_selected(self, v: int):
        current_id = list(self.buttons.keys()).index(self.selected)
        _id = (current_id + v) % len(self.buttons)
        name = list(self.buttons.keys())[_id]
        self.selected = name
        self.update_surf()
        self.send_tex()

    def letter_draw(self):
        ypos = 100
        rad = 50  # radius for output of sin
        text = "Ore Oddysey"
        sep_width = 10
        sep_count = len(text) - 1
        w = self.bigfont.render(text, True, "green").get_width() + sep_width * sep_count

        let_mul = math.pi / len(text)  # so um idk how to explain,
        # if the letter count is too much + let mul is too high then
        # it wont form a perfect standing wave(I believe is the right term)

        # I still have to make it so that the letters in the middle move the most(antinode) and the ones on either edge dont move much(node) but too lazy tbh
        #

        for j, col in enumerate(["darkgreen", "green"]):
            # j will make the sin value exactly 1pi ahead so it will form an infinity symbol
            start_pos = [(640 / 2) - (w / 2), ypos]
            for i, l in enumerate(text):
                surf = self.bigfont.render(l, True, col)
                start_pos[1] = (
                    ypos
                    + math.sin(
                        (j * math.pi + i * let_mul + self.app.elapsed_time)
                        % (math.pi * 2)
                    )
                    * rad
                )
                self.ui_surf.blit(surf, start_pos)
                start_pos[0] += surf.get_width() + sep_width

    def update_surf(self):
        self.ui_surf.fill(("#2E2C33"))
        for name, obj in self.buttons.items():
            rect: pygame.Rect = obj["rect"]
            if name == self.selected:
                pygame.draw.rect(self.ui_surf, "#5bc94b", rect.inflate(4, 4))
            pygame.draw.rect(self.ui_surf, "#1F1F1F", rect)

            surf = self.font.render(name, True, "#5bc94b")
            size = pygame.Vector2(surf.get_size())
            rectsize = pygame.Vector2(rect.size)
            topleft = rect.topleft + (rectsize - size) / 2
            self.ui_surf.blit(surf, topleft)
        self.letter_draw()
        r = self.pg_snake.get_rect()
        r.topleft = [self.app.WIN_SIZE[0] - r.width, self.app.WIN_SIZE[1] - r.height]
        r.move_ip(-24, -24)
        self.ui_surf.blit(self.pg_snake, r.topleft)

    @state
    def render(self):
        # im sorry performance
        self.update_surf()
        self.send_tex()
        self.send_uniforms()

        self.vao.render()
        # self.init_uniforms()
        # self.vao.render()

    def destroy(self):
        self.app.mesh.vao.del_vao("main_menu")
        self.app.mesh.texture.del_texture("ui")
