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
            if keys[pg.K_q]:
                self.position += self.forward * velocity
            if keys[pg.K_e]:
                self.position -= self.forward * velocity
            if keys[pg.K_a]:
                self.position -= self.right * velocity
            if keys[pg.K_d]:
                self.position += self.right * velocity
            if keys[pg.K_w]:
                self.position += self.up * velocity
            if keys[pg.K_s]:
                self.position -= self.up * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + glm.vec3(0, 0, -1), self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(90), 4/3, 1, 1000)