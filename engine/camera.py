import glm
import pygame as pg

FOV = 90  # deg
NEAR = 0
FAR = 1000
SENSITIVITY = 0.0


class Camera:
    def __init__(self, app, position=(600, 0, 120), yaw=-90, pitch=0):
        self.app = app
        self.SPEED = 40
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(position)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.roll = 0
        # view matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        self.freemove = True
        self.no_paralax = False

    def update_camera_vectors(self):
        roll = glm.radians(self.roll)

        self.up = glm.normalize(glm.vec3(glm.sin(roll), glm.cos(roll), 0))
        self.right = glm.normalize(self.up.yxz * glm.vec3(1, -1, 0))

    def update(self):
        self.move()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self):
        if self.freemove:
            velocity = self.SPEED * self.app.delta_time
            keys = pg.key.get_pressed()
            offset = glm.vec3()
            if keys[pg.K_q]:
                offset += self.forward
                # self.position += self.forward * velocity
            if keys[pg.K_e]:
                offset -= self.forward
                # self.position -= self.forward * velocity
            if keys[pg.K_a]:
                offset -= self.right
                # self.position -= self.right * velocity
            if keys[pg.K_d]:
                offset += self.right
                # self.position += self.right * velocity
            if keys[pg.K_w]:
                offset += self.up
                # self.position += self.up * velocity
            if keys[pg.K_s]:
                offset -= self.up
                # self.position -= self.up * velocity
            if glm.length(offset) > 0:
                offset = glm.normalize(offset)
            self.position += offset * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + glm.vec3(0, 0, -1), self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(90), 4/3, 1, 1000)