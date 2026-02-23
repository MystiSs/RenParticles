init -1115 python in renparticles:
    class LifetimeDeltaDecreaser(_UpdateBehavior):
        def __call__(self, context):
            particle = context.particle

            particle.lifetime -= context.delta
            if particle.lifetime < 0.0:
                particle.destroy()

            return UpdateState.Pass

    class AutoExpirePreset(_RFBehaviorPreset):
        behaviors = {
            "on_update": [LifetimeDeltaDecreaser],
            "on_event": None,
            "on_particle_dead": None
        }

        def distribute_properties(self):
            super(AutoExpirePreset, self).distribute_properties()
            self.behaviors["on_update"][0].inject_properties(oneshot=self.m_oneshot)