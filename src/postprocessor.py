from typing import TYPE_CHECKING
import glm
import struct
import pygame as pg

if TYPE_CHECKING:
    from main import Game


class ProcessRender:
    def __init__(self, app: "Game", vao_name="post_process"):
        self.app = app
        self.app.share_data["post_process"] = self

        self.dust_clouds = [[-1000, -1000, 0, 0] for _ in range(4)]

        self.app.mesh.vao.Framebuffers.add_framebuffer("output", self.app.WIN_SIZE)
        self.app.mesh.vao.add_vao(
            vao_name="post_process",
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["output"],
            program=self.app.mesh.vao.program.programs["post_process"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap={
                "scaling_vector": "vec2",
                "pixel_size": "float",
                "screenResolution": "vec2",
                "dustClouds": "vec4[4]",
                "camPos": "vec3",
            },
            tmap=["U_image"],
        )
        self.vao = self.app.mesh.vao.vaos["post_process"]

        self.isSceneInit = False
        self.win_size = glm.vec2(self.app.WIN_SIZE)
        self.app.share_data["sizit"] = self.resize

    def send_dust_clouds(self):
        buf = bytearray()
        for p in self.dust_clouds:
            buf.extend(struct.pack("ffff", *p))
        self.vao.uniform_bind("dustClouds", buf)

    def resize(self):
        fbox = self.app.mesh.vao.Framebuffers.get_framebuffer(self.app.WIN_SIZE.xy)
        self.vao.FBO = fbox
        self.app.mesh.vao.Framebuffers.del_framebuffer("output")
        self.app.mesh.vao.Framebuffers.framebuffers["output"] = fbox
        self.vao.please_update = True
        self.win_size = glm.vec2(self.app.WIN_SIZE)

        # WARNING: LONG LINES-OF-CODE, INCOMING!!!
        xt = self.app.mesh.texture.from_buffer(
            self.app.mesh.vao.Framebuffers.framebuffers["default"].image_out[0]
        )
        self.vao.texture_bind(0, "U_image", xt)

    def render(self):
        self.app.mesh.vao.Framebuffers.framebuffers["output"].image_out[0].clear()
        self.app.mesh.vao.Framebuffers.framebuffers["output"].depth_out.clear()
        if not self.isSceneInit:
            self.resize()

        ar = self.maintain_aspect_ratio(self.app.WIN_SIZE)
        self.vao.uniform_bind("scaling_vector", ar.to_bytes())

        self.vao.uniform_bind("screenResolution", struct.pack("ff", *(640, 480)))
        self.send_dust_clouds()
        self.vao.uniform_bind("camPos", struct.pack("fff", *self.app.camera.position))
        print(self.dust_clouds)

        self.vao.render()
        if not self.isSceneInit:
            self.resize()

        self.isSceneInit = True
        self.app.scene_manager.scene.blit_img = (
            self.app.mesh.vao.Framebuffers.framebuffers["output"].image_out[0]
        )
        self.vao.FBO.image_out[0].blit()

    def maintain_aspect_ratio(self, windu):
        current_ratio = windu[0] / windu[1]

        if current_ratio > 1.333:
            # Scale based on height to fit the 4:3 aspect ratio 160 320 480(3) 640 (4)
            scaling_vector = glm.vec2(1.0, 1.333 / current_ratio)
        else:
            # Scale based on width to fit the 4:3 aspect ratio 160 320 480(3) 640 (4)
            scaling_vector = glm.vec2(current_ratio / 1.333, 1.0)

        return scaling_vector
