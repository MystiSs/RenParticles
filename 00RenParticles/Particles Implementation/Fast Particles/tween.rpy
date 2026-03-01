# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    from renpy.store import Transform
    from renpy.atl import warpers


    class PropertyTween(_Behavior):
        property = None
        time = 1.0
        start_value = 0.0
        end_value = 1.0
        warper = "linear"
        mode = "absolute"
        from_end = False
        
        # "once" (обычный), "loop" (повтор), "ping-pong" (туда-обратно)
        animation_mode = "once" 

        dynamic = None
        _RENP_TWEEN = "_renp_tween"
        _RENP_TWEEN_COUNTER = 0
        
        def __init__(self):
            self.dynamic = {}
            self._RENP_TWEEN = "{}_{}".format(self._RENP_TWEEN, self._RENP_TWEEN_COUNTER)
            PropertyTween._RENP_TWEEN_COUNTER += 1

        def _get_initial_data(self, particle):
            tween_data = { "_completed": False, "_active": [] }
            p_lifetime = getattr(particle, "lifetime_max", 1.0) 
            targets = self.dynamic if self.dynamic else { self.property: {} }

            for prop_name, prop_config in targets.items():
                t_val = prop_config.get("time", self.time)
                m = prop_config.get("mode", self.mode)
                f_end = prop_config.get("from_end", self.from_end)
                anim_mode = prop_config.get("animation_mode", self.animation_mode)
                
                duration = p_lifetime * t_val if m == "lifetime" else t_val
                delay = max(0.0, p_lifetime - duration) if f_end else 0.0

                start = prop_config.get("start_value", self.start_value)
                end = prop_config.get("end_value", self.end_value)
                warper_name = prop_config.get("warper", self.warper)

                tween_data[prop_name] = {
                    "duration": duration,
                    "delay": delay,
                    "elapsed": 0.0,
                    "start": start,
                    "end": end,
                    "delta": end - start,
                    "warper": warpers[warper_name],
                    "anim_mode": anim_mode
                }
                tween_data["_active"].append(prop_name)

            return tween_data

        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            props = context.system.particles_data.particles_properties

            if particle not in props:
                return UpdateState.Pass
            
            particle_data = props[particle]
            tween_data = particle_data.get(self._RENP_TWEEN)
            
            if tween_data is None:
                tween_data = self._get_initial_data(particle)
                particle_data[self._RENP_TWEEN] = tween_data
            
            if tween_data.get("_completed", False):
                return UpdateState.Pass
            
            transform_kwargs = {}
            new_active = []

            for prop_name in tween_data["_active"]:
                data = tween_data[prop_name]
                data["elapsed"] += delta
                
                if data["elapsed"] < data["delay"]:
                    new_active.append(prop_name)
                    continue

                internal_t = data["elapsed"] - data["delay"]
                duration = data["duration"]
                anim_mode = data["anim_mode"]

                if anim_mode == "once":
                    if internal_t >= duration:
                        value = data["end"]
                    else:
                        new_active.append(prop_name)
                        t = data["warper"](internal_t / duration)
                        value = data["start"] + data["delta"] * t
                
                elif anim_mode == "loop":
                    new_active.append(prop_name)
                    t = (internal_t % duration) / duration
                    t = data["warper"](t)
                    value = data["start"] + data["delta"] * t
                    
                elif anim_mode == "ping-pong":
                    new_active.append(prop_name)
                    loop_count = int(internal_t // duration)
                    t = (internal_t % duration) / duration
                    
                    if loop_count % 2 == 1:
                        t = 1.0 - t
                    
                    t = data["warper"](t)
                    value = data["start"] + data["delta"] * t

                transform_kwargs[prop_name] = value
            
            tween_data["_active"] = new_active
            if not new_active:
                tween_data["_completed"] = True
            
            if transform_kwargs:
                particle.queue_transform(**transform_kwargs)
            
            return UpdateState.Pass