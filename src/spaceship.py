from typing import TYPE_CHECKING
from struct import pack


if TYPE_CHECKING:
    from main import Game
    import zengl


def state(func):
    def wrapper(self, *args, **kwargs):
        if self.app.share_data["state"] == "space":
            return func(self, *args, **kwargs)
        else:
            return None
    return wrapper


class SpaceShip:
    def __init__(
        self, app: "Game", vao_name="spaceship", pos=(0, 0, 0), roll=0, scale=(1, 1)
    ) -> None:
        self.app = app
        self.ctx: zengl.context = app.ctx
        self.vao_name = vao_name

        self.app.share_data["spaceship"] = self
        
        planet_manager = self.app.share_data["space_planet"].planet_manager
        self.fuel_usage = 0.1
        self.fuel = 600 # planet_manager.fuel_to_planet("Platee")
        self.fuel_max = 600
        
        self.app.share_data["fuel"] = self.fuel
        self.app.share_data["fuel_usage"] = self.fuel_usage
        self.app.share_data["fuel_max"] = self.fuel_max

        self.vao = app.mesh.vao.get_vao(
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs["default"],
            vbo=self.app.mesh.vao.vbo.vbos["plane"],
            umap={"u_plsdriver": "vec3"},  # some drivers want this
            tmap=[],
        )
        app.mesh.vao.vaos[self.vao_name] = self.vao
        
    @state
    def update(self):
        self.app.share_data["fuel"] = self.fuel
        self.app.share_data["fuel_max"] = self.fuel_max
        self.render()

    def render(self):
        pass
        # self.init_uniforms()
        # self.vao.render()
        
    def destroy(self):
        self.app.mesh.vao.del_vao(self.vao_name)