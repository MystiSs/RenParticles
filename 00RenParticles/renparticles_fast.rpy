# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1337 python in renparticles:
    import random
    from collections import deque
    from renpy.store import SpriteManager, Sprite
    from renpy.display.particle import SpriteCache
    from renpy.store import Transform
    from builtins import min, max, len


    _lifetime_getters = {
        "range-random": random.uniform,
        "constant": float
    }

    class ParticlesData:
        particles_properties = None

        def __init__(self, **properties):
            self.particles_properties = {}

            for key, value in properties.items():
                setattr(self, key, value)
        
        def get(self, key):
            return getattr(self, key, None)
    
    class RenpFContext:
        system = None
        st = None
        delta = None
        particle = None
        systems = None

        def __init__(self, other_ctx=None):
            if isinstance(other_ctx, RenpFContext):
                self.systems = {}
                self.depends_on(other_ctx)

        def depends_on(self, other):
            self.system = other.system
            self.st = other.st
            self.delta = other.delta
            self.particle = None
            self.systems = other.systems
            return self

    class UpdateEmitterContext(RenpFContext):
        pass

    class EventContext(RenpFContext):
        x = None
        y = None
        event = None

    class ParticleDeadContext(RenpFContext):
        pass

    class ParticleAppearContext(RenpFContext):
        pass

    class RenParticlesPool:
        _stock = None

        _BASE_AMOUNT = 2500

        def __init__(self, reserved_amount=None):
            self._stock = deque(maxlen=reserved_amount or self._BASE_AMOUNT)

            self._hits = 0
            self._misses = 0
            self._total_created = 0

        def reserve(self):
            self._stock.extend([RenParticle() for _i in range(self._stock.maxlen)])

        def get(self):
            if self._stock:
                self._hits += 1
                return self._stock.popleft()
            
            self._misses += 1
            self._total_created += 1
            return RenParticle()
        
        def put(self, particle):
            if len(self._stock) < self._stock.maxlen:
                self._stock.append(particle)
        
        def __len__(self):
            return len(self._stock)

        @property
        def stats(self):
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            
            return (
                "Particle Pool Statistics:\n"
                "  Pool ID: {}\n"
                "  Current size: {}\n"
                "  Capacity: {}\n"
                "  Hits (cache): {}\n"
                "  Misses (new): {}\n"
                "  Hit rate: {:.1f}%\n"
                "  Total created: {}"
            ).format(
                id(self),
                len(self._stock),
                self._stock.maxlen,
                self._hits,
                self._misses,
                hit_rate,
                self._total_created
            )
    
    class RenSpriteCache(SpriteCache):
        nosave = ["st", "render"]

        child = None
        child_copy = None
        st = None
        render = None
        fast = False

    class RenSprite(Sprite):
        def set_child(self, d):
            id_d = id(d)

            sc = self.manager.displayable_map.get(id_d, None)
            if sc is None:
                d = renpy.easy.displayable(d)

                sc = RenSpriteCache()
                sc.render = None
                sc.child = d
                sc.st = None

                if d._duplicatable:
                    sc.child_copy = d._duplicate(None)
                    sc.child_copy._unique()
                else:
                    sc.child_copy = d
                    self.manager.displayable_map[id_d] = sc

            self.cache = sc

    class RenParticle(RenSprite):
        nosave = ["render"]

        lifetime = 0.0
        lifetime_max = 0.0

        _base_image = None

        def __init__(self):
            self.queued_transforms = {}

        def get_transform_from_queue(self, property_key):
            return self.queued_transforms.get(property_key, None)

        def queue_transform(self, **properties):
            self.queued_transforms.update(properties)

        def queue_transform_additive(self, **properties):
            for key, value in properties.items():
                if key in self.queued_transforms:
                    existing = self.queued_transforms[key]
                    
                    if isinstance(value, (int, float)) and isinstance(existing, (int, float)):
                        self.queued_transforms[key] = existing + value
                    
                    elif isinstance(value, (list, tuple)) and isinstance(existing, (list, tuple)):
                        if len(value) == len(existing):
                            result = [a + b for a, b in zip(existing, value)]
                            self.queued_transforms[key] = type(existing)(result)
                        else:
                            self.queued_transforms[key] = value
                    
                    else:
                        self.queued_transforms[key] = value
                else:
                    self.queued_transforms[key] = value

        def apply_transforms(self):
            if not self.queued_transforms:
                return
            if self.cache is None:
                return
            if self._base_image is None:
                self._base_image = self.cache.child_copy
            
            cache = RenSpriteCache()
            transformed_image = Transform(self._base_image, **self.queued_transforms)

            cache.render = None
            cache.st = None
            cache.child = transformed_image

            if transformed_image._duplicatable:
                cache.child_copy = transformed_image._duplicate(None)
                cache.child_copy._unique()
            else:
                cache.child_copy = transformed_image

            self.cache = cache
            self.queued_transforms.clear()

        def set_child(self, d):
            super(RenParticle, self).set_child(d)
            self._base_image = None
    
    class RenParticlesFast(SpriteManager):
        _BUFFER_AMOUNT = [1, 2, 4, 6, 8, 10, 12, 14, 16]
        _BUFFER_AMOUNT_DELTAS = [0.001, 0.0015, 0.0019, 0.00225, 0.0031, 0.004, 0.006, 0.009, 0.014]

        _UPDATE_BUFFER_AMOUNT = [1, 2, 4, 6, 8, 10, 12, 14, 16]
        _UPDATE_BUFFER_AMOUNT_DELTAS = [0.00125, 0.002, 0.004, 0.006, 0.009, 0.012, 0.017, 0.024, 0.034]

        def __init__(self, on_update=None, on_event=None, on_particle_dead=None, on_particle_appear=None, particles_data=None, ignore_time=False, redraw=None, layer=None, transform_acceleration=None, particles_listening_events=None, update_fidelity=None, update_acceleration=None, acceleration_target_fps=None, **properties):
            super(RenParticlesFast, self).__init__(ignore_time=ignore_time, **properties)
            self.layer = layer

            self.particles_queue = [ ]

            self.animation = False

            self.particles_data = particles_data
            self.redraw = redraw

            self.behaviors_by_id = { }

            self.on_update = [ ]
            self.on_event = [ ]
            self.on_particle_dead = [ ]
            self.on_particle_appear = [ ]
            self.oneshotted_on_update = [ ]
            self.oneshotted_on_update_emitters = [ ]
            self.oneshotted_on_event = [ ]
            self.oneshotted_on_dead = [ ]
            self.oneshotted_on_appear = [ ]
            self._set_on_update(on_update)
            self._set_on_update_emitters_from_update_list()
            self._set_on_event(on_event)
            self._set_on_particle_dead(on_particle_dead)
            self._set_on_particle_appear(on_particle_appear)

            self.on_update_raw = on_update
            self.on_event_raw = on_event
            self.on_particle_dead_raw = on_particle_dead
            self.on_particle_appear_raw = on_particle_appear

            self._old_st = 0.0
            self._dtime = 0.0
            self._prev_dtime = 0.0

            self.system_id = None

            self._frozen = False

            self._smoothed_dtime = 0.0

            self._transform_acceleration = transform_acceleration or get_default_system_parameter("transform_acceleration")
            self._buffer_offset = 0
            self._buffer_index = 0
            self._buffer_amount = RenParticlesFast._BUFFER_AMOUNT[0]

            self._update_acceleration = update_acceleration or get_default_system_parameter("update_acceleration")
            self._update_buffer_offset = 0
            self._update_buffer_index = 0
            self._update_buffer_amount = RenParticlesFast._UPDATE_BUFFER_AMOUNT[0]

            self._update_fidelity = update_fidelity or get_default_system_parameter("update_fidelity")
            self._update_delay_counter = 0
            self._update_fidelity_delta_accumulator = 0.0
            self._update_fidelity_delta_accumulator_debug_last = 0.0

            self._particles_listening_events = particles_listening_events or get_default_system_parameter("particles_listening_events")

            if self._transform_acceleration or self._update_acceleration:
                self._acceleration_target_fps = acceleration_target_fps or get_default_system_parameter("acceleration_target_fps")
                self._acceleration_target_delta = self._get_acc_target_fps_delta()
                self._acceleration_deltas_factor = get_default_system_parameter("acceleration_root_fps") / self._acceleration_target_fps
                self._buffer_amount_deltas = [delta * self._acceleration_deltas_factor for delta in RenParticlesFast._BUFFER_AMOUNT_DELTAS]
                self._update_buffer_amount_deltas = [delta * self._acceleration_deltas_factor for delta in RenParticlesFast._UPDATE_BUFFER_AMOUNT_DELTAS]
            
            self.simulate_time = 0.0

            self._init_contexts()

            self.dead_child = False

            #self.cycle = 0

        def get_behavior_by_id(self, behavior_id):
            return self.behaviors_by_id.get(behavior_id, None)

        def get_info(self):
            lines = ['\n']
            lines.append("=" * 40)
            lines.append("PARTICLES DATA:")
            lines.append("-" * 40)
            lines.append("redraw: {}".format(self.redraw))
            
            for key, prop in self.particles_data.__dict__.items():
                lines.append("{}: {}".format(key, prop))
            
            lines.append("-" * 40)
            lines.append("ON UPDATE:")
            for func, props in self.on_update:
                lines.append("  • {}".format(func))
                if props:
                    for k, v in props.items():
                        lines.append("    {} = {}".format(k, v))

            lines.append("-" * 40)
            lines.append("ON PARTICLE DEAD:")
            for func, props in self.on_particle_dead:
                lines.append("  • {}".format(func))
                if props:
                    for k, v in props.items():
                        lines.append("    {} = {}".format(k, v))
            
            lines.append("-" * 40)
            lines.append("ON EVENT:")
            for func, props in self.on_event:
                lines.append("  • {}".format(func))
                if props:
                    for k, v in props.items():
                        lines.append("    {} = {}".format(k, v))
            
            lines.append("=" * 40)
            return "\n".join(lines)
        
        def set_systems_in_contexts(self, subsystems_by_id):
            if not subsystems_by_id:
                return
            self._update_ctx.systems = subsystems_by_id
            self._update_emitters_ctx.depends_on(self._update_ctx)
            self._event_ctx.depends_on(self._update_ctx)
            self._particle_dead_ctx.depends_on(self._update_ctx)

        def _init_contexts(self):
            self._update_ctx = RenpFContext()
            self._update_ctx.system = self
            self._update_emitters_ctx = UpdateEmitterContext(self._update_ctx)
            self._event_ctx = EventContext(self._update_ctx)
            self._particle_dead_ctx = ParticleDeadContext(self._update_ctx)
            self._particle_appear_ctx = ParticleAppearContext(self._update_ctx)

        def _process_behavior_list(self, source, target_list):
            if source is None:
                return []
            elif callable(source) and issubclass(source, _Behavior):
                return [(source, {"oneshot": False})]
            else:
                result = [ ]
                for func, props in source:
                    behavior_id = props.get("renp_behavior_id")
                    if behavior_id is not None:
                        self.behaviors_by_id[behavior_id] = func
                    result.append((func, props))
                return result

        def _set_on_update(self, on_update):
            self.on_update = self._process_behavior_list(on_update, self.on_update)

        def _set_on_event(self, on_event):
            self.on_event = self._process_behavior_list(on_event, self.on_event)

        def _set_on_particle_dead(self, on_particle_dead):
            self.on_particle_dead = self._process_behavior_list(on_particle_dead, self.on_particle_dead)

        def _set_on_particle_appear(self, on_particle_appear):
            self.on_particle_appear = self._process_behavior_list(on_particle_appear, self.on_particle_appear)

        def _set_on_update_emitters_from_update_list(self):
            new_on_update = []
            emitters = []

            for update_func, props in self.on_update:
                if isinstance(update_func, Emitter):
                    emitters.append((update_func, props))
                else:
                    new_on_update.append((update_func, props))

            self.on_update = new_on_update
            self.on_update_emitters = emitters

        def _get_lifetime(self):
            if self.particles_data is None or self.particles_data.lifetime_type is None or self.particles_data.lifetime_timings is None:
                return 0.0

            #renpy.error("{}\n{}\n{}".format(self.particles_data, self.particles_data.lifetime_type, self.particles_data.lifetime_timings))

            lifetime_type = self.particles_data.lifetime_type
            lifetime_timings = self.particles_data.lifetime_timings

            if lifetime_type == "constant":
                return lifetime_timings

            return _lifetime_getters[lifetime_type](*lifetime_timings)

        def _get_acc_target_fps_delta(self):
            return 1.0 / self._acceleration_target_fps 

        def _calculate_smoothed_dtime(self):
            self._smoothed_dtime = (self._update_fidelity_delta_accumulator / self._update_fidelity + self._prev_dtime) * 0.5

        def _adjust_buffer_amount(self):
            margin = 0.003
            
            current_idx = self._buffer_index
            target_idx = current_idx
            
            if self._smoothed_dtime > self._acceleration_target_delta + self._buffer_amount_deltas[current_idx]:
                if current_idx < len(RenParticlesFast._BUFFER_AMOUNT) - 1:
                    target_idx = current_idx + 1
                    
            elif current_idx > 0:
                if self._smoothed_dtime < ((self._acceleration_target_delta + self._buffer_amount_deltas[current_idx - 1]) - margin):
                    target_idx = current_idx - 1
                    
            if current_idx != target_idx:
                self._buffer_index = target_idx
                self._buffer_amount = RenParticlesFast._BUFFER_AMOUNT[target_idx]
                self._buffer_offset = 0

        def _adjust_update_buffer_amount(self):
            margin = 0.003
            
            current_idx = self._update_buffer_index
            target_idx = current_idx
            
            if self._smoothed_dtime > self._acceleration_target_delta +  self._update_buffer_amount_deltas[current_idx]:
                if current_idx < len(RenParticlesFast._UPDATE_BUFFER_AMOUNT) - 1:
                    target_idx = current_idx + 1
                    
            elif current_idx > 0:
                if self._smoothed_dtime < ((self._acceleration_target_delta + self._update_buffer_amount_deltas[current_idx - 1]) - margin):
                    target_idx = current_idx - 1
                    
            if current_idx != target_idx:
                self._update_buffer_index = target_idx
                self._update_buffer_amount = RenParticlesFast._UPDATE_BUFFER_AMOUNT[target_idx]
                self._update_buffer_offset = 0

        def _get_system_debug_stats(self):
            stats = [
                "    --- Optimization Stats ---",
                "    Acceleration buffer: {} (offset: {})",
                "    Update buffer:       {} (offset: {})",
                "    Update fidelity:     {}",
                "    Update delay count:  {}",
                "    Current dtime:       {:.4f}",
                "    Delta accumulator:   {:.4f}",
                "    --------------------------"
            ]

            debug_data = "\n".join(stats).format(
                self._buffer_amount,
                self._buffer_offset,
                self._update_buffer_amount,
                self._update_buffer_offset,
                self._update_fidelity,
                self._update_delay_counter,
                self._dtime,
                self._update_fidelity_delta_accumulator_debug_last
            )

            #print(debug_data)
            
            return debug_data

        def reset(self):
            particles_properties = self.particles_data.particles_properties
            to_remove = [item for item in particles_properties.keys() if isinstance(item, RenParticle)]
            for item in to_remove:
                particles_properties.pop(item)

            self.destroy_all()
            self.particles_queue.clear()

            self.behaviors_by_id.clear()
            self._set_on_update(self.on_update_raw)
            self._set_on_update_emitters_from_update_list()
            self._set_on_event(self.on_event_raw)
            self._set_on_particle_dead(self.on_particle_dead_raw)
            self._set_on_particle_appear(self.on_particle_appear_raw)

        def freeze(self):
            self._frozen = True

        def unfreeze(self, redraw=True):
            self._frozen = False
            if redraw:
                renpy.redraw(self, 0.0)

        def create(self, d):
            s = _particles_pool.get()
            s.x = 0
            s.y = 0
            s.zorder = 0
            s.live = True
            lifetime = self._get_lifetime()
            s.lifetime = lifetime
            s.lifetime_max = lifetime
            s.manager = self
            s.events = False
            s.queued_transforms.clear()

            s.set_child(d)

            self.particles_queue.append(s)

            #Логично же. Чего я об этом не додумался -_-#
            self.particles_data.particles_properties[s] = { }

            new_on_particle_appear = []
            oneshotted_appear = []
            if self.on_particle_appear:
                self._particle_appear_ctx.particle = s
                self._particle_appear_ctx.delta = self._dtime
                for behavior_func, props in self.on_particle_appear:
                    return_value = behavior_func(self._particle_appear_ctx)
                    if props.get("oneshot", False) or return_value == UpdateState.Kill:
                        if (behavior_func, props) not in oneshotted_appear:
                            oneshotted_appear.append((behavior_func, props))
                    else:
                        if (behavior_func, props) not in new_on_particle_appear:
                            new_on_particle_appear.append((behavior_func, props))
                if oneshotted_appear:
                    self.oneshotted_on_appear.extend(oneshotted_appear)
                self.on_particle_appear = new_on_particle_appear

            return s

        def simulate_step(self, step=None):
            step = step or get_default_system_parameter("simulate_step")
            self.simulate_time -= step

            oneshotted_update = []
            oneshotted_dead = []
            new_on_update = list(self.on_update)
            new_on_particle_dead = []

            live_children = []

            self._update_ctx.delta = step
            self._particle_dead_ctx.delta = step

            for particle_idx, particle in enumerate(self.children):
                #<Симулируем, что время течёт, потом всё равно станет истинным при рендеринге>#
                self._update_ctx.st += step
                self._particle_dead_ctx.st += step

                self._particle_dead_ctx.particle = particle

                if not particle.live:
                    for behavior_func, props in self.on_particle_dead:
                        return_value = behavior_func(self._particle_dead_ctx)
                        if props.get("oneshot", False) or return_value == UpdateState.Kill:
                            if (behavior_func, props) not in oneshotted_dead:
                                oneshotted_dead.append((behavior_func, props))
                        else:
                            if (behavior_func, props) not in new_on_particle_dead:
                                new_on_particle_dead.append((behavior_func, props))
                    
                    self.particles_data.particles_properties.pop(particle, None)
                    _particles_pool.put(particle)
                    continue

                live_children.append(particle)

                self._update_ctx.particle = particle
                
                for update_func, props in new_on_update:
                    return_value = update_func(self._update_ctx)
                    if props.get("oneshot", False) or return_value == UpdateState.Kill:
                        if (update_func, props) not in oneshotted_update:
                            oneshotted_update.append((update_func, props))
            
            self.on_update = [item for item in new_on_update if item not in oneshotted_update]
            self.oneshotted_on_update.extend(oneshotted_update)

            if self.dead_child:
                self.children = live_children
                self.on_particle_dead = new_on_particle_dead
                self.oneshotted_on_dead.extend(oneshotted_dead)
                self.dead_child = False

        def simulate(self, simulate_time, step=None):
            self.simulate_time = simulate_time
            step = step or get_default_system_parameter("simulate_step")

            while self.simulate_time >= step:
                self.simulate_step(step)

        def render(self, width, height, st, at):
            if self.animation:
                st = at

            if not self._frozen and self.particles_queue:
                self.children.extend(self.particles_queue)
                self.particles_queue = []
                renpy.redraw(self, 0.0)
            
            self._prev_dtime = self._dtime
            self._dtime = max(0.0, st - self._old_st)
            self._update_fidelity_delta_accumulator += self._dtime
            self._old_st = st

            self.width = width
            self.height = height

            self._update_ctx.st = st
            self._particle_dead_ctx.st = st
            self._particle_appear_ctx.st = st

            if self._update_acceleration:
                true_delta = self._update_fidelity_delta_accumulator * self._update_buffer_amount
                self._update_ctx.delta = true_delta
                self._particle_dead_ctx.delta = true_delta
            else:
                self._update_ctx.delta = self._update_fidelity_delta_accumulator
                self._particle_dead_ctx.delta = self._update_fidelity_delta_accumulator

            if self.on_update_emitters and not self._frozen:
                new_update_emitters = []
                self._update_emitters_ctx.delta = self._dtime
                for emitter_func, props in self.on_update_emitters:
                    return_value = emitter_func(self._update_emitters_ctx)
                    if props.get("oneshot", False) or return_value == UpdateState.Kill:
                        self.oneshotted_on_update_emitters.append((emitter_func, props))
                    else:
                        new_update_emitters.append((emitter_func, props))
                self.on_update_emitters = new_update_emitters

            oneshotted_update = []
            oneshotted_dead = []
            new_on_update = list(self.on_update)
            new_on_particle_dead = []

            #Почему-то dead_child из SpriteManager не работает корректно. Причину не нашёл. Делаем так#
            has_death = False
            live_children = []

            do_update = self._update_delay_counter % self._update_fidelity == 0

            #self.cycle += 1
            if not self._frozen:
                if do_update:
                    for particle_idx, particle in enumerate(self.children):
                        if not particle.live:
                            has_death = True
                            self._particle_dead_ctx.particle = particle

                            for behavior_func, props in self.on_particle_dead:
                                return_value = behavior_func(self._particle_dead_ctx)
                                if props.get("oneshot", False) or return_value == UpdateState.Kill:
                                    if (behavior_func, props) not in oneshotted_dead:
                                        oneshotted_dead.append((behavior_func, props))
                                else:
                                    if (behavior_func, props) not in new_on_particle_dead:
                                        new_on_particle_dead.append((behavior_func, props))
                            
                            self.particles_data.particles_properties.pop(particle, None)
                            _particles_pool.put(particle)
                            continue

                        live_children.append(particle)

                        if not self._update_acceleration or (particle_idx % self._update_buffer_amount == self._update_buffer_offset):
                            self._update_ctx.particle = particle
                            
                            for update_func, props in new_on_update:
                                return_value = update_func(self._update_ctx)
                                if props.get("oneshot", False) or return_value == UpdateState.Kill:
                                    if (update_func, props) not in oneshotted_update:
                                        oneshotted_update.append((update_func, props))

                        if not self._transform_acceleration or (particle_idx % self._buffer_amount == self._buffer_offset):
                            particle.apply_transforms()

                if self._transform_acceleration or self._update_acceleration:
                    self._calculate_smoothed_dtime()
                    
                #<Transform Acceleration>#
                if self._transform_acceleration and do_update:
                    self._adjust_buffer_amount()
                    self._buffer_offset = (self._buffer_offset + 1) % self._buffer_amount

                #<Update Acceleration>#
                if self._update_acceleration and do_update:
                    self._adjust_update_buffer_amount()
                    self._update_buffer_offset = (self._update_buffer_offset + 1) % self._update_buffer_amount

                if self._update_delay_counter % self._update_fidelity == 0:
                    if _debug_stats:
                        self._update_fidelity_delta_accumulator_debug_last = self._update_fidelity_delta_accumulator
                    self._update_fidelity_delta_accumulator = 0.0
                self._update_delay_counter = (self._update_delay_counter + 1) % self._update_fidelity

                self.on_update = [item for item in new_on_update if item not in oneshotted_update]
                self.oneshotted_on_update.extend(oneshotted_update)

                if has_death:
                    self.children = live_children
                    self.on_particle_dead = new_on_particle_dead
                    self.oneshotted_on_dead.extend(oneshotted_dead)
                    self.dead_child = False #Но на всякий случай делаем сброс этого атрибута#
                    has_death = False

            if self.redraw is not None:
                renpy.display.render.redraw(self, self.redraw)

            if not self.ignore_time:
                self.displayable_map.clear()

            self.children.sort(key=lambda sc: sc.zorder)

            rv = renpy.display.render.Render(width, height)
            events = False

            caches = []

            for i in self.children:
                events |= i.events
                cache = i.cache
                r = cache.render

                if r is None:
                    if cache.st is None:
                        cache.st = st
                    cst = st - cache.st
                    r = renpy.render(cache.child_copy, width, height, cst, cst)
                    cache.render = r
                    cache.fast = (
                        (r.forward is None)
                        and (not r.mesh)
                        and (not r.uniforms)
                        and (not r.shaders)
                        and (not r.properties)
                        and (not r.xclipping)
                        and not (r.yclipping)
                    )
                    rv.depends_on(r)

                    caches.append(cache)

                w, h = r.get_size()
                r_size_half = (w * 0.5, h * 0.5)

                if cache.fast:
                    for child, xo, yo, _focus, _main in r.children:
                        rv.children.append((child, xo + i.x - r_size_half[0], yo + i.y - r_size_half[1], False, False))
                else:
                    rv.subpixel_blit(r, (i.x - r_size_half[0], i.y - r_size_half[1]))

            # for i in caches:
            #     i.render = None

            if _debug_stats:
                particle_pool_stats = renpy.store.Text("".join(_particles_pool.stats) + "\n{}".format(self._get_system_debug_stats()), size=16)
                rv.place(particle_pool_stats)

            return rv

        def event(self, ev, x, y, st):
            if self._particles_listening_events:
                for i in range(len(self.children) - 1, -1, -1):
                    s = self.children[i]

                    if s.events:
                        rv = s.cache.child.event(ev, x - s.x, y - s.y, st - s.cache.st)
                        if rv is not None:
                            return rv

            if self.on_event:
                new_on_event = []
                oneshotted = []

                self._event_ctx.st = st
                self._event_ctx.delta = self._dtime
                self._event_ctx.x = x
                self._event_ctx.y = y
                self._event_ctx.event = ev

                for event_func, props in self.on_event:
                    return_value = event_func(self._event_ctx)

                    if return_value == UpdateState.Kill or props.get("oneshot", False):
                        oneshotted.append((event_func, props))
                    else:
                        new_on_event.append((event_func, props))

                self.on_event = new_on_event
                self.oneshotted_on_event.extend(oneshotted)
    
    class RenParticleFastGroup(renpy.Displayable):
        def __init__(self, systems=None, redraw=None, layer=None, **properties):
            super(RenParticleFastGroup, self).__init__(**properties)

            self.layer = layer

            self.redraw = redraw
            self.systems = systems or [ ]
            self.systems_by_id = self._create_systems_by_id_map()

            self._link_systems_in_contexts()

            self.simulate_time = 0.0

        def _create_systems_by_id_map(self):
            return { system.system_id: system for system in self.systems if system.system_id }

        def _link_systems_in_contexts(self):
            for system in self.systems:
                system.set_systems_in_contexts(self.systems_by_id)

        def reset(self):
            for system in self.systems:
                system.reset()

        def freeze(self):
            for system in self.systems:
                system.freeze()

        def unfreeze(self, redraw=True):
            for system in self.systems:
                system.unfreeze(False)

            if redraw:
                renpy.redraw(self, 0.0)

        def freeze_one(self, id):
            system = self.systems_by_id.get(id, None)
            if system:
                system.freeze()

        def unfreeze_one(self, id, redraw=True):
            system = self.systems_by_id.get(id, None)
            if system:
                system.unfreeze(False)
                
            if redraw:
                renpy.redraw(self, 0.0)

        def get_info(self):
            lines = [ ]
            lines.append("=" * 40)
            lines.append("MULTIPLE FAST REN-PARTICLE SYSTEM")
            lines.append("=" * 40)

            for system in self.systems:
                lines.append(system.get_info())

            lines.append("=" * 40)
            return "\n".join(lines)

        def visit(self):
            return self.systems[:]
        
        def simulate_step(self, simulate_step=None):
            step = step or get_default_system_parameter("simulate_step")
            self.simulate_time -= step

            for system in self.systems:
                system.simulate_step(step)

        def simulate(self, simulate_time, simulate_step=None):
            self.simulate_time = simulate_time
            step = step or get_default_system_parameter("simulate_step")

            for system in self.systems:
                system.simulate_time = self.simulate_time

            while self.simulate_time >= step:
                self.simulate_step(step)

        def render(self, width, height, st, at):
            main_render = renpy.Render(width, height)

            #dbg_lines = []
            for system in self.systems:
                #dbg_lines.append(str(len(system.particles_data.particles_properties)))

                system_render = system.render(width, height, st, at)
                main_render.subpixel_blit(system_render, (0, 0))

            if self.redraw is not None:
                renpy.redraw(self, self.redraw)

            # dbg = renpy.store.Text("\n".join(dbg_lines), size=32)

            # main_render.place(dbg)

            return main_render

        def event(self, ev, x, y, st):
            return_value = None
            for system in self.systems:
                result = system.event(ev, x, y, st)
                if result is not None:
                    return_value = result
            return return_value
