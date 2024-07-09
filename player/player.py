from player.rigidBody import RigidBody
from bindings import *

class Player(RigidBody):
    def __init__(self):
        super().__init__()

    def check(self, keys):
        self.velocity[0] = 0

        if keys[bindings['left']] and keys[bindings['right']]:
            self.velocity[0] = 0

        elif keys[bindings['right']]:
            self.velocity[0] = 100

        elif keys[bindings['left']]:
            self.velocity[0] = -100

        if self.collision_types['bottom'] and keys[bindings['jump']]:
            self.velocity[1] = -300

        
