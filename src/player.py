import pygame as pg
import glm
import struct
import math
from typing import List, Dict, Tuple
from bindings import *

IDLE_KEYFRAMES = [0.28 for _ in range(4)]
WALK_KEYFRAMES = [0.12 for _ in range(4)]
SLIDE_KEYFRAMES = [0.1]
FALL_KEYFRAMES = [0.1]
JUMP_KEYFRAMES = [0.1]

neighbor_offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

class RigidBody:
    def __init__(self):
        self.rect = pg.FRect(0, 0, 15, 15)
        self.velocity = glm.vec2(0, 0)
        self.collision_types = {'bottom': False, 'top': False, 'right': False, 'left': False}
        self.coyote_time = 0
        self.coyote_time_wall = 0
        self.elasticity = [0.1, 0.1]
        self.friction = [12.0, 2.75]

    def get_neighboring_tiles(self, tilemap:"Tilemap"):
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

    def collision_test(self, rect, tileset:"Tilemap"):
        hit_list = []
        
        for tile in self.get_neighboring_tiles(tileset):
            if rect.colliderect(tile):
                hit_list.append(tile)

        return hit_list

    def apply_physics(self, tilemap:"Tilemap", dt:float):
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

            self.velocity[1] *= math.exp(-self.friction[1] * dt)
                
            self.velocity[0] = -self.velocity[0] * self.elasticity[0]
            self.velocity[0] = 0 if (self.velocity[0]<1.5 and self.velocity[0]>-1.5) else self.velocity[0]
        
            break

        self.rect.y += self.velocity[1] * dt
        hit_list = self.collision_test(self.rect, tilemap)
        
        self.velocity[1] -= do_gravity * dt
        
        for block in hit_list:
            if self.velocity[1] < 0:
                self.rect.top = block.bottom
                self.collision_types['bottom'] = True
                self.coyote_time = 0

            if self.velocity[1] > 0:
                self.rect.bottom = block.top
                self.collision_types['top'] = True


            self.velocity[0] *= math.exp(-self.friction[0] * dt)
        
            
            self.velocity[1] = -self.velocity[1] * self.elasticity[1]
            self.velocity[1] = 0 if (self.velocity[1]<1 and self.velocity[1]>-1) else self.velocity[1]
            break
            
        self.velocity[1] = max(self.velocity[1], -clamp_gravity)
        
        
        

