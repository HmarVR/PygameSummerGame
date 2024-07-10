class Shader:
    def __init__(self, vertex_shader, fragment_shader, **future_stuff): # future stuff like mesh shading, not nessacary for now so not doin it
        self.vertex_shader   = vertex_shader
        self.fragment_shader = fragment_shader
        
        self.blend_data = {
            "enable": True,
            "src_color": "src_alpha",
            "dst_color": "one_minus_src_alpha",
        }

    def destroy(self): # Goodbye world
        del self.vertex_shader, self.fragment_shader

class ShaderPrograms:
    def __init__(self):
        self.programs = {}
        self.programs['default'] = self.get_program('default')
        self.programs['planet'] = self.get_program('planet')
        self.programs['player'] = self.get_program('player')
        self.programs['ui'] = self.get_program('ui')
        self.programs['main_menu_ui'] = self.get_program('main_menu_ui')
        self.programs['tilemap'] = self.get_program('tilemap') # TODO: make shader
        self.programs['background'] = self.get_program('background') # TODO: make shader
        self.programs['post_process'] = self.get_program('post_process')

    def get_program(self, shader_program_name):
        with open(f'shaders/{shader_program_name}.vert.glsl') as file:
            vertex_shader = file.read()
        
        
        with open(f'shaders/{shader_program_name}.frag.glsl') as file:
            fragment_shader = file.read()
        
        
        program = Shader(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program
        
    def add_program(self, shader_program_name): # called on startup
        self.programs[shader_program_name] = self.get_program('shader_program_name')
        
    def del_program(self, shader_program_name): # called on startup
        self.programs[shader_program_name].destroy()
        del self.programs[shader_program_name]

    def destroy(self):
        [program.destroy() for program in self.programs.values()] # Ehh why not
        del self.programs
        del self