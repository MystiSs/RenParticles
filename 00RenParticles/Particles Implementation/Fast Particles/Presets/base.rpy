init -1226 python in renparticles:
    class _RFBehaviorPreset(_InjectPropertiesMixin, _CheckInitialisedMixin):
        behaviors = {
            "on_update": None,
            "on_event": None,
            "on_particle_dead": None
        }

        def __init__(self):
            self.behaviors = self.behaviors.copy()

        m_oneshot = False

        def instanciate_behaviors(self):
            for key, behaviors in self.behaviors.items():
                if behaviors is not None:
                    loaded = [behavior() for behavior in behaviors]
                    self.behaviors[key] = loaded
                else:
                    self.behaviors[key] = [ ]

        def distribute_properties(self):
            self.check_initialised()

        def build(self):
            self.instanciate_behaviors()
            self.distribute_properties()
            return self.behaviors.copy()
