import glm
import math
import struct
import zengl
import webcolors

from typing import TYPE_CHECKING
from src.planet_manager import PlanetManager
# from vbo import InstancingVBO

if TYPE_CHECKING:
    from main import Game


# FOR SPACE SCENE
class Sun:
    def __init__(
        self, app: "Game", vao_name="suni", pos=(0, 0, 0), roll=0, scale=(1, 1)
    ):
        self.app = app
        self.app.share_data["space_planet"] = self
        
        self.app.camera.SPEED = 250
        
        self.ctx: zengl.context = app.ctx

        self.time_speed = 1.0
        self.planetRotationSpeed = 0.1

        self.planet_manager = PlanetManager(self, self.app)
        self.init_uniforms()

        self.vao = app.mesh.vao.get_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["planet"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap=self.u_type_mapping,
            tmap=["T_planet", "T_planetNormal", "T_planetUV"],  # texture map
        )
        app.mesh.vao.vaos['suni'] = self.vao
        self.update_uniforms(self.uniforms)

        self.tex0 = app.mesh.texture.textures["sun"]
        self.vao.texture_bind(0, "T_planet", self.tex0)

        self.tex1 = app.mesh.texture.textures["uv"]
        self.vao.texture_bind(1, "T_planetUV", self.tex1)

        self.tex2 = app.mesh.texture.textures["normal"]
        self.vao.texture_bind(2, "T_planetNormal", self.tex2)

    def update_planet_tex(self, planet_name):
        try:
            texs = self.app.mesh.texture.textures
            texs["sun"] = self.planet_manager.planet_textures[planet_name.lower()]
            print(planet_name.lower())
            print(self.planet_manager.planet_textures)
            # self.tex0 = texs["sun"]
            self.vao.texture_bind(0, "T_planet", texs["sun"])
        except:
            print("ğ")

    def init_uniforms(self):
        self.uniforms = self.planet_manager.get_uniforms()
        self.u_type_mapping = {
            key: val["glsl_type"] for key, val in self.uniforms.items()
        }

    def update_uniforms(self, uniforms={}):
        for key, obj in uniforms.items():
            _type = obj["glsl_type"]
            func = obj["value"]
            self.vao.uniform_bind(key, func())

    def update(self):
        self.update_uniforms(self.planet_manager.dynamic_uniforms())
        self.render()

    def render(self):
        # self.init_uniforms()
        self.vao.render()
        
    def destroy(self):
        self.app.mesh.vao.del_vao('suni')