init -1337 python in renparticles:
    import random
    from renpy.store import config

    class EmitterRandomExplode(Emitter):
        def __init__(self):
            self.amount = 0
            self.area = (0, 0, config.screen_width, config.screen_height)
        
        def __call__(self, st, manager):
            images = manager.particles_data.images

            for i in range(self.amount):
                sprite = manager.create(random.choice(images))
                sprite.x = random.randint(self.area[0], self.area[2])
                sprite.y = random.randint(self.area[1], self.area[3])
            
            return UpdateState.Pass

    class EmitterOnDeadRandom(DeadEmitter):
        def __init__(self):
            self.amount = 0
            self.area = (0, 0, config.screen_width, config.screen_height)
        
        def __call__(self, particle, st, manager):
            images = manager.particles_data.images

            for i in range(self.amount):
                sprite = manager.create(random.choice(images))
                sprite.x = random.randint(self.area[0], self.area[2])
                sprite.y = random.randint(self.area[1], self.area[3])
            
            return UpdateState.Pass 
