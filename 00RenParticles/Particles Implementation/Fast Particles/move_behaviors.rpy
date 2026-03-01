# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import random
    import math
    from builtins import min, max


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

        def get_key(self):
            return self._RENP_VEL

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

            particle_data = context.system.particles_data.particles_properties.get(particle, None)
            if particle_data is None:
                return UpdateState.Pass

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

            particle_data = particles_props.get(particle, None)
            if particle_data is None:
                return UpdateState.Pass

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
            
            particle_data = system.particles_data.particles_properties.get(particle, None)
            if particle_data is None:
                return UpdateState.Pass
                        
            if self._RENP_OSC_DATA not in particle_data:
                particle_data[self._RENP_OSC_DATA] = self._get_osc_data()
            
            osc = particle_data[self._RENP_OSC_DATA]
            osc["time"] += delta
            
            dx = osc["amp"][0] * math.sin(2 * math.pi * osc["freq"][0] * osc["time"] + osc["phase"][0])
            dy = osc["amp"][1] * math.sin(2 * math.pi * osc["freq"][1] * osc["time"] + osc["phase"][1])
            
            particle.x += dx * delta
            particle.y += dy * delta
            
            return UpdateState.Pass

    class Friction(_UpdateBehavior):     
        target_behavior_id = _RequiredField()
        friction = 0.1
        per_axis = True
        min_speed = 0.01

        _key_cached = None
        
        _RENP_FRICTION = "_renp_friction"
        _COUNTER = 0
        
        def __init__(self):
            self._RENP_FRICTION = "{}_{}".format(self._RENP_FRICTION, self._COUNTER)
            self._COUNTER += 1
            self._target_behavior = None
        
        def _get_target_behavior(self, system):
            if self._target_behavior is None and self.target_behavior_id:
                self._target_behavior = system.get_behavior_by_id(self.target_behavior_id)
            return self._target_behavior
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            system = context.system

            particle_data = system.particles_data.particles_properties.get(particle, None)
            if particle_data is None:
                return UpdateState.Pass
            
            if self._target_behavior is None and self.target_behavior_id:
                self._target_behavior = system.get_behavior_by_id(self.target_behavior_id)
            
            target = self._target_behavior
            if target is None:
                return UpdateState.Pass
                        
            if self._key_cached is None:
                if hasattr(target, "get_key"):
                    self._key_cached = target.get_key()
            
            vel_key = self._key_cached
            if not vel_key or vel_key not in particle_data:
                return UpdateState.Pass
            
            vel = particle_data[vel_key]
            factor = 1.0 - self.friction * delta
            
            if self.per_axis:
                x, y = vel
                new_vel = [x * factor, y * factor]
            else:
                speed = math.hypot(vel[0], vel[1])
                if speed > self.min_speed:
                    new_speed = max(0, speed - self.friction * speed * delta)
                    if new_speed > 0:
                        ratio = new_speed / speed
                        x, y = vel
                        new_vel = [x * ratio, y * ratio]
                    else:
                        new_vel = [0.0, 0.0]
                else:
                    new_vel = [0.0, 0.0]
            
            particle_data[vel_key] = new_vel
            
            return UpdateState.Pass

    class Bounce(_UpdateBehavior):        
        target_behavior_id = _RequiredField()
        restitution = 0.8
        margin = 0
        bounce_axes = "both"
        
        _RENP_BOUNCE = "_renp_bounce"
        _COUNTER = 0
        
        def __init__(self):
            self._RENP_BOUNCE = "{}_{}".format(self._RENP_BOUNCE, self._COUNTER)
            self._COUNTER += 1
            self._target_behavior = None
            self._key_cached = None
            self._sprite_size = None
        
        def _get_margins(self, system):
            if isinstance(self.margin, (int, float)):
                return (self.margin, self.margin, self.margin, self.margin)
            elif isinstance(self.margin, (list, tuple)):
                if len(self.margin) == 2:
                    h, v = self.margin
                    return (h, v, h, v)
                elif len(self.margin) == 4:
                    return tuple(self.margin)
            return (0, 0, 0, 0)
        
        def _get_sprite_size(self, particle):
            if self._sprite_size is None and particle.cache and particle.cache.render:
                w, h = particle.cache.render.get_size()
                self._sprite_size = (w, h)
            return self._sprite_size or (0, 0)
        
        def _check_bounds(self, x, y, w, h, system, margins):
            left = margins[0]
            top = margins[1]
            right = system.width - margins[2]
            bottom = system.height - margins[3]
            
            hit_x = False
            hit_y = False
            
            if self.bounce_axes in ("both", "x"):
                if x - w/2 < left:
                    x = left + w/2
                    hit_x = True
                elif x + w/2 > right:
                    x = right - w/2
                    hit_x = True
            
            if self.bounce_axes in ("both", "y"):
                if y - h/2 < top:
                    y = top + h/2
                    hit_y = True
                elif y + h/2 > bottom:
                    y = bottom - h/2
                    hit_y = True
            
            return x, y, hit_x, hit_y
        
        def _apply_bounce_to_velocity(self, vel, hit_x, hit_y):
            new_vel = list(vel)
            if hit_x:
                new_vel[0] = -new_vel[0] * self.restitution
            if hit_y:
                new_vel[1] = -new_vel[1] * self.restitution
            
            return new_vel
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            system = context.system
            props = system.particles_data.particles_properties
            
            if self._target_behavior is None and self.target_behavior_id:
                self._target_behavior = system.get_behavior_by_id(self.target_behavior_id)
            
            target = self._target_behavior
            if target is None:
                return UpdateState.Pass
            
            particle_data = props.get(particle, None)
            if particle_data is None:
                return UpdateState.Pass
            
            if self._key_cached is None:
                if hasattr(target, "get_key"):
                    self._key_cached = target.get_key()
            
            vel_key = self._key_cached
            if not vel_key or vel_key not in particle_data:
                return UpdateState.Pass
            
            vel = particle_data[vel_key]
            
            w, h = self._get_sprite_size(particle)
            margins = self._get_margins(system)
            
            new_x, new_y, hit_x, hit_y = self._check_bounds(
                particle.x, particle.y, w, h, system, margins
            )
            
            if hit_x or hit_y:
                particle.x = new_x
                particle.y = new_y
                
                new_vel = self._apply_bounce_to_velocity(vel, hit_x, hit_y)
                particle_data[vel_key] = new_vel
            
            return UpdateState.Pass

    class Attractor(_UpdateBehavior):      
        target = _RequiredField()
        strength = 500.0
        radius = 0.0
        falloff = 1.0
        min_distance = 5.0
        max_speed = 1000.0
        screen_bounds = True
        
        _RENP_ATTRACTOR = "_attractor_vel"
        _COUNTER = 0
        
        def __init__(self):
            self._RENP_ATTRACTOR = "{}_{}".format(self._RENP_ATTRACTOR, self._COUNTER)
            self._COUNTER += 1
        
        def _get_target_position(self):
            if self.target == "mouse":
                return renpy.get_mouse_pos()
            else:
                return self.target
        
        def _calculate_force(self, dx, dy, distance):
            if distance < self.min_distance:
                return (0, 0)
            
            nx = dx / distance
            ny = dy / distance
            
            if self.radius > 0 and distance > self.radius:
                return (0, 0)
            
            if self.falloff == 0:
                force = self.strength
            elif self.falloff == 1:
                if self.radius > 0:
                    t = 1.0 - (distance / self.radius)
                    force = self.strength * t
                else:
                    force = self.strength / max(distance, self.min_distance)
            else:
                force = self.strength / (distance ** self.falloff)
            
            return nx * force, ny * force
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            system = context.system
            props = system.particles_data.particles_properties

            if particle not in props:
                return UpdateState.Pass
            
            target_pos = self._get_target_position()
            if target_pos is None:
                return UpdateState.Pass
            
            tx, ty = target_pos
            
            if tx < 0 or ty < 0:
                return UpdateState.Pass
            
            particle_data = props[particle]
            
            if self._RENP_ATTRACTOR not in particle_data:
                particle_data[self._RENP_ATTRACTOR] = [0.0, 0.0]
            
            vel = particle_data[self._RENP_ATTRACTOR]
            
            dx = tx - particle.x
            dy = ty - particle.y
            distance = math.hypot(dx, dy)
            
            fx, fy = self._calculate_force(dx, dy, distance)
            
            vel[0] += fx * delta
            vel[1] += fy * delta
            
            speed = math.hypot(vel[0], vel[1])
            if speed > self.max_speed:
                ratio = self.max_speed / speed
                vel[0] *= ratio
                vel[1] *= ratio
            
            particle.x += vel[0] * delta
            particle.y += vel[1] * delta
            
            if self.screen_bounds:
                particle.x = max(2, min(system.width - 2, particle.x))
                particle.y = max(2, min(system.height - 2, particle.y))
            
            return UpdateState.Pass
