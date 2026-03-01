# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    class EmitterRemoteSpawn(Emitter):
            amount = _RequiredField()

            def __call__(self, context):
                target_system = context.system
                
                if self.target_system is not None:
                    target_system = context.systems.get(self.target_system, target_system)

                spawn_x = context.particle.x if context.particle else 0
                spawn_y = context.particle.y if context.particle else 0

                images = target_system.particles_data.images

                for i in range(self.amount):
                    sprite = target_system.create(random.choice(images))
                    sprite.x = spawn_x
                    sprite.y = spawn_y
                    
                return UpdateState.Pass

    #<Этот эмиттер считается чистым обработчиком, чтобы его можно было интегрировать в блок поведения и чтобы он не был отделён от него>#
    #<В специальный блок эмиттеров, которые не получают текущую частицу в параметре context>#
    class EmitterIntervalRemoteSpawn(_Behavior):
            per_amount = 1
            interval = 0.0
            fallback_position = (0, 0)

            _RENP_INT_REM_EM = "_renp_int_rem_em"        
            _RENP_INT_REM_EM_COUNTER = 0

            def __init__(self):
                self.current_time = 0.0
                self._has_particle = None

                self._RENP_INT_REM_EM = "{}_{}".format(self._RENP_INT_REM_EM, self._RENP_INT_REM_EM_COUNTER)
                self._RENP_INT_REM_EM_COUNTER += 1

            def __call__(self, context):
                particle = context.particle
                delta = context.delta
                
                if self._has_particle is None:
                    self._has_particle = particle is not None

                can_spawn = False

                if self._has_particle:
                    particles_props = context.system.particles_data.particles_properties
                    particle_data = particles_props.setdefault(particle, {})
                    
                    emitter_data = particle_data.get(self._RENP_INT_REM_EM)
                    if emitter_data is None:
                        emitter_data = {"current_time": 0.0}
                        particle_data[self._RENP_INT_REM_EM] = emitter_data
                    
                    emitter_data["current_time"] += delta
                    
                    if emitter_data["current_time"] >= self.interval:
                        emitter_data["current_time"] = 0.0
                        can_spawn = True
                else:
                    self.current_time += delta
                    if self.current_time >= self.interval:
                        self.current_time = 0.0
                        can_spawn = True

                if not can_spawn:
                    return UpdateState.Pass

                target_system = self.get_system(context, self.renp_target_system)

                spawn_x = particle.x if particle else self.fallback_position[0]
                spawn_y = particle.y if particle else self.fallback_position[1]
                images = target_system.particles_data.images

                for i in range(self.per_amount):
                    sprite = target_system.create(random.choice(images))
                    sprite.x = spawn_x
                    sprite.y = spawn_y
                    
                return UpdateState.Pass