init -1337 python in renparticles:
    import random
    from renpy.store import SpriteManager
    from renpy.store import Sprite
    from builtins import min, max


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
    
    class RenpFContext:
        system = None
        st = None
        delta = None
        particle = None

        def __init__(self, other_ctx=None):
            if isinstance(other_ctx, RenpFContext):
                self.copy(other_ctx)

        def copy(self, other):
            self.system = other.system
            self.st = other.st
            self.delta = other.delta
            self.particle = None
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
    
    class RenParticlesFast(SpriteManager):
        def __init__(self, on_update=None, on_event=None, on_particle_dead=None, particles_data=None, redraw=None, **properties):
            super(RenParticlesFast, self).__init__(**properties)
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

            self._old_st = 0.0
            self._dtime = 0.0

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

        def create(self, d):
            s = RenSprite()
            s.x = 0
            s.y = 0
            s.zorder = 0
            s.live = True
            s.lifetime = self._get_lifetime()
            s.manager = self
            s.events = False

            s.set_child(d)

            self.particles_queue.append(s)

            return s

        def _get_lifetime(self):
            if self.particles_data is None or self.particles_data.lifetime_type is None or self.particles_data.lifetime_timings is None:
                return 0.0

            lifetime_type = self.particles_data.lifetime_type
            lifetime_timings = self.particles_data.lifetime_timings

            return _lifetime_getters[lifetime_type](*lifetime_timings)

        def render(self, width, height, st, at):
            if self.animation:
                st = at

            self._dtime = max(0.0, st - self._old_st)
            self._old_st = st

            self.width = width
            self.height = height

            self._update_ctx.st = st
            self._update_ctx.delta = self._dtime
            self._particle_dead_ctx.st = st
            self._particle_dead_ctx.delta = self._dtime

            if self.on_update_emitters:
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

            if self.particles_queue:
                self.children.extend(self.particles_queue)
                self.particles_queue = []
                renpy.redraw(self, 0.0)

            self.children.sort(key=lambda sc: sc.zorder)

            caches = []

            rv = renpy.display.render.Render(width, height)
            events = False

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

                if cache.fast:
                    for child, xo, yo, _focus, _main in r.children:
                        rv.children.append((child, xo + i.x, yo + i.y, False, False))
                else:
                    rv.subpixel_blit(r, (i.x, i.y))

            for cache in caches:
                cache.render = None

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
