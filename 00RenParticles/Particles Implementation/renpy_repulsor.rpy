# From Renpy documentation: https://www.renpy.org/doc/html/sprites.html#sprite-examples

init -1337 python in renparticles:
    import math

    class RepulsorUpdate(_UpdateBehavior):
        def __call__(self, st, manager):
            if manager.particles_data.repulsor_pos is None:
                return UpdateState.Pass

            px, py = manager.particles_data.repulsor_pos

            for i in manager.children:
                vx = i.x - px
                vy = i.y - py
                vl = math.hypot(vx, vy)
                if vl >= 150:
                    continue

                distance = 3.0 * (150 - vl) / 150
                i.x += distance * vx / vl
                i.y += distance * vy / vl

                if i.x < 2:
                    i.x = 2

                if i.x > manager.width - 2:
                    i.x = manager.width - 2

                if i.y < 2:
                    i.y = 2

                if i.y > manager.height - 2:
                    i.y = manager.height - 2

            return UpdateState.Pass
        
    class RepulsorEvent(_EventBehavior):
        def __call__(self, ev, x, y, st, manager):
            manager.particles_data.repulsor_pos = (x, y)