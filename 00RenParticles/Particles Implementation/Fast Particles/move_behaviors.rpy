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

    class OscillateMove(_Behavior):
        amplitudes = _RequiredField()  # [x_amplitude, y_amplitude]
        frequencies = [1.0, 1.0]       # [x_freq, y_freq]
        phases = [0.0, 0.0]            # [x_phase, y_phase]
        
        amplitudes_range = [None, None]
        frequencies_range = [None, None]
        phases_range = [None, None]
        
        _RENP_OSC_DATA = "_renp_osc_data"
        _RENP_ACC_OSC = 0
        
        def __init__(self):
            super(OscillateMove, self).__init__()
            
            self.frequencies = OscillateMove.frequencies[:]
            self.phases = OscillateMove.phases[:]
            
            self.amplitudes_range = OscillateMove.amplitudes_range[:]
            self.frequencies_range = OscillateMove.frequencies_range[:]
            self.phases_range = OscillateMove.phases_range[:]
            
            self._RENP_OSC_DATA = "{}_{}".format(self._RENP_OSC_DATA, self._RENP_ACC_OSC)
            self._RENP_ACC_OSC += 1
        
        @property
        def xamplitude(self):
            if isinstance(self.amplitudes, _RequiredField):
                return None
            return self.amplitudes[0]
        
        @property
        def yamplitude(self):
            if isinstance(self.amplitudes, _RequiredField):
                return None
            return self.amplitudes[1]
        
        @xamplitude.setter
        def xamplitude(self, value):
            if isinstance(self.amplitudes, _RequiredField):
                self.amplitudes = [0.0, 0.0]
            self.amplitudes[0] = value
        
        @yamplitude.setter
        def yamplitude(self, value):
            if isinstance(self.amplitudes, _RequiredField):
                self.amplitudes = [0.0, 0.0]
            self.amplitudes[1] = value
        
        @property
        def xamp_range(self):
            return self.amplitudes_range[0]
        
        @property
        def yamp_range(self):
            return self.amplitudes_range[1]
        
        @xamp_range.setter
        def xamp_range(self, value):
            self.amplitudes_range[0] = value
        
        @yamp_range.setter
        def yamp_range(self, value):
            self.amplitudes_range[1] = value
        
        @property
        def xfrequency(self):
            return self.frequencies[0]
        
        @property
        def yfrequency(self):
            return self.frequencies[1]
        
        @xfrequency.setter
        def xfrequency(self, value):
            self.frequencies[0] = value
        
        @yfrequency.setter
        def yfrequency(self, value):
            self.frequencies[1] = value
        
        @property
        def xfreq_range(self):
            return self.frequencies_range[0]
        
        @property
        def yfreq_range(self):
            return self.frequencies_range[1]
        
        @xfreq_range.setter
        def xfreq_range(self, value):
            self.frequencies_range[0] = value
        
        @yfreq_range.setter
        def yfreq_range(self, value):
            self.frequencies_range[1] = value
        
        @property
        def xphase(self):
            return self.phases[0]
        
        @property
        def yphase(self):
            return self.phases[1]
        
        @xphase.setter
        def xphase(self, value):
            self.phases[0] = value
        
        @yphase.setter
        def yphase(self, value):
            self.phases[1] = value
        
        @property
        def xphase_range(self):
            return self.phases_range[0]
        
        @property
        def yphase_range(self):
            return self.phases_range[1]
        
        @xphase_range.setter
        def xphase_range(self, value):
            self.phases_range[0] = value
        
        @yphase_range.setter
        def yphase_range(self, value):
            self.phases_range[1] = value
        
        def _get_xamplitude(self):
            amp = self.xamplitude
            if self.xamp_range is not None:
                amp += random.uniform(-self.xamp_range, self.xamp_range)
            return amp
        
        def _get_yamplitude(self):
            amp = self.yamplitude
            if self.yamp_range is not None:
                amp += random.uniform(-self.yamp_range, self.yamp_range)
            return amp
        
        def _get_xfrequency(self):
            freq = self.xfrequency
            if self.xfreq_range is not None:
                freq += random.uniform(-self.xfreq_range, self.xfreq_range)
            return freq
        
        def _get_yfrequency(self):
            freq = self.yfrequency
            if self.yfreq_range is not None:
                freq += random.uniform(-self.yfreq_range, self.yfreq_range)
            return freq
        
        def _get_xphase(self):
            phase = self.xphase
            if self.xphase_range is not None:
                phase += random.uniform(-self.xphase_range, self.xphase_range)
            return phase
        
        def _get_yphase(self):
            phase = self.yphase
            if self.yphase_range is not None:
                phase += random.uniform(-self.yphase_range, self.yphase_range)
            return phase
        
        def _get_osc_data(self):
            return {
                "amp": [self._get_xamplitude(), self._get_yamplitude()],
                "freq": [self._get_xfrequency(), self._get_yfrequency()],
                "phase": [self._get_xphase(), self._get_yphase()],
                "time": 0.0
            }
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties
            
            particle_data = particles_props.setdefault(particle, {})
            
            if self._RENP_OSC_DATA not in particle_data:
                particle_data[self._RENP_OSC_DATA] = self._get_osc_data()
            
            osc = particle_data[self._RENP_OSC_DATA]
            osc["time"] += delta
            
            dx = osc["amp"][0] * math.sin(2 * math.pi * osc["freq"][0] * osc["time"] + osc["phase"][0])
            dy = osc["amp"][1] * math.sin(2 * math.pi * osc["freq"][1] * osc["time"] + osc["phase"][1])
            
            particle.x += dx * delta
            particle.y += dy * delta
            
            return UpdateState.Pass
