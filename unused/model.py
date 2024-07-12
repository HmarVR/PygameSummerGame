import numpy as np
import pygame as pg
import glm

import sys
import time
import math
import struct
import json
import zengl
import webcolors

from typing import TYPE_CHECKING
from vbo import InstancingVBO

if TYPE_CHECKING:
    from main import Game


class BaseModel:
    def __init__(self, app, vao_name, tex_id, pos=(0, 0, 0), roll=0, scale=(1, 1)):
        self.app = app
        self.pos = pos
        self.roll = roll
        self.scale = scale
        self.m_model = self.get_model_matrix()
        self.tex_id = tex_id
        self.vao = app.mesh.vao.vaos[vao_name]
        self.camera = self.app.camera

    def update(self): ...

    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, glm.radians(self.roll), glm.vec3(0, 0, 1))
        # scale
        m_model = glm.scale(m_model, glm.vec3(self.scale, 0))
        return m_model

    def render(self):
        self.update()
        self.m_model = self.get_model_matrix()
        self.vao.render()




"""
class Cube(BaseModel):
    def __init__(self, app, vao_name='cube', tex_id=0, pos=(0, 0, 0), rot=0, scale=(1, 1)):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()

    def update(self):
        self.texture.use()
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

    def on_init(self):
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use()
        # mvp
        self.program['m_proj'] = self.camera.m_proj.flatten()
        self.program['m_view'] = self.camera.m_view.flatten()
        self.program['m_model'] = self.m_model.flatten()
"""


"""
class Player(BaseModel):
    def __init__(self, app, vao_name='cube', tex_id='player', pos=glm.vec3(0, 0, 0), rot=0, scale=glm.vec2(14, 18)):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()
        self.force = glm.vec2(0)

    def update(self):
        self.texture.use()
        self.program['u_texture_0'] = 0
        tss = time.time() - self.app.start_time
        anim_fps = 10
        self.program['frame'].write(glm.int8( round((tss * anim_fps) % 22) ))
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

        self.force += glm.vec2(0, -150) * self.app.delta_time

        self.pos   += glm.vec3(self.force, 0) * self.app.delta_time
        self.roll  += self.app.delta_time * 90

    def on_init(self):
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.texture.use()
        self.program['u_texture_0'] = 0
        self.program['frame'] = 0
        # mvp
        self.program['m_proj'] = self.camera.m_proj.flatten()
        self.program['m_view'] = self.camera.m_view.flatten()
        self.program['m_model'] = self.m_model.flatten()


class Cat(BaseModel):
    def __init__(self, app, vao_name='cat', tex_id='cat',
                 pos=(0, 0, 0), rot=0, scale=(1, 1)):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()

    def update(self):
        self.texture.use()
        self.program['m_view'] = self.camera.m_view.flatten()
        self.program['m_model'] = self.m_model.flatten()

    def on_init(self):
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use()
        # mvp
        self.program['m_proj'] = self.camera.m_proj.flatten()
        self.program['m_view'] = self.camera.m_view.flatten()
        self.program['m_model'] = self.m_model.flatten()
"""


class ProcessRender:
    def __init__(self, app, vao_name="screener"):
        self.app = app
        self.vao = app.mesh.vao.vaos[vao_name]

    def render(self, output_texture):
        self.vao.render()

    def maintain_aspect_ratio(self, windu):
        current_ratio = windu[0] / windu[1]

        if current_ratio > 1.333:
            # Scale based on height to fit the 4:3 aspect ratio 160 320 480(3) 640 (4)
            scaling_vector = glm.vec2(1.0, 1.333 / current_ratio)
        else:
            # Scale based on width to fit the 4:3 aspect ratio 160 320 480(3) 640 (4)
            scaling_vector = glm.vec2(current_ratio / 1.333, 1.0)

        return scaling_vector

"""
class NBaseVBO:
    def __init__(self, ctx, vbo):
        self.ctx = ctx
        self.vbo = vbo
        self.format: str = "3f /i"
        self.attribs: list = ["position"]

    def destroy(self):
        self.vbo.release()"""
