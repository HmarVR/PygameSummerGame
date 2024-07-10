import pygame as pg
import glm
from bindings import *

neighbor_offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

class RigidBody:
    def __init__(self):
        self.rect = pg.FRect(0, 0, 13, 16)
        self.velocity = [0, 0]
        self.collision_types = {'bottom': False, 'top': False, 'right': False, 'left': False}
        self.coyote_time = 0
        self.elasticity = 0
        self.friction = 5.1

    def get_neighboring_tiles(self, tilemap):
        tiles = []
        loc = (round(self.rect.x // 16), round(self.rect.y // 16))

        for offset in neighbor_offsets:
            around_loc = f'{offset[0] + loc[0]};{offset[1] - loc[1]}'
            if around_loc in tilemap:
                if tilemap[around_loc][1]:
                    x, y = around_loc.split(';')
                    x = (int(x)) * 16
                    y = (-int(y)) * 16
                    r = pg.Rect(x, y, 16, 16)
                    tiles.append(r)
        
        return tiles

    def collision_test(self, rect, tileset):
        hit_list = []
        
        for tile in self.get_neighboring_tiles(tileset):
            if rect.colliderect(tile):
                hit_list.append(tile)

        return hit_list

    def apply_physics(self, tilemap, dt):
        self.collision_types = {'bottom': False, 'top': False, 'right': False, 'left': False}

        self.rect.x += self.velocity[0] * dt

        hit_list = self.collision_test(self.rect, tilemap)

        for block in hit_list:
            if self.velocity[0] > 0:
                self.rect.right = block.left
                self.collision_types['left'] = True

            if self.velocity[0] < 0:
                self.rect.left = block.right
                self.collision_types['right'] = True

            self.velocity[1] -= self.friction * dt
            self.velocity[0] = -self.velocity[0] * self.elasticity
        
            break

        self.rect.y += self.velocity[1] * dt
        hit_list = self.collision_test(self.rect, tilemap)
        
        do_gravity = 392
        self.velocity[1] -= do_gravity * dt
        self.velocity[1] = max(min(self.velocity[1], 300), -300)
        
        for block in hit_list:
            if self.velocity[1] < 0:
                self.rect.top = block.bottom
                self.collision_types['bottom'] = True
                self.coyote_time = 0
                do_gravity = 0

            if self.velocity[1] > 0:
                self.rect.bottom = block.top
                self.collision_types['top'] = True

            self.velocity[0] -= self.friction * dt
            self.velocity[1] = -self.velocity[1] * self.elasticity
            break
            

        self.coyote_time += dt
        
        
        

class Player(RigidBody):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
        self.app.mesh.vao.add_vao(
            vao_name="player",
            fbo=self.app.mesh.vao.Framebuffers.framebuffers["default"],
            program=self.app.mesh.vao.program.programs['player'],
            vbo=self.app.mesh.vao.vbo.vbos['plane'],
            umap=
			{ 
				"m_model": "mat4",
				"m_view": "mat4",
				"frame": "int",
			},
            tmap=["u_texture_0"],
        )
        self.vao = self.app.mesh.vao.vaos['player']
        
        self.texture = self.app.mesh.texture.textures["player"]
        self.vao.texture_bind(0, "u_texture_0", self.texture)
        
        self.pos = glm.vec3(900, 0, 0)
        self.rect = pg.FRect(902, 0, 13, 16)
        self.roll = 0
        self.scale = glm.vec2(8)
        self.boxcam = glm.vec2(0)

    def check(self, keys):
        self.velocity[0] = 0

        if keys[bindings['left']] and keys[bindings['right']]:
            self.velocity[0] = 0

        elif keys[bindings['right']]:
            self.velocity[0] = 100

        elif keys[bindings['left']]:
            self.velocity[0] = -100

        if self.coyote_time < 0.1 and keys[bindings['jump']]:
            self.velocity[1] = 200
            self.coyote_time = 100
            
            
            
    def update(self):
        self.check(pg.key.get_pressed())
        self.apply_physics(self.app.share_data['tilemap'].tilemap['0'], self.app.delta_time)
        
        self.boxcam = glm.clamp(self.boxcam, glm.vec2(-30), glm.vec2(30))
        self.boxcam += self.pos.xy - glm.vec2(self.rect.x-2, self.rect.y)
        
        self.pos = glm.vec3(self.rect[0]-2, self.rect[1], 0)
        
        
        
        self.app.camera.position.xy = self.pos.xy + self.boxcam
        self.m_model = self.get_model_matrix()
        
        self.vao.uniform_bind("m_model", self.m_model.to_bytes())
        self.vao.uniform_bind(
            "m_view",
            (self.app.camera.m_proj * self.app.camera.m_view * self.m_model).to_bytes(),
        )
        
        self.vao.render()

    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, glm.radians(self.roll), glm.vec3(0, 0, 1))
        # scale
        m_model = glm.scale(m_model, glm.vec3(self.scale[0], self.scale[1], 1))
        return m_model
    
