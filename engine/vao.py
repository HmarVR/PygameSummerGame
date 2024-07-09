from typing import TYPE_CHECKING, Dict, List, Tuple, Literal, Any
from engine.shader_program import ShaderPrograms, Shader
from engine.vbo import VBOs
from engine.fbo import Framebuffers
import struct, zengl

if TYPE_CHECKING:
    from main import Game
    import pygame
    from fbo import FBO
    from vbo import VBO, InstancingVBO
    from texture import Texture


class VAO:
    def __init__(
        self,
        ctx:"zengl.Context",
        shader:Shader,
        FBO:"FBO",
        VBO:"VBO",
        IBO:"InstancingVBO" = None,
        uniforms_map:Dict[str, str] = {},
        textures_names:List[str] = [],
        instance_count:int = 1,
    ):
        self.ctx:"zengl.Context" = ctx
        self.uniforms, self.ufs_size, self.ufs_includes = self.pack_uniforms(
            uniforms_map
        )
        self.shader:"Shader" = shader
        self.FBO:"FBO" = FBO
        self.VBO:"VBO" = VBO
        self.IBO:"IBO" = IBO
        self.dynaforms:Dict[str, Any] = {}
        
        self.uniform_buffer:"zengl.Buffer" = self.ctx.buffer(size=self.ufs_size)
        self.please_update:bool  = False
        self.NUL_IMG = self.ctx.image(size=(1, 1), format="rgba8unorm", texture=True, samples=1)
        
        self.layout = [{"name": "Common", "binding": 0}]
        [self.layout.append({"name": textures_name, "binding": i}) for i, textures_name in enumerate(textures_names)]
        
        self.resources = [{"type": "uniform_buffer", "binding": 0, "buffer": self.uniform_buffer}]
        
        for i in range(len(textures_names)):
            self.resources.append( \
            {
                "type": "sampler",
                "binding": i,
                "image": self.NUL_IMG,
                "min_filter": "nearest",
                "mag_filter": "nearest",
                "wrap_x": "clamp_to_edge",  # clamp_to_edge == you need to give 0 - 1
                "wrap_y": "clamp_to_edge",  # repeat == automatically repeats texture
            }
        )
        self.ptb = 1

        self.construct_pipeline(instance_count=instance_count)

    def reconstruct_pipeline(self, instance_count:int=1):
        layout = self.layout
        resources = self.resources
        
        old_line = self.pipeline 
        if (self.dynaforms=={}):
            self.pipeline = self.ctx.pipeline(
                template=old_line,
                resources=resources,
                framebuffer=self.FBO.get_FBO(),
                viewport=self.FBO.get_viewport(),
                blend=self.shader.blend_data,
                instance_count=instance_count,
            )
        else:
            self.pipeline = self.ctx.pipeline(
                template=old_line,
                resources=resources,
                framebuffer=self.FBO.get_FBO(),
                viewport=self.FBO.get_viewport(),
                blend=self.shader.blend_data,
                uniforms=self.dynaforms,
                instance_count=instance_count,
            )
        self.ctx.release(old_line)
        self.please_update = False
        
        
    def construct_pipeline(self, instance_count:int=1):
        layout = self.layout
        resources = self.resources

        if self.IBO != None:
            buffers = [
                *zengl.bind(self.VBO.vbo, self.VBO.format, *self.VBO.locations),
                *zengl.bind(self.IBO.vbo, self.IBO.format, *self.IBO.locations),
            ]
        else:
            buffers = [
                *zengl.bind(self.VBO.vbo, self.VBO.format, *self.VBO.locations),
            ]
        
        self.pipeline = self.ctx.pipeline(
            includes=self.ufs_includes,
            vertex_shader=self.shader.vertex_shader,
            fragment_shader=self.shader.fragment_shader,
            layout=layout,
            resources=resources,
            framebuffer=self.FBO.get_FBO(),
            topology="triangles",
            viewport=self.FBO.get_viewport(),
            vertex_buffers=buffers,
            vertex_count=self.VBO.vbo.size // zengl.calcsize(self.VBO.format),
            cull_face=self.VBO.cull_face,
            blend=self.shader.blend_data,
            instance_count=instance_count,
            depth={
                "write": True,
                "func": "lequal",
            },
        )

    def reload_shaders(self):
        self.construct_pipeline()


    def texture_bind(self, binding:int, name:str, image:"Texture"):
        if image.auto_mipmaps:
            image.data.mipmaps()
    
        if ( image.filter[0].startswith("linear") or
             image.filter[1].startswith("linear") ):
            self.resources[binding + self.ptb] = \
            {
                "type": "sampler",
                "binding": binding,
                "image": image.data,
                "min_filter": image.filter[0],
                "mag_filter": image.filter[1],
                "wrap_x": image.repeat[0],  # clamp_to_edge == you need to give 0 - 1
                "wrap_y": image.repeat[1],  # repeat == automatically repeats texture
                'max_anisotropy': self.max_anisotropy,
                'lod_bias': self.lod_bias,
            }
        else:
            self.resources[binding + self.ptb] = \
            {
                "type": "sampler",
                "binding": binding,
                "image": image.data,
                "min_filter": image.filter[0],
                "mag_filter": image.filter[1],
                "wrap_x": image.repeat[0],  # clamp_to_edge == you need to give 0 - 1
                "wrap_y": image.repeat[1],  # repeat == automatically repeats texture
            }
            
        self.layout[binding + self.ptb] = {"name": name, "binding": binding}
        
        self.please_update = True

    def render(self, instance_count:int=1):
        if self.please_update:
            self.reconstruct_pipeline(instance_count)
            
        self.pipeline.render()

    def uniform_bind(self, name, value): # FOR UPDATING INCLUDES
        try:
            self.uniform_buffer.write(value, offset=self.uniforms[name])
        except: # UH OH, ITS NOT IN THE BUFFER. DO SOMETHING ABOUT IT
            print("OPTIMIZE YOUR CODE NEXT TIME", name, value)

    @staticmethod
    def pack_uniforms(uniforms_map):
        uniforms = {}
        layout = ""
        offset = 0
        
        # TO READER, PLEASE MAKE THIS SWITCH CASE
        # WARNING :-:-: TACTICAL CODEMESS INCOMING 
        for uf_name, uf_data in uniforms_map.items():
            data_type = uf_data
            v = len(uf_data)-1
            if uf_data == "float":
                size = 4  # Size of a float in bytes
                align = 4
            elif uf_data == "vec2":
                size = 8  # 2 floats
                align = 8
            elif uf_data == "vec3":
                size = 12  # 3 floats, but aligned as vec4 in std140 layout
                align = 16
            elif uf_data == "vec4":
                size = 16  # 4 floats
                align = 16
                
            elif uf_data == "mat2":
                size = 16  # 2x2 floats
                align = 16  # aligned as vec4 in std140 layout
            elif uf_data == "mat3":
                size = 36  # 3x3 floats, but aligned as mat4 in std140 layout
                align = 64  # aligned as mat4 in std140 layout
            elif uf_data == "mat4":
                size = 64  # 4x4 floats
                align = 64
              
            elif uf_data == "int":
                size = 4  # 1 i32
                align = 4
            elif uf_data == "ivec2":
                size = 8  # 2 i32
                align = 8
            elif uf_data == "ivec3":
                size = 12  # 3 i32
                align = 16
            elif uf_data == "ivec4":
                size = 16  # 4 i32
                align = 16
              
            elif uf_data == "imat2":
                size = 16  # 2x2 ints
                align = 16  # aligned as vec4 in std140 layout
            elif uf_data == "imat3":
                size = 36  # 3x3 ints, but aligned as ivec4 in std140 layout
                align = 64  # aligned as imat4 in std140 layout
            elif uf_data == "imat4":
                size = 64  # 4x4 ints
                align = 64
            elif data_type == 'bool':
                size = 1
                align = 4
                
                
            elif data_type.startswith("float"):
                arr_size = data_type[6:v]
                size  = 4 * int(arr_size)
                align = 4
            elif data_type.startswith("vec2"):
                arr_size = data_type[5:v]
                size  = 8 * int(arr_size)
                align = 8
            elif data_type.startswith("vec3"):
                arr_size = data_type[5:v]
                size  = 16 * int(arr_size)
                align = 16
            elif data_type.startswith("vec4"):
                arr_size = data_type[5:v]
                size  = 16 * int(arr_size)
                align = 16

            elif data_type.startswith("mat2"):
                arr_size = data_type[5:v]
                size  = 16 * int(arr_size)
                align = 16  # aligned as vec4 in std140 layout
            elif data_type.startswith("mat3"):
                arr_size = data_type[5:v]
                size  = 64 * int(arr_size)
                align = 64  # aligned as mat4 in std140 layout
            elif data_type.startswith("mat4"):
                arr_size = data_type[5:v]
                size  = 64 * int(arr_size)
                align = 64
              
            elif data_type.startswith("int"):
                arr_size = data_type[5:v]
                size  = 4 * int(arr_size)
                align = 4
            elif data_type.startswith("ivec2"):
                arr_size = data_type[5:v]
                size  = 8 * int(arr_size)
                align = 8
            elif data_type.startswith("ivec3"):
                arr_size = data_type[5:v]
                size  = 16 * int(arr_size)
                align = 16
            elif data_type.startswith("ivec4"):
                arr_size = data_type[5:v]
                size  = 16 * int(arr_size)
                align = 16

            elif data_type.startswith("imat2"):
                arr_size = data_type[5:v]
                size  = 8 * int(arr_size)
                align = 8  # aligned as vec4 in std140 layout
            elif data_type.startswith("imat3"):
                arr_size = data_type[5:v]
                size  = 64 * int(arr_size)
                align = 64  # aligned as mat4 in std140 layout
            elif data_type.startswith("imat4"):
                arr_size = data_type[5:v]
                size  = 64 * int(arr_size)
                align = 64
              
            else:
                raise NotImplementedError(
                    f"Either unknown GLSL type: {uf_data['glsl_type']} or not Implemented"
                )

            # Add padding for alignment
            if offset % align != 0:
                offset += align - (offset % align)

            uniforms[uf_name] = offset
            offset += size
            layout += f"{uf_data} {uf_name};\n"

        includes = f"""
                layout (std140) uniform Common {{{layout if uniforms else 'float dummy;'}}};
            """
        buffer_size = 16 + offset
        return uniforms, buffer_size, {"uniforms": includes.strip()}
        
    def destroy(self):
        self.ctx.release(self.pipeline)
        self.ctx.release(self.uniform_buffer)
        self.ctx.release(self.NUL_IMG)


