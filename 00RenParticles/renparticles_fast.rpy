# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1337 python in renparticles:
    import random
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

    class RenSprite(Sprite):
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
            
            cache = SpriteCache()
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
            super(RenSprite, self).set_child(d)
            self._base_image = None
    
    class RenParticlesFast(SpriteManager):
        def __init__(self, on_update=None, on_event=None, on_particle_dead=None, particles_data=None, ignore_time=False, redraw=None, layer=None, **properties):
            super(RenParticlesFast, self).__init__(ignore_time=ignore_time, **properties)
            self.layer = layer

            self.particles_queue = [ ]

            self.animation = False

            self.particles_data = particles_data
            self.redraw = redraw

            self._set_on_update(on_update)
            self._set_on_update_emitters_from_update_list()
            self._set_on_event(on_event)
            self._set_on_particle_dead(on_particle_dead)
            self.oneshotted_on_update = [ ]
            self.oneshotted_on_update_emitters = [ ]
            self.oneshotted_on_event = [ ]
            self.oneshotted_on_dead = [ ]

            self.on_update_raw = on_update
            self.on_event_raw = on_event
            self.on_particle_dead_raw = on_particle_dead

            self._old_st = 0.0
            self._dtime = 0.0

            self.system_id = None

            self._frozen = False

            self._init_contexts()

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

        def _set_on_update(self, on_update):
            if on_update is None:
                self.on_update = []
            elif callable(on_update):
                self.on_update = [(on_update, {"oneshot": False})]
            else:
                self.on_update = [(func, props) for func, props in on_update]

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

        def _set_on_event(self, on_event):
            if on_event is None:
                self.on_event = []
            elif callable(on_event):
                self.on_event = [(on_event, {"oneshot": False})]
            else:
                self.on_event = [(func, props) for func, props in on_event]

        def _set_on_particle_dead(self, on_particle_dead):
            if on_particle_dead is None:
                self.on_particle_dead = []
            elif callable(on_particle_dead):
                self.on_particle_dead = [(on_particle_dead, {"oneshot": False})]
            else:
                self.on_particle_dead = [(func, props) for func, props in on_particle_dead]

        def _get_lifetime(self):
            if self.particles_data is None or self.particles_data.lifetime_type is None or self.particles_data.lifetime_timings is None:
                return 0.0

            #renpy.error("{}\n{}\n{}".format(self.particles_data, self.particles_data.lifetime_type, self.particles_data.lifetime_timings))

            lifetime_type = self.particles_data.lifetime_type
            lifetime_timings = self.particles_data.lifetime_timings

            if lifetime_type == "constant":
                return lifetime_timings

            return _lifetime_getters[lifetime_type](*lifetime_timings)

        def reset(self):
            particles_properties = self.particles_data.particles_properties
            to_remove = [item for item in particles_properties.keys() if isinstance(item, RenSprite)]
            for item in to_remove:
                particles_properties.pop(item)

            self.destroy_all()
            self.particles_queue.clear()

            self._set_on_update(self.on_update_raw)
            self._set_on_update_emitters_from_update_list()
            self._set_on_event(self.on_event_raw)
            self._set_on_particle_dead(self.on_particle_dead_raw)

        def freeze(self):
            self._frozen = True

        def unfreeze(self, redraw=True):
            self._frozen = False
            if redraw:
                renpy.redraw(self, 0.0)

        def create(self, d):
            s = RenSprite()
            s.x = 0
            s.y = 0
            s.zorder = 0
            s.live = True
            lifetime = self._get_lifetime()
            s.lifetime = lifetime
            s.lifetime_max = lifetime
            s.manager = self
            s.events = False

            s.set_child(d)

            self.particles_queue.append(s)

            return s

        def render(self, width, height, st, at):
            if self.animation:
                st = at

            if not self._frozen and self.particles_queue:
                self.children.extend(self.particles_queue)
                self.particles_queue = []
                renpy.redraw(self, 0.0)

            self._dtime = max(0.0, st - self._old_st)
            self._old_st = st

            self.width = width
            self.height = height

            self._update_ctx.st = st
            self._update_ctx.delta = self._dtime
            self._particle_dead_ctx.st = st
            self._particle_dead_ctx.delta = self._dtime

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

            live_children = []

            if not self._frozen:
                for particle in self.children:
                    self._update_ctx.particle = particle
                    self._particle_dead_ctx.particle = particle

                    #<On update part>#
                    for update_func, props in new_on_update:
                        return_value = update_func(self._update_ctx)
                        if props.get("oneshot", False) or return_value == UpdateState.Kill:
                            if (update_func, props) not in oneshotted_update:
                                oneshotted_update.append((update_func, props))

                    #<On some particle dead part>#
                    if self.dead_child and not particle.live:
                        for behavior_func, props in self.on_particle_dead:
                            return_value = behavior_func(self._particle_dead_ctx)
                            if props.get("oneshot", False) or return_value == UpdateState.Kill:
                                if (behavior_func, props) not in oneshotted_dead:
                                    oneshotted_dead.append((behavior_func, props))
                            else:
                                if (behavior_func, props) not in new_on_particle_dead:
                                    new_on_particle_dead.append((behavior_func, props))

                        self.particles_data.particles_properties.pop(particle, None)
                    else:
                        live_children.append(particle)
                        #<Scheduled transforms>#
                        particle.apply_transforms()

                self.on_update = [item for item in new_on_update if item not in oneshotted_update]
                self.oneshotted_on_update.extend(oneshotted_update)

                if self.dead_child:
                    self.children = live_children
                    self.on_particle_dead = new_on_particle_dead
                    self.oneshotted_on_dead.extend(oneshotted_dead)
                    self.dead_child = False

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

            for i in caches:
                i.render = None

            return rv

        def event(self, ev, x, y, st):
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
