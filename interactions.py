__author__ = 'nickdg'

import ratcave.graphics as graphics
from ratcave.utils import timers

class Spinner(graphics.Physical):

    def __init__(self, velocity=1., axis=1, *args, **kwargs):
        """Spins in direction "axis" with speed "velocity" when Spinner.update_physics(dt) is called!"""
        super(Spinner, self).__init__(*args, **kwargs)

        self.velocity = 0.
        self.spin_velocity = velocity
        self.axis = axis

    def start(self):
        self.velocity = self.spin_velocity

    def update(self, dt):

        rotation = list(self.rotation)
        rotation[self.axis] += self.velocity * dt
        self.rotation = rotation



class Jumper(graphics.Physical):

    def __init__(self, jump_velocity=2., gravity_coeff=-2.2, *args, **kwargs):
        super(Jumper, self).__init__(*args, **kwargs)

        self.floor_height = self.position[1]
        self.gravity_coeff = gravity_coeff
        self.jump_velocity = jump_velocity
        self.velocity = 0.

    def start(self):

        # Reset to floor height (to prevent air-jumping)
        if self.position[1] <= self.floor_height:
            self.position[1] = self.floor_height
            self.velocity = self.jump_velocity

    def update(self, dt):

        # if in the air, update position via gravitational constant
        if self.position[1] > self.floor_height:
            self.velocity += (self.gravity_coeff * dt)
            self.position[1] += (self.velocity * dt)
        else:
            self.velocity = 0.



