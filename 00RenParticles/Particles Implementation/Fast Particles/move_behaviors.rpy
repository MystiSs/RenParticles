init -1115 python in renparticles:
    import weakref
    import random


    class SimpleMove(_Behavior):
        velocity = _RequiredField()
        velocity_range = [None, None]
        xvelocity_range = None
        yvelocity_range = None

        _RENP_VEL = "_renp_simple_vel"
        _RENP_ACC = 0

        def __init__(self):
            self.velocity_range = SimpleMove.velocity_range[:]
            self._RENP_VEL = "{}_{}".format(Move._RENP_VEL, self._RENP_ACC)
            Move._RENP_ACC += 1

        @property
        def xspeed(self):
            if isinstance(self.velocity, _RequiredField):
                return None
            return self.velocity[0]

        @property
        def yspeed(self):
            if isinstance(self.velocity, _RequiredField):
                return None
            return self.velocity[1]

        @xspeed.setter
        def xspeed(self, value):
            if isinstance(self.velocity, _RequiredField):
                self.velocity = [0.0, 0.0]

            self.velocity[0] = value

        @yspeed.setter
        def yspeed(self, value):
            if isinstance(self.velocity, _RequiredField):
                self.velocity = [0.0, 0.0]

            self.velocity[1] = value

        @property
        def xvel_range(self):
            return self.velocity_range[0]

        @property
        def yvel_range(self):
            return self.velocity_range[1]

        @xvel_range.setter
        def xvel_range(self, value):
            self.velocity_range[0] = value

        @yvel_range.setter
        def yvel_range(self, value):
            self.velocity_range[1] = value

        def _get_xspeed(self):
            speed = self.xspeed
            if self.xvel_range is not None:
                speed += random.uniform(-self.xvel_range, self.xvel_range)
            return speed

        def _get_yspeed(self):
            speed = self.yspeed
            if self.yvel_range is not None:
                speed += random.uniform(-self.yvel_range, self.yvel_range)
            return speed

        def _get_velocity(self):
            return [self._get_xspeed(), self._get_yspeed()]

        def __call__(self, context):
            particle = context.particle
            delta = context.delta

            particle_data = particles_props.setdefault(particle, {})
            if self._RENP_VEL not in particle_data:
                particle_data[self._RENP_VEL] = self._get_velocity()
            velocity = particle_data[self._RENP_VEL]

            particle.x += velocity[0] * delta
            particle.y += velocity[1] * delta

            return UpdateState.Pass

    class Move(SimpleMove):
        velocity = [0.0, 0.0]
        acceleration = [0.0, 0.0]
        acceleration_range = [None, None]

        _RENP_VEL = "_renp_vel"
        _RENP_ACCL = "_renp_acc" 
        _RENP_ACC = 0

        def __init__(self):
            super(Move, self).__init__()

            self.acceleration = Move.acceleration[:]
            self.acceleration_range = Move.acceleration_range[:]
            self._RENP_VEL = "{}_{}".format(Move._RENP_VEL, self._RENP_ACC)
            self._RENP_ACCL = "{}_{}".format(Move._RENP_ACCL, self._RENP_ACC)
            Move._RENP_ACC += 1

        @property
        def xacceleration(self):
            if isinstance(self.acceleration, _RequiredField):
                return None
            return self.acceleration[0]

        @property
        def yacceleration(self):
            if isinstance(self.acceleration, _RequiredField):
                return None
            return self.acceleration[1]

        @xacceleration.setter
        def xacceleration(self, value):
            if isinstance(self.acceleration, _RequiredField):
                self.velocity = [0.0, 0.0]

            self.acceleration[0] = value

        @yacceleration.setter
        def yacceleration(self, value):
            if isinstance(self.acceleration, _RequiredField):
                self.acceleration = [0.0, 0.0]

            self.acceleration[1] = value

        @property
        def xacc_range(self):
            return self.acceleration_range[0]

        @property
        def yacc_range(self):
            return self.acceleration_range[1]

        @xacc_range.setter
        def xacc_range(self, value):
            self.acceleration_range[0] = value

        @yacc_range.setter
        def yacc_range(self, value):
            self.acceleration_range[1] = value

        def _get_xacc(self):
            acc = self.xacceleration
            if self.xacc_range is not None:
                acc += random.uniform(-self.xacc_range, self.xacc_range)
            return acc

        def _get_yacc(self):
            acc = self.yacceleration
            if self.yacc_range is not None:
                acc += random.uniform(-self.yacc_range, self.yacc_range)
            return acc

        def _get_acceleration(self):
            return [self._get_xacc(), self._get_yacc()]

        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties

            particle_data = particles_props.setdefault(particle, {})

            if self._RENP_VEL not in particle_data:
                particle_data[self._RENP_VEL] = self._get_velocity()
            if self._RENP_ACCL not in particle_data:
                particle_data[self._RENP_ACCL] = self._get_acceleration()

            velocity = particles_props[particle][self._RENP_VEL]
            acceleration = particles_props[particle][self._RENP_ACCL]

            particle.x += velocity[0] * delta
            particle.y += velocity[1] * delta

            velocity[0] += acceleration[0] * delta
            velocity[1] += acceleration[1] * delta

            return UpdateState.Pass
