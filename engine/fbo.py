from typing import TYPE_CHECKING, Dict, List, Tuple

class Framebuffer:
    def __init__(self, ctx, depth_out:"zengl.Image", image_out:List["zengl.Image"], **future_stuff): # future stuff like mesh shading, not nessacary for now so not doin it
        self.image_out = image_out
        self.depth_out = depth_out
        
    def get_FBO(self):
        return [*self.image_out, self.depth_out]
        
    def get_viewport(self):
        return (0, 0, *self.image_out[0].size)

    def destroy(self, ctx): # Goodbye world
        ctx.release(self.image_out)
        ctx.release(self.depth_out)

class Framebuffers:
    def __init__(self, ctx:"zengl.Context"):
        self.ctx = ctx
    
        self.framebuffers:Dict[str, Framebuffer] = {}
        self.framebuffers['default'] = self.get_framebuffer((640, 480))

    def get_framebuffer(
        self,
        resolution:Tuple[int, int],
        samples:int=1,
        depth_type:str="depth24plus",
        color_type:List[str]=["rgba8unorm"], 
    ):
        image_out = [self.ctx.image(resolution, color_type[i], samples=samples) for i in range(len(color_type))]
        depth_out = self.ctx.image(resolution, depth_type, samples=samples)
        
        program = Framebuffer(ctx=self.ctx, depth_out=depth_out, image_out=image_out)
        return program
        
    def add_framebuffer(
        self, 
        framebuffer_name:str,
        resolution:Tuple[int, int],
        samples:int=1,
        depth_type="depth24plus",
        color_type:List[str]=["rgba8unorm"], 
    ):
        self.framebuffers[framebuffer_name] = self.get_framebuffer(resolution, samples, depth_type, color_type)
        
    def del_framebuffer(self, framebuffer_name:str):
        self.framebuffers[framebuffer_name].destroy(self.ctx)
        del self.framebuffers[framebuffer_name]

    def destroy(self):
        [self.del_framebuffer(program) for program in self.programs.values()] # Ehh why not
        del self