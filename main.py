# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pygame-ce",
#   "numpy",
#   "zengl",
#   "webcolors",
#   "glm",
#   "pillow"
# ]
# ///

# NOTE: normally its PyGLM but theres an top level mapping missing so its glm now.

import numpy as np
import zengl
import glm
import pygame

import struct
import sys
import time
import asyncio

from engine.camera import Camera
from engine.mesh import Mesh
from src.loader import EventManager
from scene_manager import SceneManager
from engine.vao import *
from engine.vbo import *
from engine.fbo import *
from engine.shader_program import *
from engine.texture import *

import platform

WEB = True if sys.platform in ("wasi", "emscripten") else False

WIN_SIZE = 640, 480


class Game:
    def __init__(self, win_size=(640, 480)):
        # init pygame modules
        pygame.init()

        self.share_data = {
            "state": "main_menu"
        }  # SEND ANY DATA BETWEEN MODELS USING THIS

        # why u dont try to use GPU, (Or you cant do that)
        if not WEB:
            import zengl_extras

            try:
                zengl_extras.init(gpu=True, opengl_core=False)
                print("GPU")
            except:
                zengl_extras.init(gpu=False, opengl_core=False)

        # window size
        self.WIN_SIZE = glm.ivec2(
            win_size
        )  # why not just tuple? bcuz this auto-packs and auto-types

        # set opengl attr
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 0)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_ES
        )

        # construct opengl context
        pygame.display.set_caption("Ninjine")

        flags = (
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
            if not WEB
            else pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_mode(
            self.WIN_SIZE,
            flags=flags,
            vsync=0,
        )

        # make a new context
        self.ctx = zengl.context()

        # create an object to help track time
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.time = time.time()

        self.elapsed_frames = 0
        self.delta_time = 0
        self.elapsed_time = 0

        # camera
        self.camera = Camera(self)
        # mesh
        self.mesh = Mesh(self)
        # scene
        self.scene_manager = SceneManager(self)

        # events
        self.events = []
        # event manager
        self.event_manager = EventManager(self)

        if WEB:
            platform.window.canvas.style.width = "640px"
            platform.window.canvas.style.height = "480px"

    def check_events(self):
        self.events = pygame.event.get()

        self.event_manager.handle_events(
            self.events
        )  # this is where resizing windows and idk what goes

    def render(self):
        self.scene_manager.update()
        # print(self.scene_manager.scene)

    def quit(self):
        self.mesh.destroy()  # GL needs manual memory managment or pc will crash (soon enough)
        pg.quit()
        sys.exit()

    async def run(self):
        while True:
            if WEB and self.elapsed_frames < 1000:
                platform.window.canvas.style.width = "640px"
                platform.window.canvas.style.height = "480px"
            self.elapsed_frames += 1
            self.check_events()
            self.camera.update()
            self.render()

            self.delta_time = self.clock.tick(60) / 1000
            self.elapsed_time += self.delta_time
            self.fps = 1 / self.delta_time

            pygame.display.set_caption(f"FPS {self.fps} | DT {self.delta_time}")

            # swap buffers
            pygame.display.flip()
            await asyncio.sleep(0)


if __name__ == "__main__":
    app = Game(WIN_SIZE)
    asyncio.run(app.run())
