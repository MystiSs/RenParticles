init -1337 python in renparticles:
    import random
    from renpy.store import config

    class EmitterRandom(Emitter):
        amount = _RequiredField()
        area = _RequiredField()
        
        def __call__(self, context):
            system = context.system
            images = system.particles_data.images

            for i in range(self.amount):
                sprite = system.create(random.choice(images))
                sprite.x = random.randint(self.area[0], self.area[2])
                sprite.y = random.randint(self.area[1], self.area[3])
            
            return UpdateState.Pass
