# How To Use ModzernGL (MODERNGL + ZENGL)

# Basics:

Place your objects in model.py, they have an init and update function alongside their `VAO` which can be used to render the object or bind uniforms. Or alternatively you can make a new `VAO` object by executing `self.app.mesh.vaos.add_vao(vao_name:str, fbo:fbo.Framebuffer, program:shader_program.Shader, vbo:vbo.VBO, umap:Dict, tmap:List[str])`

## Explanation:

- `vao_name`: the key when you access it through `self.app.mesh.vao.vaos[]`, should be a `str`
- `fbo`: the `Framebuffer` that the VAO is rendering to. More than one vao can render to the same framebuffer, should be of type `fbo.Framebuffer`
- `vbo`: the `VBO` that the VAO is using. more than one vao can use the same VBO, should inherit from type `vbo.VBO`
- `program`: the `Shader` that the VAO is using. More than one vao can use the same shader, should be of type `shader_program.Shader`

**_THESE FEATURES WILL PROBABLY BE ALTERED OR REMOVED IN THE FUTURE_**

- `umap`: the `uniform_map` that the VAO is using (must contain all of the shaders uniforms) (template for the uniform_buffer) and is of type `dict`. Includes:
  a `key` of uniform_name (name of the uniform in the shader) of type `str`
  a `value` of type `dict` containing:
  a `value` element containing the uniform value and is packed using `struct.pack` (import struct btw)
  a `glsl_type` element containing the uniform's glsl_type (all glsl types are at the end of this document)

- `tmap`: a list of all textures in the shader's uniform data (must contain all of the shaders samplers)

## Explanation:

- `vao_name`: the key when you access it through `self.app.mesh.vao.vaos[]`, should be a `str`
- `fbo`: the `Framebuffer` that the VAO is rendering to. More than one vao can render to the same framebuffer, should be of type `fbo.Framebuffer`
- `vbo`: the `VBO` that the VAO is using. more than one vao can use the same VBO, should inherit from type `vbo.VBO`
- `program`: the `Shader` that the VAO is using. More than one vao can use the same shader, should be of type `shader_program.Shader`

**_THESE FEATURES WILL PROBABLY BE ALTERED OR REMOVED IN THE FUTURE_**

- `umap`: the `uniform_map` that the VAO is using (must contain all of the shaders uniforms) (template for the uniform_buffer) and is of type `dict`. Includes:
  a `key` of uniform_name (name of the uniform in the shader) of type `str`
  a `value` of type `dict` containing:
  a `value` element containing the uniform value and is packed using `struct.pack` (import struct btw)
  a `glsl_type` element containing the uniform's glsl_type (all glsl types are at the end of this document)

- `tmap`: a list of all textures in the shader's uniform data (must contain all of the shaders samplers)
  each item in tmap can either be a sampler2d or a sampler2DArray(please set precision highp for both sampler2d and array in your shaders, otherwise weird errors will happen.)
