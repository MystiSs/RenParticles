# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import math
    import random

    class Wander(_UpdateBehavior):
        """Плавное блуждание с поворотами"""
        
        radius = 15.0               # Радиус блуждания (максимальное смещение)
        speed = 35.0                # Базовая скорость перемещения
        turn_chance = 0.35          # Шанс смены направления за кадр (0.0 - 1.0)
        turn_angle = 180.0          # Максимальный угол поворота (в градусах)
        smoothness = 0.33           # Плавность поворота (0.0 - 1.0)
        
        min_speed = 10.0            # Минимальная скорость блуждания
        max_speed = 100.0           # Максимальная скорость блуждания
        screen_bounds = True        # Удерживать в пределах экрана
        
        radius_range = None         # [min, max] или число
        speed_range = None          # [min, max] или число
        turn_chance_range = None    # [min, max] или число
        turn_angle_range = None     # [min, max] или число
        smoothness_range = None     # [min, max] или число

        _ranges_normalized = False
        
        _check_is_valid = True
        _valid = {
            "radius", "speed", "turn_chance", "turn_angle", "smoothness",
            "min_speed", "max_speed", "screen_bounds",
            "radius_range", "speed_range", "turn_chance_range",
            "turn_angle_range", "smoothness_range"
        }
        
        _RENP_WANDER = "_renp_wander_data"
        _COUNTER = 0

        def __init__(self):
            self._RENP_WANDER = "{}_{}".format(self._RENP_WANDER, self._COUNTER)
            Wander._COUNTER += 1       

        def get_key(self):
            return self._RENP_WANDER     

        def _normalize_ranges(self):
            ranges = {
                "radius_range": self.radius,
                "speed_range": self.speed,
                "turn_chance_range": self.turn_chance,
                "turn_angle_range": self.turn_angle,
                "smoothness_range": self.smoothness
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

        def _get_wander_params(self):
            radius = self.radius
            if self.radius_range[0] is not None:
                min_r = self.radius_range[0]
                max_r = self.radius_range[1] if self.radius_range[1] is not None else min_r
                radius += random.uniform(-min_r, max_r)
                radius = max(1.0, radius)
            
            speed = self.speed
            if self.speed_range[0] is not None:
                min_s = self.speed_range[0]
                max_s = self.speed_range[1] if self.speed_range[1] is not None else min_s
                speed += random.uniform(-min_s, max_s)
                speed = max(self.min_speed, min(self.max_speed, speed))
            
            # Плавность
            smoothness = self.smoothness
            if self.smoothness_range[0] is not None:
                min_sm = self.smoothness_range[0]
                max_sm = self.smoothness_range[1] if self.smoothness_range[1] is not None else min_sm
                smoothness += random.uniform(-min_sm, max_sm)
                smoothness = max(0.0, min(1.0, smoothness))

            turn_chance = self.turn_chance
            if self.turn_chance_range[0] is not None:
                min_tc = self.turn_chance_range[0]
                max_tc = self.turn_chance_range[1] if self.turn_chance_range[1] is not None else min_tc
                turn_chance += random.uniform(-min_tc, max_tc)
                turn_chance = max(0.0, min(1.0, turn_chance))

            # Угол поворота
            turn_angle = self.turn_angle
            if self.turn_angle_range[0] is not None:
                min_ta = self.turn_angle_range[0]
                max_ta = self.turn_angle_range[1] if self.turn_angle_range[1] is not None else min_ta
                turn_angle += random.uniform(-min_ta, max_ta)
                turn_angle = max(0.0, turn_angle)
            
            # Начальное направление (случайный угол)
            initial_angle = random.uniform(0, 2 * math.pi)
            
            return {
                "radius": radius,
                "speed": speed,
                "turn_chance": turn_chance,
                "turn_angle": math.radians(turn_angle),  # Переводим в радианы
                "smoothness": smoothness,
                "angle": initial_angle,
                "target_angle": initial_angle,
                "position_x": 0.0,  # Текущее смещение по X
                "position_y": 0.0,  # Текущее смещение по Y
                "target_x": 0.0,    # Целевое смещение по X
                "target_y": 0.0,    # Целевое смещение по Y

                "velocity": [0.0, 0.0],

                "time": 0.0,
            }

        def _get_target_position(self, params):
            # Случайный угол в пределах радиуса
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, params["radius"])
            
            target_x = math.cos(angle) * distance
            target_y = math.sin(angle) * distance
            
            return target_x, target_y

        def _update_angle(self, params, delta):
            if random.random() < params["turn_chance"] * delta * 60:
                angle_change = random.uniform(-params["turn_angle"], params["turn_angle"])
                params["target_angle"] = params["angle"] + angle_change
                
                params["target_angle"] = params["target_angle"] % (2 * math.pi)
            
            angle_diff = params["target_angle"] - params["angle"]
            
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            if params["smoothness"] <= 0:
                params["angle"] = params["target_angle"]
            else:
                lerp_factor = 1.0 - pow(1.0 - params["smoothness"], delta * 60)
                params["angle"] += angle_diff * lerp_factor
            
            params["angle"] = params["angle"] % (2 * math.pi)

        def _update_position(self, params, delta):
            # Двигаемся в текущем направлении
            direction_x = math.cos(params["angle"])
            direction_y = math.sin(params["angle"])

            move_x = direction_x * params["speed"] * delta
            move_y = direction_y * params["speed"] * delta

            params["velocity"][0] = direction_x * params["speed"]
            params["velocity"][1] = direction_y * params["speed"]
            
            params["position_x"] += move_x
            params["position_y"] += move_y
            
            distance = math.hypot(params["position_x"], params["position_y"])
            
            if distance > params["radius"]:
                if distance > 0:
                    params["position_x"] = (params["position_x"] / distance) * params["radius"]
                    params["position_y"] = (params["position_y"] / distance) * params["radius"]

                center_angle = math.atan2(-params["position_y"], -params["position_x"])
                params["target_angle"] = center_angle
                
                if params["smoothness"] <= 0:
                    params["angle"] = center_angle

                params["velocity"][0] = math.cos(params["angle"]) * params["speed"]
                params["velocity"][1] = math.sin(params["angle"]) * params["speed"]

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
            if self._RENP_WANDER not in particle_data:
                particle_data[self._RENP_WANDER] = self._get_wander_params()
            
            wander_data = particle_data[self._RENP_WANDER]
            
            wander_data["time"] += delta
            
            self._update_angle(wander_data, delta)
            self._update_position(wander_data, delta)

            particle.x += wander_data["position_x"] * delta * 10.0
            particle.y += wander_data["position_y"] * delta * 10.0

            if self.screen_bounds:
                particle.x = max(2, min(system.width - 2, particle.x))
                particle.y = max(2, min(system.height - 2, particle.y))

            return UpdateState.Pass