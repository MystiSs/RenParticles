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
        def __init__(self, **properties):
            for key, value in properties.items():
                setattr(self, key, value)
        
        def __getattr__(self, name):
            return None
            #renpy.error("Attribute '{}' does not exist in {}".format(name, self))

    class RenSprite(Sprite):
        lifetime = 0.0

        def __getattr__(self, name):
            return None
    
    class RenParticlesFast(SpriteManager):
        def __init__(self, on_update=None, on_event=None, on_particle_dead=None, particles_data=None, redraw=None, **properties):
            super(RenParticlesFast, self).__init__(**properties) 
            self.animation = False

            self.particles_data = particles_data
            self.redraw = redraw

            self._set_on_update(on_update)
            self._set_on_event(on_event)
            self._set_on_particle_dead(on_particle_dead)
            self.oneshotted_on_update = [ ]
            self.oneshotted_on_event = [ ]
            self.oneshotted_on_dead = [ ]

            self._old_st = 0.0
            self._dtime = 0.0

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
        
        def _set_on_update(self, on_update):
            if on_update is None:
                self.on_update = None
            self.on_update = [(on_update[0], on_update[1])] if callable(on_update[0]) else [(func, props) for func, props in on_update]
        
        def _set_on_event(self, on_event):
            if on_event is None:
                self.on_event = None
            self.on_event = [(on_event[0], on_event[1])] if callable(on_event[0]) else [(func, props) for func, props in on_event]

        def _set_on_particle_dead(self, on_particle_dead):
            if on_particle_dead is None:
                self.on_particle_dead = None
            self.on_particle_dead = [(on_particle_dead[0], on_particle_dead[1])] if callable(on_particle_dead[0]) else [(func, props) for func, props in on_particle_dead]

        def delta(self):
            return self._dtime

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

            self.children.append(s)

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

            if self.on_update:
                new_on_update = [ ]
                
                for update, props in self.on_update:
                    return_value = update(st, self)
                    if not props.get("oneshot", False) and return_value != UpdateState.Kill:
                        new_on_update.append((update, props))
                        self.oneshotted_on_update.append((update, props))
                
                self.on_update = new_on_update
                
                if self.redraw is not None:
                    renpy.display.render.redraw(self, self.redraw)

            if not self.ignore_time:
                self.displayable_map.clear()

            if self.dead_child:
                new_children = [ ]
                new_on_dead = [ ]
                for particle in self.children:
                    if not particle.live:
                        for on_particle_dead, props in self.on_particle_dead:
                            return_value = on_particle_dead(particle, st, self)
                            if not props.get("oneshot", False) and return_value != UpdateState.Kill:
                                new_on_dead.append((on_particle_dead, props))
                                self.oneshotted_on_dead.append((on_particle_dead, props))
                    else:
                        new_children.append(particle)
                    
                    self.on_particle_dead = new_on_dead
                
                self.children = new_children

            self.children.sort(key=lambda sc: sc.zorder)

            caches = []

            rv = renpy.display.render.Render(width, height)

            events = False

            for i in self.children:
                events |= i.events

                cache = i.cache
                r = i.cache.render
                if cache.render is None:
                    if cache.st is None:
                        cache.st = st

                    cst = st - cache.st

                    cache.render = r = renpy.render(cache.child_copy, width, height, cst, cst)
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
                new_on_event = [ ]

                for event, props in self.on_event:
                    return_value = event(ev, x, y, st, self)
                    if return_value is not UpdateState.Kill or props.get("oneshot", False):
                        new_on_event.append((event, props))
                
                self.on_event = new_on_event
            else:
                return None
