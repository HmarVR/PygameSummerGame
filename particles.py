from player.rigidBody import *

class Particle(RigidBody):
    def __init__(self):
        super().__init__()
        self.elasticity = -1
        self.friction = float('inf')
        self.life = 1
        self.max_life = 1
        self.radius = 5
        self.color = (255, 255, 255)

    def pos(self, scroll = [0, 0]):
        return self.rect.center[0] + scroll[0], self.rect.center[1] + scroll[1]

class ParticleManager:
    def __init__(self):
        self.particles = []

    def update_particles(self, display, tilemap, scroll, dt):
        for particle in self.particles[:]:
            particle.velocity[1] += 500 * dt
            particle.life -= dt
            particle.apply_physics(tilemap, dt)
            pg.draw.circle(display, particle.color, particle.pos(scroll), particle.radius * (particle.life / particle.max_life))
            particle.rect.w = particle.radius * (particle.life / particle.max_life) / 2
            particle.rect.h = particle.radius * (particle.life / particle.max_life) / 2

            if particle.life <= 0:
                self.particles.remove(particle)

    def add(self, pos, radius, color, velocity, life):
        p = Particle()
        p.velocity = velocity
        p.color = color
        p.life = life
        p.max_life = life
        p.radius = radius
        p.rect.center = pos
        p.rect.w, p.rect.h = radius*2, radius*2
        self.particles.append(p)