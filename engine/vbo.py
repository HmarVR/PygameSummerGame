import numpy as np
# import pywavefront
from typing import TYPE_CHECKING, Literal, List, Dict

if TYPE_CHECKING:
	import zengl


class VBOs:
	def __init__(self, ctx):
		self.vbos:Dict[str, "VBO"] = {}
		self.vbos['plane'] = PlaneVBO(ctx)

	def destroy(self) -> None:
		[vbo.destroy() for vbo in self.vbos.values()]


class VBO:
	def __init__(self, ctx):
		self.ctx:"zengl.Context" = ctx
		self.vbo:"zengl.Buffer" = self.get_vbo()
		self.format:str = None
		self.attribs:List[str] = None
		self.locations:List[int] = None
		
		self.cull_face:str = "back"

	def get_vertex_data(self) -> np.ndarray: ...

	def get_vbo(self) -> "zengl.Buffer":
		vertex_data = self.get_vertex_data()
		vbo = self.ctx.buffer(vertex_data)
		return vbo

	def destroy(self) -> None:
		self.ctx.release(self.vbo)

	
class PlaneVBO(VBO):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.format:str = '2f 3f'
		self.locations:List[int] = [0, 1]
		self.attribs:List[str] = ['in_texcoord_0', 'in_position']

	@staticmethod
	def get_data(vertices, indices) -> np.ndarray:
		data = [vertices[ind] for triangle in indices for ind in triangle]
		return np.array(data, dtype='f4')

	def get_vertex_data(self) -> np.ndarray:
		vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1)]

		indices = [(0, 2, 3), (0, 1, 2)]
		vertex_data = self.get_data(vertices, indices)

		tex_coord_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
		tex_coord_indices = [(0, 2, 3), (0, 1, 2)]
		tex_coord_data = self.get_data(tex_coord_vertices, tex_coord_indices)
		vertex_data = np.hstack([tex_coord_data, vertex_data])
		return vertex_data
		
		
class TriangleVBO(VBO):
	def __init__(self, ctx):
		super().__init__(ctx)
		self.format:str = '2f 3f'
		self.locations:List[int] = [0, 1]
		self.attribs:List[str] = ['in_texcoord_0', 'in_position']

	@staticmethod
	def get_data(vertices, indices) -> np.ndarray:
		data = [vertices[ind] for triangle in indices for ind in triangle]
		return np.array(data, dtype='f4')

	def get_vertex_data(self) -> np.ndarray:
		vertices = [(-1, -1, 1), (1,  -1,  1), (0, 1,  1)]

		indices = [(0, 1, 2)]
		vertex_data = self.get_data(vertices, indices)

		tex_coord_vertices = [(0, 0), (1, 0), (0.5, 1)]
		tex_coord_indices = [(0, 1, 2)]
		tex_coord_data = self.get_data(tex_coord_vertices, tex_coord_indices)
		vertex_data = np.hstack([tex_coord_data, vertex_data])
		return vertex_data
		
	def destroy(self) -> None:
		self.ctx.release(self.vbo)
		

class InstancingVBO:
	def __init__(self, ctx, vbo, format:str, *attribs:List[str], offset=0):
		self.ctx = ctx
		self.vbo = vbo
		self.format:str = f"{format} /i"
		self.locations:List[int] = [i + offset for i in range( len(attribs) )]
		self.attribs:List[str] = attribs

	def destroy(self) -> None:
		self.ctx.release(self.vbo)
