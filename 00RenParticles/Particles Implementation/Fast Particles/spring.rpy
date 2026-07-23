# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import math
    import random

    class Spring(_UpdateBehavior):
        """Пружинистое притяжение к точке с инерцией и затуханием"""
        
        # --- Обязательные параметры ---
        target = _RequiredField()  # "mouse" или (x, y)
        
        stiffness = 500.0          # Жёсткость пружины
        damping = 0.9              # Затухание (0.0 - 1.0, 1.0 = нет затухания)
        rest_length = 0.0          # Длина покоя
        
        max_force = 50000.0        # Максимальная сила
        max_speed = 2500.0         # Максимальная скорость
        screen_bounds = True       # Удерживать в пределах экрана
        
        stiffness_range = None     # [min, max] или число
        damping_range = None       # [min, max] или число
        rest_length_range = None   # [min, max] или число

        _ranges_normalized = False

        _check_is_valid = True
        _valid = {
            "target", "stiffness", "damping", "rest_length",
            "max_force", "max_speed", "screen_bounds",
            "stiffness_range", "damping_range", "rest_length_range"
        }

        _RENP_SPRING = "_renp_spring_data"
        _COUNTER = 0

        def __init__(self):
            self._RENP_SPRING = "{}_{}".format(self._RENP_SPRING, self._COUNTER)
            Spring._COUNTER += 1

        def _normalize_ranges(self):
            if self.stiffness_range is None:
                self.stiffness_range = [None, None]
            elif isinstance(self.stiffness_range, (int, float)):
                self.stiffness_range = [self.stiffness_range, self.stiffness_range]
            elif len(self.stiffness_range) == 1:
                self.stiffness_range = [self.stiffness_range[0], self.stiffness_range[0]]
            
            if self.damping_range is None:
                self.damping_range = [None, None]
            elif isinstance(self.damping_range, (int, float)):
                self.damping_range = [self.damping_range, self.damping_range]
            elif len(self.damping_range) == 1:
                self.damping_range = [self.damping_range[0], self.damping_range[0]]
            
            if self.rest_length_range is None:
                self.rest_length_range = [None, None]
            elif isinstance(self.rest_length_range, (int, float)):
                self.rest_length_range = [self.rest_length_range, self.rest_length_range]
            elif len(self.rest_length_range) == 1:
                self.rest_length_range = [self.rest_length_range[0], self.rest_length_range[0]]

            self._ranges_normalized = True

        def _get_spring_params(self):            
            stiffness = self.stiffness
            if self.stiffness_range[0] is not None:
                min_s = self.stiffness_range[0]
                max_s = self.stiffness_range[1] if self.stiffness_range[1] is not None else min_s
                stiffness += random.uniform(-min_s, max_s)
                stiffness = max(0.1, stiffness)
            
            damping = self.damping
            if self.damping_range[0] is not None:
                min_d = self.damping_range[0]
                max_d = self.damping_range[1] if self.damping_range[1] is not None else min_d
                damping += random.uniform(-min_d, max_d)
                damping = max(0.0, min(1.0, damping))
            
            rest_length = self.rest_length
            if self.rest_length_range[0] is not None:
                min_r = self.rest_length_range[0]
                max_r = self.rest_length_range[1] if self.rest_length_range[1] is not None else min_r
                rest_length += random.uniform(-min_r, max_r)
                rest_length = max(0.0, rest_length)
            
            return {
                "stiffness": stiffness,
                "damping": damping,
                "rest_length": rest_length,
                "velocity": [0.0, 0.0]
            }

        def _get_target_position(self):
            if self.target == "mouse":
                pos = renpy.get_mouse_pos()
                return pos
            else:
                return self.target

        def _calculate_spring_force(self, dx, dy, distance, params):
            if distance < 0.001:
                return 0.0, 0.0
            
            nx = dx / distance
            ny = dy / distance
            
            #Здесь k положительный. Направление берётся от напрявляющего вектора, т.е. от nx и ny#
            displacement = distance - params["rest_length"]
            force_magnitude = params["stiffness"] * displacement
            
            force_magnitude = max(-self.max_force, min(self.max_force, force_magnitude))
            
            return nx * force_magnitude, ny * force_magnitude

        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            system = context.system
            props = system.particles_data.particles_properties

            if particle not in props:
                return UpdateState.Pass

            if not self._ranges_normalized:
                self._normalize_ranges()

            target_pos = self._get_target_position()
            if target_pos is None:
                return UpdateState.Pass
            
            tx, ty = target_pos

            particle_data = props[particle]
            if self._RENP_SPRING not in particle_data:
                particle_data[self._RENP_SPRING] = self._get_spring_params()
            
            spring_data = particle_data[self._RENP_SPRING]

            dx = tx - particle.x
            dy = ty - particle.y
            distance = math.hypot(dx, dy)
            
            fx, fy = self._calculate_spring_force(dx, dy, distance, spring_data)

            spring_data["velocity"][0] = (
                spring_data["velocity"][0] * spring_data["damping"] + fx * delta
            )
            spring_data["velocity"][1] = (
                spring_data["velocity"][1] * spring_data["damping"] + fy * delta
            )

            speed = math.hypot(spring_data["velocity"][0], spring_data["velocity"][1])
            if speed > self.max_speed:
                ratio = self.max_speed / speed
                spring_data["velocity"][0] *= ratio
                spring_data["velocity"][1] *= ratio

            particle.x += spring_data["velocity"][0] * delta
            particle.y += spring_data["velocity"][1] * delta

            if self.screen_bounds:
                particle.x = max(2, min(system.width - 2, particle.x))
                particle.y = max(2, min(system.height - 2, particle.y))

            return UpdateState.Pass