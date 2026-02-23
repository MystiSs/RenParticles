init -1115 python in renparticles:
    import random
    from builtins import min
    from renpy.store import config

    class EmitterRandom(Emitter):
        amount = _RequiredField()
        area = (0, 0, config.screen_width, config.screen_height)
        
        def __call__(self, context):
            system = context.system
            images = system.particles_data.images

            for i in range(self.amount):
                sprite = system.create(random.choice(images))
                sprite.x = random.randint(self.area[0], self.area[2])
                sprite.y = random.randint(self.area[1], self.area[3])
            
            return UpdateState.Pass

    class IntervalSprayEmitter(Emitter):
        amount = _RequiredField()
        interval = 0.0
        per_amount = 1
        kill_on_finish = True

        area = (0, 0, config.screen_width, config.screen_height)

        def __init__(self):
            self.remaining = None
            self.current_time = 0.0

        def __call__(self, context):
            if self.remaining is None:
                self.remaining = self.amount

            if self.remaining <= 0:
                return UpdateState.Kill if self.kill_on_finish else UpdateState.Pass

            self.current_time += context.delta
            if self.current_time >= self.interval:
                system = context.system
                images = system.particles_data.images

                self.current_time = 0.0
                amount_to_create = min(self.remaining, self.per_amount)

                for i in range(amount_to_create):
                    sprite = system.create(random.choice(images))
                    sprite.x = random.randint(self.area[0], self.area[2])
                    sprite.y = random.randint(self.area[1], self.area[3])
                
                self.remaining -= amount_to_create
            
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

    class IntervalSprayPreset(_RFBehaviorPreset):
        behaviors = {
            "on_update": [IntervalSprayEmitter],
            "on_event": None,
            "on_particle_dead": None
        }

        m_oneshot = False

        amount = _RequiredField()
        interval = 0.0
        per_amount = 1
        kill_on_finish = True

        area = (0, 0, config.screen_width, config.screen_height)

        def distribute_properties(self):
            super(IntervalSprayPreset, self).distribute_properties()

            emitter = self.behaviors["on_update"][0]
            emitter.inject_properties(amount=self.amount, interval=self.interval, per_amount=self.per_amount, kill_on_finish=self.kill_on_finish, area=self.area, oneshot=self.m_oneshot)
