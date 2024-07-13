import numpy as np
import glm
import struct
import json
from engine.vbo import InstancingVBO


class Tilemap:
    def __init__(self, app, tile_size=16):
        self.app = app

        self.app.share_data["tilemap"] = self

        self.ctx: mgl.Context = app.ctx
        self.tile_size = tile_size
        str_dict = {
            0 : 65,
            'Albasee0': 0,
            'Albasee1': 1,
            'Albasee2': 2,
            'Albasee3': 3,
            'Albasee4': 4,
            'Albasee5': 5,
            'Albasee6': 6,
            'Albasee7': 7,
            'Albasee8': 8,
            'Albasee9': 9,
            'Albasee10': 10,
            'Albasee11': 11,
            'Albasee12': 12,
            'Albasee13': 13,
            'Albasee14': 14,
            'Albasee15': 15,
            'AlbaseeGlaicer0': 16,
            'AlbaseeGlaicer1': 17,
            'AlbaseeGlaicer2': 18,
            'AlbaseeGlaicer3': 19,
            'AlbaseeGlaicer4': 20,
            'AlbaseeGlaicer5': 21,
            'AlbaseeGlaicer6': 22,
            'AlbaseeGlaicer7': 23,
            'AlbaseeGlaicer8': 24,
            'AlbaseeGlaicer9': 25,
            'AlbaseeGlaicer10': 26,
            'AlbaseeGlaicer11': 27,
            'AlbaseeGlaicer12': 28,
            'AlbaseeGlaicer13': 29,
            'AlbaseeGlaicer14': 30,
            'AlbaseeGlaicer15': 31,
            'Vulakit0': 32,
            'Vulakit1': 33,
            'Vulakit2': 34,
            'Vulakit3': 35,
            'Vulakit4': 36,
            'Vulakit5': 37,
            'Vulakit6': 38,
            'Vulakit7': 39,
            'Vulakit8': 40,
            'Vulakit9': 41,
            'Vulakit10': 42,
            'Vulakit11': 43,
            'Vulakit12': 44,
            'Vulakit13': 45,
            'Vulakit14': 46,
            'Vulakit15': 47,
            'AlbaseeBG0': 48,
            'AlbaseeBG1': 49,
            'AlbaseeBG2': 50,
            'AlbaseeBG3': 51,
            'AlbaseeBG4': 52,
            'AlbaseeBG5': 53,
            'AlbaseeBG6': 54,
            'AlbaseeBG7': 55,
            'AlbaseeBG8': 56,
            'AlbaseeBG9': 57,
            'AlbaseeBG10': 58,
            'AlbaseeBG11': 59,
            'AlbaseeBG12': 60,
            'AlbaseeBG13': 61,
            'AlbaseeBG14': 62,
            'AlbaseeBG15': 63,
            'VulakitBasalt0': 64,
            'VulakitBasalt1': 65,
            'VulakitBasalt2': 66,
            'VulakitBasalt3': 67,
            'VulakitBasalt4': 68,
            'VulakitBasalt5': 69,
            'VulakitBasalt6': 70,
            'VulakitBasalt7': 71,
            'VulakitBasalt8': 72,
            'VulakitBasalt9': 73,
            'VulakitBasalt10': 74,
            'VulakitBasalt11': 75,
            'VulakitBasalt12': 76,
            'VulakitBasalt13': 77,
            'VulakitBasalt14': 78,
            'VulakitBasalt15': 79,
        }
        self.str_dict = str_dict
        with open(f"file.json") as file:
            self.tilemap = json.load(file)
            self.app.share_data["tilemap"] = self
            self.app.camera.freemove = False

        self.offgrid_tiles = []

        self.MAPSIZE = sum([len(tilemap_i) for tilemap_i in self.tilemap.values()])
        self.size = self.MAPSIZE + 256

        self.block_arr = np.zeros((self.size, 4), dtype="f4")

        giga_i = 0
        for index, tilemap_i in reversed(self.tilemap.items()):
            for j in tilemap_i.items():
                key = j[0].split(";")
                # print(key, int(index))
                self.block_arr[giga_i] = [
                    int(key[0]),
                    -int(key[1]),
                    self.str_dict[j[1][4]],
                    int(index) * 0.1,
                ]
                giga_i += 1

        self.block_arr.reshape((self.size, 4))
        self.buffer = self.ctx.buffer(self.block_arr)

        self.ibo = InstancingVBO(self.ctx, self.buffer, "4f", "posOffset", offset=2)
        self.app.mesh.vao.vbo.vbos["mapIbo"] = self.ibo

        self.vao = app.mesh.vao.get_ins_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["tilemap"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            ibo=self.ibo,
            umap={
                "m_model": "mat4",
                "m_view": "mat4",
            },
            tmap=["Tiler"],
        )

        self.app.mesh.vao.vaos["tiler"] = self.vao
        app.mesh.texture.textures["albasee"] = app.mesh.texture.get_texture_array(
            "assets/textures/tiles/"
        )
        self.tex = app.mesh.texture.textures["albasee"]
        self.vao.texture_bind(0, "Tiler", self.tex)

        self.pos = glm.vec3(0)
        self.roll = 0
        self.scale = glm.vec2(self.tile_size / 2)

        self.m_model = self.get_model_matrix()
        self.vao.uniform_bind("m_model", self.m_model.to_bytes())
        self.app.camera.position.z = 120

    def update(self):
        self.vao.uniform_bind(
            "m_view",
            (self.app.camera.m_proj * self.app.camera.m_view * self.m_model).to_bytes(),
        )
        self.vao.render(instance_count=self.MAPSIZE)

    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, glm.radians(self.roll), glm.vec3(0, 0, 1))
        # scale
        m_model = glm.scale(m_model, glm.vec3(self.scale[0], self.scale[1], 1))
        return m_model

    def render(self): ...

    def destroy(self):
        self.app.mesh.vao.del_vao("tiler")
        self.app.ctx.release(self.ibo)
