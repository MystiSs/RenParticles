# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.


# From Ren'Py documentation: https://www.renpy.org/doc/html/sprites.html#sprite-examples
init -1115 python in renparticles:
    import math

    class RepulsorUpdate(_Behavior):
        repulsor_pos = None
        strength = 3.0
        radius = 150.0
        clamp_margin = 2.0

        def __call__(self, context):
            system = context.system
            particles_data = system.particles_data

            pos = particles_data.get("repulsor_pos")
            if pos is None:
                if self.repulsor_pos is not None:
                    pos = self.repulsor_pos
                    particles_data.repulsor_pos = pos
                else:
                    return UpdateState.Pass

            px, py = pos
            p = context.particle

            vx = p.x - px
            vy = p.y - py

            dist = math.hypot(vx, vy)
            if dist == 0:
                return UpdateState.Pass

            if dist >= self.radius:
                return UpdateState.Pass

            falloff = (self.radius - dist) / self.radius

            force = self.strength * falloff

            nx = vx / dist
            ny = vy / dist

            p.x += force * nx
            p.y += force * ny

            m = self.clamp_margin

            if p.x < m:
                p.x = m
            elif p.x > system.width - m:
                p.x = system.width - m

            if p.y < m:
                p.y = m
            elif p.y > system.height - m:
                p.y = system.height - m

            return UpdateState.Pass
        
    class RepulsorEvent(_EventBehavior):
        def __call__(self, context):
            if not isinstance(context, EventContext):
                renpy.error(
                    "Invalid context type for RepulsorEvent: {}\n"
                    "Expected: EventContext\n"
                    "This usually happens when the event handler is attached to the wrong callback type.".format(
                        type(context).__name__
                    )
                )
            context.system.particles_data.repulsor_pos = (context.x, context.y)

    class RepulsorPreset(_RFBehaviorPreset):
        behaviors = {
            "on_update": [RepulsorUpdate],
            "on_event": [RepulsorEvent],
            "on_particle_dead": None
        }

        repulsor_pos = None

        strength = 3.0
        radius = 150.0
        clamp_margin = 2.0

        def distribute_properties(self):
            super(RepulsorPreset, self).distribute_properties()

            self.behaviors["on_update"][0].inject_properties(repulsor_pos=self.repulsor_pos, strength=self.strength, radius=self.radius, clamp_margin=self.clamp_margin)