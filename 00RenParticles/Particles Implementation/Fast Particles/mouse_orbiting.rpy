# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import math
    import random


    class OrbitCursorUpdate(_Behavior):    
        radius = 100.0
        speed = 10.0
        speed_variance = 0.5
        pull_strength = 0.5
        clockwise = True
        screen_bounds = True
        
        _RENP_MORBIT = "_orbit_speed"
        _RENP_ACC = 0

        def __init__(self):
            self.cursor_pos = None
            self.last_mouse_pos = None

            self._RENP_MORBIT = "{}_{}".format(self._RENP_MORBIT, self._RENP_ACC)
            self._RENP_ACC += 1

        def __call__(self, context):
            mouse_x, mouse_y = renpy.get_mouse_pos()
            
            if mouse_x < 0 or mouse_y < 0:
                return UpdateState.Pass
                
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties
            
            particle_data = particles_props.setdefault(particle, {})
            
            if self._RENP_MORBIT not in particle_data:
                variance_factor = random.uniform(1.0 - self.speed_variance, 1.0 + self.speed_variance)
                particle_data[self._RENP_MORBIT] = self.speed * variance_factor
            
            particle_speed = particle_data[self._RENP_MORBIT]
            
            dx = particle.x - mouse_x
            dy = particle.y - mouse_y
            distance = math.hypot(dx, dy)
            
            if distance < 1:
                angle = random.uniform(0, 2 * math.pi)
                particle.x = mouse_x + math.cos(angle) * self.radius
                particle.y = mouse_y + math.sin(angle) * self.radius
                return UpdateState.Pass
            
            nx = dx / distance
            ny = dy / distance
            
            dir_sign = 1 if self.clockwise else -1
            
            perp_x = -ny * dir_sign
            perp_y = nx * dir_sign
            
            target_x = mouse_x + nx * self.radius
            target_y = mouse_y + ny * self.radius
            
            rotation_offset = particle_speed * delta * self.radius
            target_x += perp_x * rotation_offset
            target_y += perp_y * rotation_offset
            
            particle.x += (target_x - particle.x) * self.pull_strength
            particle.y += (target_y - particle.y) * self.pull_strength
            
            if self.screen_bounds:
                system = context.system
                if particle.x < 2:
                    particle.x = 2
                elif particle.x > system.width - 2:
                    particle.x = system.width - 2
                    
                if particle.y < 2:
                    particle.y = 2
                elif particle.y > system.height - 2:
                    particle.y = system.height - 2
            
            return UpdateState.Pass
    
    class OrbitPoint(_UpdateBehavior):        
        center = _RequiredField()
        radius = 100.0
        speed = 10.0
        speed_variance = 0.5
        pull_strength = 0.5
        clockwise = True
        screen_bounds = True
        
        _RENP_ORBIT = "_orbit_speed"
        _COUNTER = 0
        
        def __init__(self):
            self._RENP_ORBIT = "{}_{}".format(self._RENP_ORBIT, self._COUNTER)
            self._COUNTER += 1
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties
            
            center_x, center_y = self.center
            
            particle_data = particles_props[particle]
            
            if self._RENP_ORBIT not in particle_data:
                variance_factor = random.uniform(1.0 - self.speed_variance, 1.0 + self.speed_variance)
                particle_data[self._RENP_ORBIT] = self.speed * variance_factor
            
            particle_speed = particle_data[self._RENP_ORBIT]
            
            dx = particle.x - center_x
            dy = particle.y - center_y
            distance = math.hypot(dx, dy)
            
            if distance < 1:
                angle = random.uniform(0, 2 * math.pi)
                particle.x = center_x + math.cos(angle) * self.radius
                particle.y = center_y + math.sin(angle) * self.radius
                return UpdateState.Pass
            
            nx = dx / distance
            ny = dy / distance
            
            dir_sign = 1 if self.clockwise else -1
            
            perp_x = -ny * dir_sign
            perp_y = nx * dir_sign
            
            target_x = center_x + nx * self.radius
            target_y = center_y + ny * self.radius
            
            rotation_offset = particle_speed * delta * self.radius
            target_x += perp_x * rotation_offset
            target_y += perp_y * rotation_offset
            
            particle.x += (target_x - particle.x) * self.pull_strength
            particle.y += (target_y - particle.y) * self.pull_strength
            
            if self.screen_bounds:
                system = context.system
                particle.x = max(2, min(system.width - 2, particle.x))
                particle.y = max(2, min(system.height - 2, particle.y))
            
            return UpdateState.Pass
    
    class OrbitMousePreset(_RFBehaviorPreset):
        behaviors = {
            "on_update": [OrbitCursorUpdate],
            "on_event": None,
            "on_particle_dead": None
        }

        radius = 100.0
        speed = 10.0
        speed_variance = 0.5
        pull_strength = 0.5
        clockwise = True
        screen_bounds = True

        def distribute_properties(self):
            super(OrbitMousePreset, self).distribute_properties()
            self.behaviors["on_update"][0].inject_properties(radius=self.radius,
                                            speed=self.speed,
                                            speed_variance=self.speed_variance,
                                            pull_strength=self.pull_strength,
                                            clockwise=self.clockwise,
                                            screen_bounds=self.screen_bounds,
                                            oneshot=self.m_oneshot)
