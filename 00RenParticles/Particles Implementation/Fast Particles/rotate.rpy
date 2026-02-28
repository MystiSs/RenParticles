# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import random


    class RotateBehavior(_Behavior):     
        speed = 360.0
        speed_range = 0.0
        phase = 0.0
        phase_range = 0.0
        
        _RENP_ROTATE = "_renp_rotate"
        _RENP_ROTATE_COUNTER = 0
        
        def __init__(self):
            self._RENP_ROTATE = "{}_{}".format(self._RENP_ROTATE, self._RENP_ROTATE_COUNTER)
            self._RENP_ROTATE_COUNTER += 1
        
        def _get_initial_data(self, particle):
            actual_speed = self.speed
            if self.speed_range > 0:
                actual_speed += random.uniform(-self.speed_range, self.speed_range)
            
            actual_phase = self.phase
            if self.phase_range > 0:
                actual_phase += random.uniform(-self.phase_range, self.phase_range)
            
            return {
                "speed": actual_speed,
                "phase": actual_phase,
                "total_rotation": actual_phase
            }
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties
            
            particle_data = particles_props.setdefault(particle, {})
            
            rotate_data = particle_data.get(self._RENP_ROTATE)
            if rotate_data is None:
                particle_data[self._RENP_ROTATE] = self._get_initial_data(particle)
                rotate_data = particle_data[self._RENP_ROTATE]
            
            delta_rotation = rotate_data["speed"] * delta
            rotate_data["total_rotation"] += delta_rotation
            
            particle.queue_transform(rotate=rotate_data["total_rotation"])
            
            return UpdateState.Pass