class VAOs:
    def __init__(self, ctx:"zengl.Context"):
        self.ctx:"zengl.Context" = ctx
        self.Framebuffers:Framebuffers = Framebuffers(self.ctx)
        self.vbo:VBOs = VBOs(ctx)
        self.program:ShaderPrograms = ShaderPrograms()
        self.vaos:Dict[str, VAO] = {}
        """
        # cube vao
        self.vaos['cube'] = self.get_vao(
            program=self.program.programs['default'],
            vbo = self.vbo.vbos['cube'])"""
        
        
        # background vao
        self.add_vao(
            vao_name="background",
            fbo=self.Framebuffers.framebuffers["default"],
            program=self.program.programs['background'],
            vbo=self.vbo.vbos['plane'],
            umap=
			{ 
				"u_color_offset": "vec3",
				"screenResolution": "vec2",
				"mos": "vec2",
			},
            tmap=["U_bg_image"],
        )
        
        """
        # screen resizer vao
        self.vaos['screener'] = self.get_vao(
            program=self.program.programs['resizer'],
            vbo=self.vbo.vbos['cube'])"""
        

    def get_vao(self, program, fbo, vbo, umap={}, tmap=[]):
        vao = VAO(self.ctx, program, fbo, vbo, uniforms_map=umap, textures_names=tmap)
        return vao
    
    def get_ins_vao(self, program, fbo, vbo, ibo, umap={}, tmap=[], instance_count=1):
        vao = VAO(self.ctx, program, fbo, vbo, ibo, umap, tmap, instance_count)
        return vao
        
        

    def add_vao(self, vao_name, program, fbo, vbo, umap={}, tmap=[]):
        self.vaos[vao_name] = VAO(self.ctx, program, fbo, vbo, uniforms_map=umap, textures_names=tmap)
    
    def add_ins_vao(self, vao_name, program, fbo, vbo, ibo, umap={}, tmap=[], instance_count=1):
        self.vaos[vao_name] = VAO(self.ctx, program, fbo, vbo, ibo, umap, tmap, instance_count)
        
        
    
    def del_vao(self, vao_name):
        self.vaos[vao_name].destroy()
        del self.vaos[vao_name]
        

    def destroy(self):
        [vao.destroy() for vao in self.vaos.values()]
        self.vbo.destroy()
        self.program.destroy()