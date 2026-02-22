init -1337 python in renparticles:
    class LifetimeDeltaDecreaser(_UpdateBehavior):
        def __call__(self, context):
            particle = context.particle

            particle.lifetime -= context.delta
            if particle.lifetime < 0.0:
                particle.destroy()

            return UpdateState.Pass