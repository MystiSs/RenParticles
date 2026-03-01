# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import random

    class FlickerBehavior(_Behavior):
        property = "alpha"
        base_value = 0.5
        range = (0.0, 0.0)
        mode = "add"
        interval = 0.1

        _RENP_FLICKER = "_renp_flicker"
        _RENP_FLICKER_COUNTER = 0

        def __init__(self):
            self._RENP_FLICKER = "{}_{}".format(self._RENP_FLICKER, self._RENP_FLICKER_COUNTER)
            self._RENP_FLICKER_COUNTER += 1

        def __call__(self, context):
            particle = context.particle
            system = context.system
            delta = context.delta
            props = system.particles_data.particles_properties

            if particle not in props:
                return UpdateState.Pass
            
            particle_data = props[particle]
            if self._RENP_FLICKER not in particle_data:
                particle_data[self._RENP_FLICKER] = {"timer": 0.0, "last_val": 0.0}
            
            flick_data = particle_data[self._RENP_FLICKER]
            flick_data["timer"] += delta
            
            if flick_data["timer"] >= self.interval:
                flick_data["timer"] = 0.0
                
                val = random.uniform(self.range[0], self.range[1])
                if self.mode == "sub":
                    val = -abs(val)
                elif self.mode == "add":
                    val = abs(val)
                
                flick_data["last_val"] = val

            if particle.get_transform_from_queue(self.property) is None:
                particle.queue_transform(**{self.property: self.base_value})

            particle.queue_transform_additive(**{self.property: flick_data["last_val"]})
            
            return UpdateState.Pass