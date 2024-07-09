from engine.vao import VAOs
from engine.texture import Textures


class Mesh:
	def __init__(self, app):
		self.app = app
		self.vao = VAOs(app.ctx)
		self.texture = Textures(app.ctx)

	def destroy(self):
		self.vao.destroy()
		self.texture.destroy()