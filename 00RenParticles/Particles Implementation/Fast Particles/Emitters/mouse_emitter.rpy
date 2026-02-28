# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    class MouseIntervalSpawner(Emitter):     
        amount = "infinite"
        interval = 0.1
        per_amount = 1
        offset = (0, 0)
        kill_on_finish = False
        
        def __init__(self):
            self._last_spawn = 0
            self._spawned = 0
            self._finished = False
        
        def __call__(self, context):
            if self._finished:
                return UpdateState.Kill
            
            system = context.system
            delta = context.delta
            
            self._last_spawn += delta
            
            if self._last_spawn < self.interval:
                return UpdateState.Pass
            
            x, y = renpy.get_mouse_pos()
            
            x += self.offset[0]
            y += self.offset[1]
            
            for i in range(self.per_amount):
                if self.amount != "infinite" and self._spawned >= self.amount:
                    if self.kill_on_finish:
                        self._finished = True
                    return UpdateState.Pass if not self._finished else UpdateState.Kill
                
                if system.particles_data.images:
                    sprite = system.create(random.choice(system.particles_data.images))
                    sprite.x = x
                    sprite.y = y
                    self._spawned += 1
            
            self._last_spawn = 0
            
            return UpdateState.Pass