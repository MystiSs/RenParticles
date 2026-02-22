init -1337 python in renparticles:
    class LifetimeDeltaDecreaser(_UpdateBehavior):
        def __call__(self, st, manager):
            particles = manager.children
            delta = manager.delta()

            for particle in particles:
                particle.lifetime -= delta

                if particle.lifetime < 0.0:
                    particle.destroy()

            return UpdateState.Pass