class Player(RigidBody):
    def __init__(self, app:"Game"):
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
                "flip": "bool",
			},
            tmap=["u_texture_0"],
        )
        self.vao = self.app.mesh.vao.vaos['player']
        
        self.texture = self.app.mesh.texture.textures["player"]
        self.vao.texture_bind(0, "u_texture_0", self.texture)
        
        self.pos = glm.vec3(902, 0, 0)
        self.rect = pg.FRect(902, 0, 14, 15)
        self.roll = 0
        self.scale = glm.vec2(7.5)
        self.boxcam = glm.vec2(0)
        self.idle_animation = Animation(IDLE_KEYFRAMES)
        self.walk_animation = Animation(WALK_KEYFRAMES)
        self.slide_animation = Animation(SLIDE_KEYFRAMES)
        self.fall_animation = Animation(FALL_KEYFRAMES)
        self.jump_animation = Animation(JUMP_KEYFRAMES)
        self.animations = [
            self.idle_animation, 
            self.walk_animation, 
            self.slide_animation, 
            self.fall_animation, 
            self.jump_animation, 
        ]
        self.animation_manager = AnimationManager(self.animations)
        self.move = 1
        self.flip = False

    def check(self, keys):
        # self.velocity[0] = 0
        MAX_SPED = 900 if self.move > 0.275 else 1
        ACC_SPED = 800
        
        MAX_WINDSPED = 200 if self.move > 0.275 else 1
        ACC_WINDSPED = 170
        
        input_velocity = glm.vec2(0)
        
        if keys[bindings['left']] and keys[bindings['right']]:
            self.elasticity[0] = 0.0 # yea now pressin both buttons does something

        elif keys[bindings['right']]:
            self.elasticity[0] = 0.0
            input_velocity.x += (ACC_SPED if self.coyote_time < 0.1 else ACC_WINDSPED) * self.app.delta_time
            # TO NON-CALCULUS PEOPLE: because of chain rule this should be dP/dT
            self.flip = False

        elif keys[bindings['left']]:
            self.elasticity[0] = 0.0
            input_velocity.x -= (ACC_SPED if self.coyote_time < 0.1 else ACC_WINDSPED) * self.app.delta_time
            # TO NON-CALCULUS PEOPLE: because of chain rule this should be dP/dT
            self.flip = True
            
        
        # Calculate potential new velocity
        potential_velocity = self.velocity.x + input_velocity.x
        MAX_SPEED = MAX_SPED if self.coyote_time < 0.1 else MAX_WINDSPED

        # Cap the input velocity if potential velocity exceeds MAX_SPEED
        if glm.length(potential_velocity) > MAX_SPEED:
            if glm.length(self.velocity.x) < MAX_SPEED:
                max_addition = MAX_SPEED - glm.length(self.velocity[0])
                if glm.length(input_velocity.x) > 0:
                    input_velocity = glm.normalize(input_velocity) * max_addition
            else:
                # Well just allow them to descelerate
                max_addition = -MAX_SPEED + glm.length(self.velocity.x)
                if self.velocity.x >= MAX_SPEED and input_velocity.x < 0 and self.move > 0.275:
                    input_velocity = glm.normalize(input_velocity) * max_addition
                elif self.velocity.x <= -MAX_SPEED and input_velocity.x > 0 and self.move > 0.275:
                    input_velocity = glm.normalize(input_velocity) * max_addition
                else:
                    input_velocity = glm.vec2(0)
                    
        self.velocity.x += glm.clamp(input_velocity.x, -MAX_SPEED, MAX_SPEED)

        if self.coyote_time < 0.1 and keys[bindings['jump']]:
            self.velocity.y = 200
            self.coyote_time = 100
            
        elif self.coyote_time_wall < 0.1 and pg.key.get_just_pressed()[bindings['jump']]:
            self.velocity.y = 145
            self.velocity.x = -160 if self.collision_types['left'] else 160
            self.coyote_time_wall = 100
            self.move = 0
            
        if self.coyote_time_wall < 0.1:
            self.animation_manager.set_animation(2)
            
            
        elif (keys[bindings['right']] and keys[bindings['left']]) and self.coyote_time < 0.1:
            self.animation_manager.set_animation(0)
            
        elif (keys[bindings['right']] or keys[bindings['left']]) and self.coyote_time < 0.1:
            self.animation_manager.set_animation(1)
            
        elif self.velocity[1] < -40:
            self.animation_manager.set_animation(3)
            
        elif self.velocity[1] > 40:
            self.animation_manager.set_animation(4)
            
        else: # my boy prolly just chillin rn am I right (gotta capitalie the I am I right)
            self.animation_manager.set_animation(0)
            
        
            
    def update(self):
        self.elasticity[0] = 0.1
        keys = pg.key.get_pressed()
        self.check(keys)
        self.apply_physics(self.app.share_data['tilemap'].tilemap['0'], self.app.delta_time)
        self.coyote_time += self.app.delta_time
        self.coyote_time_wall += self.app.delta_time
        
        self.boxcam = glm.clamp(self.boxcam, glm.vec2(-30), glm.vec2(30))
        self.boxcam += self.pos.xy - glm.vec2(self.rect.x-1, self.rect.y)
        
        self.pos = glm.vec3(self.rect[0]-1, self.rect[1], 0)
        
        
        
        self.app.camera.position.xy = self.pos.xy + self.boxcam
        self.m_model = self.get_model_matrix()
        
        
        self.animation_manager.update(self.app.delta_time)
        self.frame = self.animation_manager.get_frame()
        self.move += self.app.delta_time
        
        self.vao.uniform_bind("m_model", self.m_model.to_bytes())
        self.vao.uniform_bind("frame", struct.pack("i", self.frame))
        self.vao.uniform_bind("flip", struct.pack("?", self.flip))
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
        

class Animation:
    def __init__(self, Keyframes:List[float]):
        self.Keyframes = Keyframes
        self.currentKeyframe = 0
        self.animationTimeSoFar = 0
        self.len = len(self.Keyframes)
        self.__iterCount = 0
        
    def __len__(self) -> int:
        self.len = len(self.Keyframes)
        return self.len
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.__iterCount > self.len:
            self.__iterCount = 0
            raise StopIteration
        self.Keyframes[self.__iterCount]
        self.__iterCount += 1
    
    def update(self, dt:float):
        self.animationTimeSoFar += dt
        if self.animationTimeSoFar > self.Keyframes[self.currentKeyframe]:
            self.currentKeyframe = (self.currentKeyframe+1)%len(self.Keyframes)
            self.animationTimeSoFar = 0
            
            
class AnimationManager:
    def __init__(self, Animations:List[Animation]):
        self.Animations = Animations
        self.currentAnimation = 0
        
    
    def update(self, dt:float):
        self.Animations[self.currentAnimation].update(dt)
        
    def set_animation(self, animation_id:int):
        if self.currentAnimation != animation_id:
            self.currentAnimation = animation_id
            self.Animations[self.currentAnimation].currentKeyframe = 0
        
    def get_frame(self) -> int:
        frame = 0
        for i, e in enumerate(self.Animations):
            if i == self.currentAnimation:
                return frame+self.Animations[self.currentAnimation].currentKeyframe
            frame += len(e)
