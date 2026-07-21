# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import math

    class EventZone(_Behavior):
        """
        Базовый обработчик зоны событий.
        Вызывает функцию, когда частица попадает в заданную зону.
        """
        x = 0.0
        y = 0.0
        width = 100.0
        height = 100.0
        shape = "rect"  # "rect", "circle", "ellipse" #
        
        function = None  # Сигнатура: function(particle, context, behavior) , но может быть списком#
        once = True
        
        particle_local = False
        inverse = False

        _normalized = False
        
        _check_is_valid = True
        _valid = {"x", "y", "width", "height", "shape", "function", "once", "particle_local", "inverse"}
        
        _RENP_ZONE = "_renp_event_zone"
        _RENP_ZONE_COUNTER = 0
        
        def __init__(self):
            self._RENP_ZONE = "{}_{}".format(self._RENP_ZONE, self._RENP_ZONE_COUNTER)
            EventZone._RENP_ZONE_COUNTER += 1
        
        def _get_zone_center(self, particle):
            if self.particle_local:
                return particle.x + self.x, particle.y + self.y
            else:
                return self.x, self.y
        
        def _check_rect(self, px, py, cx, cy):
            half_w = self.width / 2.0
            half_h = self.height / 2.0
            
            in_zone = (cx - half_w <= px <= cx + half_w) and (cy - half_h <= py <= cy + half_h)
            return in_zone
        
        def _check_circle(self, px, py, cx, cy):
            radius = self.width / 2.0 
            dx = px - cx
            dy = py - cy
            distance = math.sqrt(dx*dx + dy*dy)
            
            in_zone = distance <= radius
            return in_zone
        
        def _check_ellipse(self, px, py, cx, cy):
            half_w = self.width / 2.0
            half_h = self.height / 2.0
            
            dx = px - cx
            dy = py - cy
            normalized = (dx*dx) / (half_w*half_w) + (dy*dy) / (half_h*half_h)
            
            in_zone = normalized <= 1.0
            return in_zone
        
        def _is_in_zone(self, particle):
            px = particle.x
            py = particle.y
            
            cx, cy = self._get_zone_center(particle)
            
            if self.shape == "circle":
                in_zone = self._check_circle(px, py, cx, cy)
            elif self.shape == "ellipse":
                in_zone = self._check_ellipse(px, py, cx, cy)
            else:
                in_zone = self._check_rect(px, py, cx, cy)
            
            if self.inverse:
                in_zone = not in_zone
            
            return in_zone

        def _normalize_functions(self):
            if self.function is None:
                self.function = []
            
            if isinstance(self.function, (list, tuple)):
                self.function = [func for func in self.function if func is not None]
            else:
                self.function = [self.function]
            
            self._normalized = True
        
        def _call_callbacks(self, particle, context, behavior):
            if not self._normalized:
                self._normalize_functions()

            for callback in self.function:
                callback(particle, context, self)
        
        def _get_particle_zone_data(self, particle_data):
            if self._RENP_ZONE not in particle_data:
                particle_data[self._RENP_ZONE] = {
                    "triggered": False,
                    "last_state": False
                }
            return particle_data[self._RENP_ZONE]
        
        def __call__(self, context):
            particle = context.particle
            system = context.system
            delta = context.delta
            props = system.particles_data.particles_properties
            
            if particle not in props:
                return UpdateState.Pass
            
            if self.function is None:
                return UpdateState.Pass
            
            particle_data = props[particle]
            zone_data = self._get_particle_zone_data(particle_data)
            
            in_zone = self._is_in_zone(particle)
            zone_data["last_state"] = in_zone
            
            if in_zone:
                if not self.once or (self.once and not zone_data["triggered"]):
                    self._call_callbacks(particle, context, self)
                    zone_data["triggered"] = True
            
            return UpdateState.Pass
    
    class EventZoneOnEnter(EventZone):
        """
        Вариант EventZone, который срабатывает только при входе в зону.
        Функция вызывается в момент перехода из "вне зоны" в "внутри зоны".
        """
        def __init__(self):
            super(EventZoneOnEnter, self).__init__()
        
        def __call__(self, context):
            particle = context.particle
            system = context.system
            props = system.particles_data.particles_properties
            
            if particle not in props:
                return UpdateState.Pass
            
            if self.function is None:
                return UpdateState.Pass
            
            particle_data = props[particle]
            zone_data = self._get_particle_zone_data(particle_data)
            
            in_zone = self._is_in_zone(particle)
            was_in_zone = zone_data.get("last_state", False)
            zone_data["last_state"] = in_zone
            
            if in_zone and not was_in_zone:
                if not self.once or (self.once and not zone_data["triggered"]):
                    self._call_callbacks(particle, context, self)
                    zone_data["triggered"] = True
            
            return UpdateState.Pass

    class EventZoneOnExit(EventZone):
        """
        Вариант EventZone, который срабатывает только при выходе из зоны.
        Функция вызывается в момент перехода из "внутри зоны" в "вне зоны".
        """
        def __init__(self):
            super(EventZoneOnExit, self).__init__()
        
        def __call__(self, context):
            particle = context.particle
            system = context.system
            props = system.particles_data.particles_properties
            
            if particle not in props:
                return UpdateState.Pass
            
            if self.function is None:
                return UpdateState.Pass
            
            particle_data = props[particle]
            zone_data = self._get_particle_zone_data(particle_data)
            
            in_zone = self._is_in_zone(particle)
            was_in_zone = zone_data.get("last_state", False)
            zone_data["last_state"] = in_zone
            
            if not in_zone and was_in_zone:
                if not self.once or (self.once and not zone_data["triggered"]):
                    self._call_callbacks(particle, context, self)
                    zone_data["triggered"] = True
            
            return UpdateState.Pass

    class EventZoneWhileIn(EventZone):
        """
        Вариант EventZone, который вызывает функцию каждый кадр, пока частица в зоне.
        Функция вызывается каждый кадр с delta временем.
        """
        def __init__(self):
            super(EventZoneWhileIn, self).__init__()
        
        def __call__(self, context):
            particle = context.particle
            system = context.system
            props = system.particles_data.particles_properties
            
            if particle not in props:
                return UpdateState.Pass
            
            if self.function is None:
                return UpdateState.Pass
            
            particle_data = props[particle]
            zone_data = self._get_particle_zone_data(particle_data)
            
            in_zone = self._is_in_zone(particle)
            zone_data["last_state"] = in_zone
            
            if in_zone:
                if not self.once or (self.once and not zone_data["triggered"]):
                    self._call_callbacks(particle, context, self)
                    zone_data["triggered"] = True
            
            return UpdateState.Pass
    
    def on_enter_zone_debug(particle, context, behavior):
        particle.destroy()
        print("Zone Entered!\nP: {}\nCTX: {}\nBEH: {}".format(particle, context, behavior))
