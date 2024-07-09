from enum import auto, Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Game
    import zengl




class StateManager:
    def __init__(
        self, app: "Game", vao_name="STATE", pos=(0, 0, 0), roll=0, scale=(1, 1)
    ):
        self.app = app
        self.ctx: zengl.context = app.ctx
        self.state = "main_menu"
        self.app.share_data["state_manager"] = self
        self.app.share_data["state"] = self.state

        self.vao = app.mesh.vao.get_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["default"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap={},
            tmap=[],  # texture map
        )
        app.mesh.vao.vaos[vao_name] = self.vao

    def change_state(self, state):
        self.state = state
        self.app.share_data["state"] = self.state

    def update(self):
        pass
        # self.render()

    def render(self):
        pass
        # self.init_uniforms()
        # self.vao.render()

