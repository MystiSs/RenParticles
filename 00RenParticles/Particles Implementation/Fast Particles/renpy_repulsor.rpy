# From Renpy documentation: https://www.renpy.org/doc/html/sprites.html#sprite-examples

init -1115 python in renparticles:
    import math

    class RepulsorUpdate(_Behavior):
        repulsor_pos = None

        def __call__(self, context):
            system = context.system
            particles_data = system.particles_data

            if particles_data.repulsor_pos is None:
                if self.repulsor_pos is not None:
                    particles_data.repulsor_pos = self.repulsor_pos
                else:
                    return UpdateState.Pass

            px, py = particles_data.repulsor_pos
            i = context.particle
            
            vx = i.x - px
            vy = i.y - py
            vl = math.hypot(vx, vy)
            if vl >= 150:
                return UpdateState.Pass

            distance = 3.0 * (150 - vl) / 150
            i.x += distance * vx / vl
            i.y += distance * vy / vl

            if i.x < 2:
                i.x = 2

            if i.x > system.width - 2:
                i.x = system.width - 2

            if i.y < 2:
                i.y = 2

            if i.y > system.height - 2:
                i.y = system.height - 2

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

        def distribute_properties(self):
            super(RepulsorPreset, self).distribute_properties()

            if self.repulsor_pos is not None:
                self.behaviors["on_update"][0].inject_properties(self.repulsor_pos)