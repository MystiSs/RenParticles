# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import random
    from builtins import min


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
    
    class FaceVelocity(_UpdateBehavior):
        target_behavior_id = _RequiredField()
        base_angle = 0.0
        mode = "absolute" # "absolute" | "additive"
        invert = False

        def __init__(self):
            self._target_behavior = None
            self._key_cached = None

        def __call__(self, context):
            particle = context.particle
            system = context.system
            props = system.particles_data.particles_properties

            if self._target_behavior is None:
                self._target_behavior = system.get_behavior_by_id(self.target_behavior_id)
            
            target = self._target_behavior
            if not target or particle not in props:
                return UpdateState.Pass

            if self._key_cached is None and hasattr(target, "get_key"):
                self._key_cached = target.get_key()

            particle_data = props[particle]
            vel_key = self._key_cached

            if not vel_key or vel_key not in particle_data:
                return UpdateState.Pass

            vx, vy = particle_data[vel_key]

            if abs(vx) < 0.1 and abs(vy) < 0.1:
                return UpdateState.Pass

            angle = math.degrees(math.atan2(vy, vx))

            if self.invert:
                angle += 180

            final_angle = angle + self.base_angle

            if self.mode == "absolute":
                particle.queue_transform(rotate=final_angle)
            else:
                particle.queue_transform_additive(rotate=final_angle)

            return UpdateState.Pass