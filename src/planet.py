import glm
import math
from copy import deepcopy
import struct
import zengl
import webcolors

from typing import TYPE_CHECKING

class Planet:
    def __init__(
        self, app: "Game", vao_name="sun", pos=(0, 0, 0), roll=0, scale=(1, 1)
    ):
        self.app = app
        self.ctx: zengl.context = app.ctx

        self.load_palette()

        self.time_speed = 1.0
        self.planetRotationSpeed = 0.1

        self.uniforms_map = {
            "time": {
                "value": lambda: struct.pack("f", self.app.elapsed_time),
                "glsl_type": "float",
            },
            "planetCenter": {
                "value": lambda: struct.pack("ff", *(glm.vec2(320, 240)- self.app.camera.position.xy/500) ),
                "glsl_type": "vec2",
            },
            "bodyRadius": {
                "value": lambda: struct.pack("f", 50),
                "glsl_type": "float",
            },
            "cloudRadius": {
                "value": lambda: struct.pack("f", 55),
                "glsl_type": "float",
            },
            "screenResolution": {
                "value": lambda: struct.pack("ff", 640.0, 480.0),
                "glsl_type": "vec2",
            },
            "aspectRatio": {
                "value": lambda: struct.pack("f", 3 / 2),
                "glsl_type": "float",
            },
            "screenAspect": {
                "value": lambda: struct.pack("ff", 3, 2),
                "glsl_type": "vec2",
            },
            "lightDirection": {
                "value": lambda: struct.pack("fff", *[math.sin(self.app.elapsed_time/500), -0.6, math.cos(self.app.elapsed_time/500)]),
                "glsl_type": "vec3",
            },
            "movedLightDirection": {
                "value": lambda: struct.pack("fff", *[math.sin(self.app.elapsed_time/50), -0.6, math.cos(self.app.elapsed_time/50)]),
                "glsl_type": "vec3",
            },
            "paletteSize": {
                "value": lambda: struct.pack("i", len(self.palette)),
                "glsl_type": "int",
            },
            "palette": {
                "value": self.get_palette,
                "glsl_type": f"vec4[{len(self.palette)}]",
            },
            "time_speed": {
                "value": lambda: struct.pack("f", self.time_speed),
                "glsl_type": "float",
            },
            "planetRotationSpeed": {
                "value": lambda: struct.pack("f", self.planetRotationSpeed),
                "glsl_type": "float",
            },
            "planetOffset": {  # for rotating planet but too lazy to write func
                "value": lambda: struct.pack("f", self.app.elapsed_time/480),
                "glsl_type": "float",
            },
            "isStar": {
                "value": lambda: struct.pack("?", False),  # TODO, make this a func
                "glsl_type": "bool",
            },
            "cameraPos": {
                "value": lambda: struct.pack("ff", self.app.camera.position.x, self.app.camera.position.y),
                "glsl_type": "vec2",
            },
        }

        umapping = {key: val["glsl_type"] for key, val in self.uniforms_map.items()}
        
        self.vao = app.mesh.vao.get_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["planet"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap=umapping,
            tmap=["T_planet", "T_planetUV", "T_planetNormal"],  # texture map
        )
        app.mesh.vao.vaos["sun"] = self.vao

        self.tex0 = app.mesh.texture.textures["sun"]
        self.vao.texture_bind(0, "T_planet", self.tex0)
        
        self.tex1 = app.mesh.texture.textures["uv"]
        self.vao.texture_bind(1, "T_planetUV", self.tex1)

        self.tex2 = app.mesh.texture.textures["normal"]
        self.vao.texture_bind(2, "T_planetNormal", self.tex2)

        self.init_uniforms()

    def load_palette(self):
        _palette = """000000
21283f
38526e
3f86b0
839dbf
cee3ef
"""
        self.palette = []
        _palette = _palette.splitlines()
        palette_size = len(_palette)
        for v in _palette:
            rgb = webcolors.hex_to_rgb(v if v[0] == "#" else f"#{v}")
            color = [rgb.red / 255, rgb.green / 255, rgb.blue / 255, 1.0]  # rgba
            self.palette.append(color)

    def get_palette(self):
        buffer = bytearray()
        for rgb in self.palette:
            buffer.extend(struct.pack("ffff", *rgb))
        return buffer

    def init_uniforms(self):
        for key, obj in self.uniforms_map.items():
            _type = obj["glsl_type"]
            func = obj["value"]
            self.vao.uniform_bind(key, func())

    def update(self):
        # self.vao.uniform_bind('m_view', (self.app.camera.m_proj * self.app.camera.m_view * self.m_model).to_bytes())
        self.render()

    def render(self):
        self.init_uniforms()
        self.vao.render()
        
    def destroy(self):
        self.app.mesh.vao.del_vao('sun')