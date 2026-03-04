# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import random
    import math
    from builtins import min
    from renpy.store import config

    class EmitterRandom(Emitter):
        amount = _RequiredField()
        area = (0, 0, config.screen_width, config.screen_height)

        _check_is_valid = True
        _valid = { "area", "amount" }

        _renp_period = 2.0 * math.pi
        
        def __call__(self, context):
            system = context.system
            images = system.particles_data.images

            for i in range(self.amount):
                sprite = system.create(random.choice(images))
                sprite.x = random.randint(0, self.area[2]) + self.area[0]
                sprite.y = random.randint(0, self.area[3]) + self.area[1]
            
            return UpdateState.Pass

    class SprayRadialEmitter(Emitter):
        amount = _RequiredField()
        radius = 100
        center = (0, 0)

        _check_is_valid = True
        _valid = { "radius", "amount", "center" }

        def __call__(self, context):
            system = context.system
            images = system.particles_data.images

            for i in range(self.amount):
                sprite = system.create(random.choice(images))

                r = self.radius * math.sqrt(random.random())
                angle = random.uniform(0.0, SprayRadialEmitter._renp_period)
                center = self.center if self.center != "mouse" else renpy.get_mouse_pos()
                sprite.x = center[0] + r * math.cos(angle)
                sprite.y = center[1] + r * math.sin(angle)

            return UpdateState.Pass

    class SprayRingEmitter(Emitter):
        amount = _RequiredField()
        radius = 100
        width = 10
        center = (0, 0)

        _check_is_valid = True
        _valid = { "radius", "amount", "center", "width" }

        _renp_period = 2.0 * math.pi

        def _get_ring_position(self):
            angle = random.uniform(0.0, SprayRingEmitter._renp_period)
            
            if self.width > 0:
                offset = random.uniform(-self.width / 2, self.width / 2)
                r = self.radius + offset
            else:
                r = self.radius
            
            center = self.center if self.center != "mouse" else renpy.get_mouse_pos()
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            
            return x, y

        def __call__(self, context):
            system = context.system
            images = system.particles_data.images

            for i in range(self.amount):
                sprite = system.create(random.choice(images))
                sprite.x, sprite.y = self._get_ring_position()

            return UpdateState.Pass

    class IntervalSprayEmitter(Emitter):
        amount = "infinite"
        interval = 0.0
        per_amount = 1
        kill_on_finish = True

        area = (0, 0, config.screen_width, config.screen_height)

        _check_is_valid = True
        _valid = { "area", "amount",  "interval", "per_amount", "kill_on_finish" }

        def __init__(self):
            self.remaining = None
            self.current_time = 0.0

        def __call__(self, context):
            if self.amount == "infinite":
                #<Questions?>#
                self.remaining = 4294967295
                self.amount = -1

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
                    sprite.x = random.randint(0, self.area[2]) + self.area[0]
                    sprite.y = random.randint(0, self.area[3]) + self.area[1]
                
                self.remaining -= amount_to_create
            
            return UpdateState.Pass

    class IntervalSprayRadialEmitter(Emitter):
        amount = "infinite"
        interval = 0.0
        per_amount = 1
        kill_on_finish = True

        radius = 100
        center = (0, 0) # or "mouse"

        _check_is_valid = True
        _valid = { "center", "radius", "amount",  "interval", "per_amount", "kill_on_finish" }

        _renp_period = 2.0 * math.pi

        def __init__(self):
            self.remaining = None
            self.current_time = 0.0

        def _get_position(self):
            angle = random.uniform(0.0, IntervalSprayRadialEmitter._renp_period)
            
            center = self.center if self.center != "mouse" else renpy.get_mouse_pos()
            x = center[0] + self.radius * math.cos(angle)
            y = center[1] + self.radius * math.sin(angle)
            
            return x, y

        def __call__(self, context):
            if self.amount == "infinite":
                #<Questions?>#
                self.remaining = 4294967295
                self.amount = -1

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
                    sprite.x, sprite.y = self._get_position()
                
                self.remaining -= amount_to_create
            
            return UpdateState.Pass

    class IntervalSprayRingEmitter(Emitter):
        amount = "infinite"
        interval = 0.0
        per_amount = 1
        kill_on_finish = True

        width = 10
        radius = 100
        center = (0, 0) # or "mouse"

        _check_is_valid = True
        _valid = { "center", "width", "radius", "amount",  "interval", "per_amount", "kill_on_finish" }

        _renp_period = 2.0 * math.pi

        def __init__(self):
            self.remaining = None
            self.current_time = 0.0

        def _get_ring_position(self):
            angle = random.uniform(0.0, IntervalSprayRingEmitter._renp_period)
            
            if self.width > 0:
                offset = random.uniform(-self.width / 2, self.width / 2)
                r = self.radius + offset
            else:
                r = self.radius
            
            center = self.center if self.center != "mouse" else renpy.get_mouse_pos()
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            
            return x, y

        def __call__(self, context):
            if self.amount == "infinite":
                #<Questions?>#
                self.remaining = 4294967295
                self.amount = -1

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
                    sprite.x, sprite.y = self._get_ring_position()
                
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

        amount = "infinite"
        interval = 0.0
        per_amount = 1
        kill_on_finish = True

        area = (0, 0, config.screen_width, config.screen_height)

        def distribute_properties(self):
            super(IntervalSprayPreset, self).distribute_properties()

            emitter = self.behaviors["on_update"][0]
            emitter.inject_properties(amount=self.amount, interval=self.interval, per_amount=self.per_amount, kill_on_finish=self.kill_on_finish, area=self.area, oneshot=self.m_oneshot)
