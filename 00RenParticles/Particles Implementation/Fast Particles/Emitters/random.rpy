init -1115 python in renparticles:
    import random
    from renpy.store import config

    class EmitterRandom(Emitter):
        amount = _RequiredField()
        area = (0, 0, config.screen_width, config.screen_height)
        
        def __call__(self, context):
            system = context.system
            images = system.particles_data.images

            try:
                for i in range(self.amount):
                    sprite = system.create(random.choice(images))
                    sprite.x = random.randint(self.area[0], self.area[2])
                    sprite.y = random.randint(self.area[1], self.area[3])
            except Exception as e:
                renpy.error("VALUE: {}\nEXC: {}".format(self.amount, e))
            
            return UpdateState.Pass

    class SprayPreset(_RFBehaviorPreset):
        behaviors = {
            "on_update": [EmitterRandom],
            "on_event": None,
            "on_particle_dead": None
        }

        m_oneshot = True

        amount = _RequiredField()
        area = (0, 0, config.screen_width, config.screen_height)

        def distribute_properties(self):
            super(SprayPreset, self).distribute_properties()

            emitter = self.behaviors["on_update"][0]
            emitter.inject_properties(amount=self.amount, area=self.area, oneshot=self.m_oneshot)
