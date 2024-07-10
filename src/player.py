import pygame as pg
import glm
import struct
import math
from bindings import *

neighbor_offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

class RigidBody:
    def __init__(self):
        self.rect = pg.FRect(0, 0, 16, 16)
        self.velocity = [0, 0]
        self.collision_types = {'bottom': False, 'top': False, 'right': False, 'left': False}
        self.coyote_time = 0
        self.coyote_time_wall = 0
        self.elasticity = 0
        self.friction = [1.0, 0.5]

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
        do_gravity = 392
        clamp_gravity = 300

        hit_list = self.collision_test(self.rect, tilemap)

        for block in hit_list:
            if self.velocity[0] > 0:
                self.rect.right = block.left
                self.collision_types['left'] = True
                if self.move > 0.275:
                    self.coyote_time_wall = 0

            if self.velocity[0] < 0:
                self.rect.left = block.right
                self.collision_types['right'] = True
                if self.move > 0.275:
                    self.coyote_time_wall = 0

            if self.friction[1] == 0 or self.friction[1] == 1:
                self.velocity[1] -= self.velocity[1] * self.friction[1]
            else:
                self.velocity[1] -= self.velocity[1] * self.friction[1] * dt
                clamp_gravity *= (1-self.friction[1])
                do_gravity *= (1-self.friction[1])
                
            self.velocity[0] = -self.velocity[0] * self.elasticity
        
            break

        self.rect.y += self.velocity[1] * dt
        hit_list = self.collision_test(self.rect, tilemap)
        
        self.velocity[1] -= do_gravity * dt
        self.velocity[1] = max(min(self.velocity[1], clamp_gravity), -clamp_gravity)
        
        for block in hit_list:
            if self.velocity[1] < 0:
                self.rect.top = block.bottom
                self.collision_types['bottom'] = True
                self.coyote_time = 0

            if self.velocity[1] > 0:
                self.rect.bottom = block.top
                self.collision_types['top'] = True


            if self.friction[0] == 0 or self.friction[0] == 1:
                self.velocity[0] -= self.velocity[0] * self.friction[0]
            else:
                self.velocity[0] -= self.velocity[0] * self.friction[0] * dt
            
            
            self.velocity[1] = -self.velocity[1] * self.elasticity
            break
            
        
        
        

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
        self.rect = pg.FRect(900, 0, 15, 16)
        self.roll = 0
        self.scale = glm.vec2(8)
        self.boxcam = glm.vec2(0)
        self.frame = 0
        self.time_since_lastframe = 0
        self.move = 1

    def check(self, keys):
        # self.velocity[0] = 0
        MAX_SPED = 100 if self.move > 0.275 else 1
        ACC_SPED = 200
        MAX_ACCEL = glm.clamp(ACC_SPED-abs(self.velocity[0]), 0, MAX_SPED)
        
        MAX_WINDSPED = 50 if self.move > 0.275 else 1
        ACC_WINDSPED = 100
        MAX_WINDACCEL = glm.clamp(ACC_WINDSPED-abs(self.velocity[0]), 0, MAX_WINDSPED)

        if keys[bindings['left']] and keys[bindings['right']]:
            pass

        elif keys[bindings['right']]:
            self.velocity[0] += MAX_ACCEL if self.coyote_time < 0.1 else MAX_WINDACCEL

        elif keys[bindings['left']]:
            self.velocity[0] -= MAX_ACCEL if self.coyote_time < 0.1 else MAX_WINDACCEL

        if self.coyote_time < 0.1 and keys[bindings['jump']]:
            self.velocity[1] = 200
            self.coyote_time = 100
            
        elif self.coyote_time_wall < 0.1 and pg.key.get_just_pressed()[bindings['jump']]:
            self.velocity[1] = 150
            self.velocity[0] = -240 if self.collision_types['left'] else 240
            self.coyote_time_wall = 100
            self.move = 0
            
            
            
    def update(self):
        self.apply_physics(self.app.share_data['tilemap'].tilemap['0'], self.app.delta_time)
        self.check(pg.key.get_pressed())
        self.coyote_time += self.app.delta_time
        self.coyote_time_wall += self.app.delta_time
        
        self.boxcam = glm.clamp(self.boxcam, glm.vec2(-30), glm.vec2(30))
        self.boxcam += self.pos.xy - glm.vec2(self.rect.x-1, self.rect.y)
        
        self.pos = glm.vec3(self.rect[0]-1, self.rect[1], 0)
        
        
        
        self.app.camera.position.xy = self.pos.xy + self.boxcam
        self.m_model = self.get_model_matrix()
        
        self.time_since_lastframe += self.app.delta_time
        if self.time_since_lastframe > 0.288:
            self.frame += 1
            self.frame = self.frame%4
            self.time_since_lastframe = 0
            
        self.move += self.app.delta_time
        
        self.vao.uniform_bind("m_model", self.m_model.to_bytes())
        self.vao.uniform_bind("frame", struct.pack("i", self.frame))
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
    
