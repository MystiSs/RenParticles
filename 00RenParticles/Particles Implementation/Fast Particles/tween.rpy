init -1115 python in renparticles:
    from renpy.store import Transform
    from renpy.atl import warpers


    class PropertyTween(_Behavior):
        # time = _RequiredField()
        # property = _RequiredField()
        # warper = "linear"

        property = None
        time = 1.0
        start_value = 0.0
        end_value = 1.0
        warper = "linear"

        dynamic = None

        # property ->
        # time
        # start_value
        # end_value
        # warper

        _RENP_TWEEN = "_renp_tween"
        _RENP_TWEEN_COUNTER = 0
        
        def __init__(self):
            self.dynamic = {}
            self._RENP_TWEEN = "{}_{}".format(self._RENP_TWEEN, self._RENP_TWEEN_COUNTER)
            self._RENP_TWEEN_COUNTER += 1

        def _get_initial_data(self, particle):
            tween_data = { "_finished": False, "_active": None }

            if self.dynamic:
                for prop_name, prop_data in self.dynamic.items():
                    time = prop_data.get("time", self.time)
                    start = prop_data.get("start_value", self.start_value)
                    end = prop_data.get("end_value", self.end_value)
                    warper_name = prop_data.get("warper", self.warper)

                    tween_data[prop_name] = {
                        "time": time,
                        "progress": 0.0,
                        "start": start,
                        "delta": end - start,
                        "warper": warpers[warper_name],
                        "finished": False,
                        "end": end,
                    }
                tween_data["_active"] = self.dynamic.keys() 

            else:
                time = self.time
                start = self.start_value
                end = self.end_value
                warper_func = warpers[self.warper]

                tween_data[self.property] = {
                    "time": time,
                    "progress": 0.0,
                    "start": start,
                    "delta": end - start,
                    "warper": warper_func,
                    "finished": False,
                    "end": end,
                }

                tween_data["_active"] = [self.property]

            return tween_data

        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties
            
            particle_data = particles_props.setdefault(particle, {})
            
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
                
                data["progress"] += delta
                
                if data["progress"] >= data["time"]:
                    transform_kwargs[prop_name] = data["end"]
                else:
                    new_active.append(prop_name)
                    t = data["progress"] / data["time"]
                    t = data["warper"](t)
                    value = data["start"] + data["delta"] * t
                    transform_kwargs[prop_name] = _renp_clamp(value, data["start"], data["end"])
            
            tween_data["_active"] = new_active
            
            if not new_active:
                tween_data["_completed"] = True
            
            if transform_kwargs:
                particle.queue_transform(**transform_kwargs)
            
            return UpdateState.Pass    