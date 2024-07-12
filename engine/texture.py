import pygame as pg
import sys, time, os
from typing import Dict, List, Tuple, Any


class Texture:
    def __init__(
        self,
        image:"zengl.Image",
        filter:Tuple[str, str] = ("nearest", "nearest"),
        repeat:Tuple[str, str] = ("repeat", "repeat"),
        mipmap_levels:int=1,
        max_anisotropy:float=1.0,
        lod_bias:float=0.0,
        auto_mipmaps=False,
    ):
        self.data = image
        
        # IMPORTANT
        self.filter = filter
        self.repeat = repeat
        
        # MIPMAPS
        self.mipmap_levels = mipmap_levels
        self.max_anisotropy = max_anisotropy
        self.lod_bias = lod_bias
        self.auto_mipmaps = auto_mipmaps
        
    def destroy(self, ctx:"zengl.Context"):
        ctx.release(self.data)
        
        

class Textures:
    def __init__(self, ctx:"zengl.Context"):
        self.ctx = ctx
        self.textures:Dict[str, Texture] = {}
        self.textures["plant1"] = self.get_texture("assets/textures/plant1.png")
        self.textures["plant2"] = self.get_texture("assets/textures/proccessed.png")
        
        self.textures["sun"] = self.get_texture("assets/textures/albasee.png")
        self.textures["normal"] = self.get_texture("assets/textures/normal.png")
        self.textures["uv"] = self.get_texture("assets/textures/uv.png")
        
        
        self.textures["player"] = self.get_texture_array("assets/textures/player/")

    def from_surface(self, surface: "pg.Surface"):
        texture = pg.transform.flip(surface, flip_x=False, flip_y=True)
        texture = self.ctx.image(
            size=texture.get_size(),
            format="rgba8unorm",
            data=pg.image.tostring(texture, "RGBA"),
            texture=True,
            cubemap=False,
            samples=1,
        )
        return Texture(texture)

    def get_texture(self, path:str,
        filter:Tuple[str, str] = ("nearest", "nearest"),
        repeat:Tuple[str, str] = ("repeat", "repeat"),
        mipmaps:Tuple[str, str] = (0, 0),
        max_anisotropy:float=1.0,
        lod_bias:float=0.0,
        auto_mipmaps:bool=False,
    ):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.image(size=texture.get_size(), format="rgba8unorm",
                                data=pg.image.tostring(texture, 'RGBA'), texture=True,
                                cubemap=False, samples=1)
        #texture.mipmaps(0, 64)
        return Texture(texture, filter, repeat, mipmaps)
        
        
    def from_buffer(self, Image:"zengl.Image",
        filter:Tuple[str, str] = ("nearest", "nearest"),
        repeat:Tuple[str, str] = ("repeat", "repeat"),
        mipmaps:Tuple[str, str] = (0, 0),
        max_anisotropy:float=1.0,
        lod_bias:float=0.0,
        auto_mipmaps:bool=False,
    ):
        #texture.mipmaps(0, 64)
        return Texture(Image, filter, repeat, mipmaps)
        
        
    @staticmethod
    def order(x):
        order = ['Albasee', 'Vulakit', 'AlbaseeBG', 'VulakitBasalt']
        return sum([i*512 if x.startswith(order[i]) else 0 for i in range( len(order) ) ])


    def get_texture_array(self, path:str,
        filter = ("nearest", "nearest"),
        repeat = ("repeat", "repeat"),
        mipmaps = (0, 0),
        max_anisotropy = 1.0,
        lod_bias = 0.0,
        auto_mipmaps = False,
    ):
        textures = [] 
        for texture in sorted(os.listdir(path), key= lambda x : self.order(x) + len(x) ):
            textures.append(path + texture)
            
        
        t_size = pg.image.load(path + texture).get_size()
        tex_array = self.ctx.image(size=(t_size[0], t_size[1]), format="rgba8unorm", 
            samples=1,
            array=len(textures))
            
        for index, texture_path in enumerate(textures):
            texture = pg.image.load(texture_path).convert()
            texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
            texture = self.ctx.image(size=texture.get_size(), format="rgba8unorm",
                                    data=pg.image.tostring(texture, 'RGBA'), texture=True,
                                    cubemap=False, samples=1)
                                    

            tex_array.write(texture.read(), offset=(0, 0), size=(t_size[0], t_size[1]), layer=index)


        return Texture(
            image=tex_array, 
            filter=filter,
            repeat=repeat,
            mipmap_levels=mipmaps,
            max_anisotropy=max_anisotropy,
            lod_bias=lod_bias,
            auto_mipmaps=auto_mipmaps,
        )
        
        
        
        
    def add_texture(self, texture_name:str,
        path:str,
        filter = ("nearest", "nearest"),
        repeat = ("repeat", "repeat"),
        mipmaps = (0, 0),
        max_anisotropy = 1.0,
        lod_bias = 0.0,
        auto_mipmaps = False,
    ):
        self.textures[texture_name] = self.get_texture(
            image=tex_array, 
            filter=filter,
            repeat=repeat,
            mipmap_levels=mipmaps,
            max_anisotropy=max_anisotropy,
            lod_bias=lod_bias,
            auto_mipmaps=auto_mipmaps,
        )
        
        
    def add_texture_array(self, 
        texture_name:str,
        path:str,
        filter = ("nearest", "nearest"),
        repeat = ("repeat", "repeat"),
        mipmaps = (0, 0),
        max_anisotropy = 1.0,
        lod_bias = 0.0,
        auto_mipmaps = False,
    ):
        self.textures[texture_name] = self.get_texture_array(
            image=tex_array,
            filter=filter,
            repeat=repeat,
            mipmap_levels=mipmaps,
            max_anisotropy=max_anisotropy,
            lod_bias=lod_bias,
            auto_mipmaps=auto_mipmaps,
        )
        
    def del_texture(self, texture_name:str):
        self.textures[texture_name].destroy(self.ctx)
        del self.textures[texture_name]

    def destroy(self):
        [tex.destroy(self.ctx) for tex in self.textures.values()]
