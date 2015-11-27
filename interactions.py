import ratcave.graphics as graphics
from ratcave.utils import timers
import random


class Spinner(graphics.Physical):

    def __init__(self, spin_velocity=45., axis=1, *args, **kwargs):
        """Spins in direction "axis" with speed "velocity" when Spinner.update_physics(dt) is called!"""
        super(Spinner, self).__init__(*args, **kwargs)

        self.velocity = 0.
        self.spin_velocity = spin_velocity
        self.axis = axis
        self.timer = timers.countdown_timer(0)

    def start(self):
        if self.velocity:
            self.timer = timers.countdown_timer(2.)
        else:
            self.velocity = self.spin_velocity * random.choice([1., -1.])


    def update(self, dt):
        # Keep spinning if timeout hasn't completed.
        if self.timer.next() > 0.:
            self.rot_y += self.velocity * dt


class Jumper(graphics.Physical):

    def __init__(self, jump_velocity=1., gravity_coeff=-5.5, *args, **kwargs):
        """Jumps with jump_velocity, coming back down at rate gravity_coeff."""
        super(Jumper, self).__init__(*args, **kwargs)

        self.floor_height = self.y
        self.gravity_coeff = gravity_coeff
        self.jump_velocity = jump_velocity
        self.velocity = 0.

    def start(self):

        # Reset to floor height (to prevent air-jumping)
        if self.y <= self.floor_height:
            self.y = self.floor_height
            self.velocity = self.jump_velocity
            self.y = self.floor_height + .005

    def update(self, dt):

        # if in the air, update position via gravitational constant
        if self.y > self.floor_height:
            self.velocity += (self.gravity_coeff * dt)
            self.y += (self.velocity * dt)
        else:
            self.velocity = 0.


class Scaler(graphics.Physical):

    def __init__(self, end_scale=.5, scale_velocity=.01, *args, **kwargs):
        """Grows and Shrinks between its scale and the end_scale (relative to its current scale) endpoints with speed scale_velocity."""

        super(Scaler, self).__init__(*args, **kwargs)
        self.scale_endpoints = tuple(sorted((self.scale, self.scale * end_scale)))
        self.scale_velocity = scale_velocity
        self.scale_direction = -1 if end_scale < self.scale else 1.
        self.timer = timers.countdown_timer(0)

    def start(self):
        self.timer = timers.countdown_timer(2.)

    def update(self, dt):

        if self.timer.next() > 0.:

            # When it reaches the end of the scale range, flip the direction
            if self.scale < self.scale_endpoints[0] or self.scale > self.scale_endpoints[1]:
                self.scale_direction *= -1

            # Set New Scale
            self.scale += self.scale_direction * self.scale_velocity * dt
