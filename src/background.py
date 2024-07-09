import struct

class Background:
    def __init__(self, app, vao_name="background", tex_id="plant2"):
        self.app = app
        self.tex_id = tex_id
        self.vao = app.mesh.vao.vaos[vao_name]

        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.vao.texture_bind(0, "U_bg_image", self.texture)
        self.vao.uniform_bind("screenResolution", struct.pack("ff", *(640.0, 480.0)))

    def render(self):
        self.vao.uniform_bind("mos", (self.app.camera.position/2000).to_bytes())
        self.vao.render()
        
    def destroy(self):
        pass