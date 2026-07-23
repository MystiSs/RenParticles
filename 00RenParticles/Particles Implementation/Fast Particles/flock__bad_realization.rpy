# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

#Не работает нифига, либо я чёт не понимаю#

init -1115 python in renparticles:
    import math
    import random

    class Flock(_UpdateBehavior):
        """Стайное поведение (Boids) с тремя основными правилами:
        
        1. Разделение (Separation) — избегание столкновений с соседями
        2. Выравнивание (Alignment) — синхронизация направления с соседями
        3. Сплочение (Cohesion) — притяжение к центру стаи
        """
        
        separation_radius = 30.0     # Радиус разделения
        alignment_radius = 80.0      # Радиус выравнивания
        cohesion_radius = 120.0      # Радиус сплочения
        
        separation_weight = 1.5      # Вес разделения
        alignment_weight = 1.0       # Вес выравнивания
        cohesion_weight = 1.0        # Вес сплочения
        
        max_speed = 200.0            # Максимальная скорость
        min_speed = 20.0             # Минимальная скорость
        max_force = 1000.0           # Максимальная сила (избегаем рывков)
        screen_bounds = True         # Удерживать в пределах экрана
        margin = 50.0                # Отступ от краёв
        
        separation_radius_range = None # [min, max] или число
        alignment_radius_range = None  # [min, max] или число
        cohesion_radius_range = None   # [min, max] или число
        separation_weight_range = None # [min, max] или число
        alignment_weight_range = None  # [min, max] или число
        cohesion_weight_range = None   # [min, max] или число
        max_speed_range = None         # [min, max] или число
        min_speed_range = None         # [min, max] или число

        _ranges_normalized = False
        
        _check_is_valid = True
        _valid = {
            "separation_radius", "alignment_radius", "cohesion_radius",
            "separation_weight", "alignment_weight", "cohesion_weight",
            "max_speed", "min_speed", "max_force", "screen_bounds", "margin",
            "separation_radius_range", "alignment_radius_range", "cohesion_radius_range",
            "separation_weight_range", "alignment_weight_range", "cohesion_weight_range",
            "max_speed_range", "min_speed_range"
        }
        
        _RENP_FLOCK = "_renp_flock_data"
        _COUNTER = 0
        
        _neighbors_cache = {}
        _cache_frame = 0

        def __init__(self):
            self._RENP_FLOCK = "{}_{}".format(self._RENP_FLOCK, self._COUNTER)
            Flock._COUNTER += 1

        def get_key(self):
            return self._RENP_FLOCK

        def _normalize_ranges(self):
            ranges = {
                "separation_radius_range": self.separation_radius,
                "alignment_radius_range": self.alignment_radius,
                "cohesion_radius_range": self.cohesion_radius,
                "separation_weight_range": self.separation_weight,
                "alignment_weight_range": self.alignment_weight,
                "cohesion_weight_range": self.cohesion_weight,
                "max_speed_range": self.max_speed,
                "min_speed_range": self.min_speed
            }
            
            for attr, default in ranges.items():
                value = getattr(self, attr)
                if value is None:
                    setattr(self, attr, [None, None])
                elif isinstance(value, (int, float)):
                    setattr(self, attr, [value, value])
                elif len(value) == 1:
                    setattr(self, attr, [value[0], value[0]])

            self._ranges_normalized = True

        def _get_flock_params(self):
            sep_r = self.separation_radius
            if self.separation_radius_range[0] is not None:
                min_r = self.separation_radius_range[0]
                max_r = self.separation_radius_range[1] if self.separation_radius_range[1] is not None else min_r
                sep_r += random.uniform(-min_r, max_r)
                sep_r = max(1.0, sep_r)
            
            ali_r = self.alignment_radius
            if self.alignment_radius_range[0] is not None:
                min_r = self.alignment_radius_range[0]
                max_r = self.alignment_radius_range[1] if self.alignment_radius_range[1] is not None else min_r
                ali_r += random.uniform(-min_r, max_r)
                ali_r = max(1.0, ali_r)
            
            coh_r = self.cohesion_radius
            if self.cohesion_radius_range[0] is not None:
                min_r = self.cohesion_radius_range[0]
                max_r = self.cohesion_radius_range[1] if self.cohesion_radius_range[1] is not None else min_r
                coh_r += random.uniform(-min_r, max_r)
                coh_r = max(1.0, coh_r)
            
            sep_w = self.separation_weight
            if self.separation_weight_range[0] is not None:
                min_w = self.separation_weight_range[0]
                max_w = self.separation_weight_range[1] if self.separation_weight_range[1] is not None else min_w
                sep_w += random.uniform(-min_w, max_w)
                sep_w = max(0.0, sep_w)
            
            ali_w = self.alignment_weight
            if self.alignment_weight_range[0] is not None:
                min_w = self.alignment_weight_range[0]
                max_w = self.alignment_weight_range[1] if self.alignment_weight_range[1] is not None else min_w
                ali_w += random.uniform(-min_w, max_w)
                ali_w = max(0.0, ali_w)
            
            coh_w = self.cohesion_weight
            if self.cohesion_weight_range[0] is not None:
                min_w = self.cohesion_weight_range[0]
                max_w = self.cohesion_weight_range[1] if self.cohesion_weight_range[1] is not None else min_w
                coh_w += random.uniform(-min_w, max_w)
                coh_w = max(0.0, coh_w)
            
            max_speed = self.max_speed
            if self.max_speed_range[0] is not None:
                min_s = self.max_speed_range[0]
                max_s = self.max_speed_range[1] if self.max_speed_range[1] is not None else min_s
                max_speed += random.uniform(-min_s, max_s)
                max_speed = max(self.min_speed, max_speed)
            
            min_speed = self.min_speed
            if self.min_speed_range[0] is not None:
                min_s = self.min_speed_range[0]
                max_s = self.min_speed_range[1] if self.min_speed_range[1] is not None else min_s
                min_speed += random.uniform(-min_s, max_s)
                min_speed = max(0.0, min(self.max_speed, min_speed))
            
            initial_angle = random.uniform(0, 2 * math.pi)
            
            return {
                "sep_r": sep_r,
                "ali_r": ali_r,
                "coh_r": coh_r,
                
                "sep_w": sep_w,
                "ali_w": ali_w,
                "coh_w": coh_w,
                
                "max_speed": max_speed,
                "min_speed": min_speed,
                
                "angle": initial_angle,
                "velocity": [math.cos(initial_angle) * max_speed, math.sin(initial_angle) * max_speed],
                "time": 0.0
            }

        def _get_neighbors(self, particle, system, props, params):
            neighbors = {
                "sep": [],  # Для разделения (близкие)
                "ali": [],  # Для выравнивания
                "coh": []   # Для сплочения
            }
            
            # Получаем все живые частицы
            living_particles = system.children
            
            for other in living_particles:
                if other is particle or not other.live:
                    continue
                
                # Расстояние до соседа
                dx = other.x - particle.x
                dy = other.y - particle.y
                distance = math.hypot(dx, dy)
                
                # Проверяем радиусы
                if distance < params["sep_r"]:
                    neighbors["sep"].append((other, dx, dy, distance))
                elif distance < params["ali_r"]:
                    neighbors["ali"].append((other, dx, dy, distance))
                elif distance < params["coh_r"]:
                    neighbors["coh"].append((other, dx, dy, distance))
            
            return neighbors

        def _calculate_separation(self, neighbors, params):
            if not neighbors["sep"]:
                return [0.0, 0.0]
            
            steer_x = 0.0
            steer_y = 0.0
            
            for _, dx, dy, distance in neighbors["sep"]:
                if distance < 0.001:
                    continue
                
                force = 1.0 / distance
                steer_x += dx * force
                steer_y += dy * force
            
            mag = math.hypot(steer_x, steer_y)
            if mag > 0:
                steer_x = (steer_x / mag) * params["sep_w"]
                steer_y = (steer_y / mag) * params["sep_w"]
            
            return [steer_x, steer_y]

        def _calculate_alignment(self, neighbors, props, params):
            if not neighbors["ali"]:
                return [0.0, 0.0]
            
            avg_x = 0.0
            avg_y = 0.0
            count = 0
            
            for other, _, _, _ in neighbors["ali"]:
                other_data = props.get(other, {})
                flock_data = other_data.get(self._RENP_FLOCK, {})
                
                vel = flock_data.get("velocity", [0.0, 0.0])
                if vel[0] != 0 or vel[1] != 0:
                    avg_x += vel[0]
                    avg_y += vel[1]
                    count += 1
            
            if count == 0:
                return [0.0, 0.0]
            
            avg_x /= count
            avg_y /= count
            
            mag = math.hypot(avg_x, avg_y)
            if mag > 0:
                avg_x = (avg_x / mag) * params["ali_w"]
                avg_y = (avg_y / mag) * params["ali_w"]
            
            return [avg_x, avg_y]

        def _calculate_cohesion(self, neighbors, particle, params):
            if not neighbors["coh"]:
                return [0.0, 0.0]
            
            center_x = 0.0
            center_y = 0.0
            count = 0
            
            for other, _, _, _ in neighbors["coh"]:
                center_x += other.x
                center_y += other.y
                count += 1
            
            if count == 0:
                return [0.0, 0.0]
            
            center_x /= count
            center_y /= count
            
            dx = center_x - particle.x
            dy = center_y - particle.y
            distance = math.hypot(dx, dy)
            
            if distance < 0.001:
                return [0.0, 0.0]
            
            steer_x = (dx / distance) * params["coh_w"]
            steer_y = (dy / distance) * params["coh_w"]
            
            return [steer_x, steer_y]

        def _apply_force(self, velocity, force_x, force_y, params, delta):
            velocity[0] += force_x * delta
            velocity[1] += force_y * delta
            
            # Ограничение скорости
            speed = math.hypot(velocity[0], velocity[1])
            if speed > params["max_speed"]:
                velocity[0] = (velocity[0] / speed) * params["max_speed"]
                velocity[1] = (velocity[1] / speed) * params["max_speed"]
            elif speed < params["min_speed"] and speed > 0:
                velocity[0] = (velocity[0] / speed) * params["min_speed"]
                velocity[1] = (velocity[1] / speed) * params["min_speed"]
            
            force_mag = math.hypot(force_x, force_y)
            if force_mag > self.max_force:
                velocity[0] += (force_x / force_mag) * self.max_force * delta
                velocity[1] += (force_y / force_mag) * self.max_force * delta
            
            return velocity

        def _apply_screen_bounds(self, particle, system):
            margin = self.margin
            
            if particle.x < margin:
                particle.x = margin
            elif particle.x > system.width - margin:
                particle.x = system.width - margin
            
            if particle.y < margin:
                particle.y = margin
            elif particle.y > system.height - margin:
                particle.y = system.height - margin

        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            system = context.system
            props = system.particles_data.particles_properties

            if particle not in props:
                return UpdateState.Pass

            if not self._ranges_normalized:
                self._normalize_ranges()

            particle_data = props[particle]
            if self._RENP_FLOCK not in particle_data:
                particle_data[self._RENP_FLOCK] = self._get_flock_params()
            
            flock_data = particle_data[self._RENP_FLOCK]
            flock_data["time"] += delta

            neighbors = self._get_neighbors(particle, system, props, flock_data)

            sep_force = self._calculate_separation(neighbors, flock_data)
            
            ali_force = self._calculate_alignment(neighbors, props, flock_data)
            
            coh_force = self._calculate_cohesion(neighbors, particle, flock_data)

            velocity = flock_data["velocity"]
            
            self._apply_force(velocity, sep_force[0], sep_force[1], flock_data, delta)
            self._apply_force(velocity, ali_force[0], ali_force[1], flock_data, delta)
            self._apply_force(velocity, coh_force[0], coh_force[1], flock_data, delta)

            particle.x += velocity[0] * delta
            particle.y += velocity[1] * delta

            if self.screen_bounds:
                self._apply_screen_bounds(particle, system)

            return UpdateState.Pass
