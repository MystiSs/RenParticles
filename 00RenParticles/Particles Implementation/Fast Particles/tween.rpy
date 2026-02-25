init -1115 python in renparticles:
    from renpy.store import Transform
    from renpy.atl import warpers


    class PropertyTween(_Behavior):
        time = _RequiredField()
        property = _RequiredField()
        warper = "linear"

        start_value = 0.0
        end_value = 1.0

        _RENP_TWEEN = "_renp_tween"
        _RENP_TWEEN_COUNTER = 0
        
        def __init__(self):
            self._RENP_TWEEN = "{}_{}".format(self._RENP_TWEEN, self._RENP_TWEEN_COUNTER)
            self._RENP_TWEEN_COUNTER += 1

        def _get_initial_data(self, particle):
            return { "progress": 0.0, "finished": False, "base_image": particle.cache.child }

        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            particles_props = context.system.particles_data.particles_properties
            
            particle_data = particles_props.setdefault(particle, {})

            if not self._RENP_TWEEN in particle_data:
                particle_data[self._RENP_TWEEN] = self._get_initial_data(particle)

            if particle_data[self._RENP_TWEEN]["finished"]:
                return UpdateState.Pass

            particle_data[self._RENP_TWEEN]["progress"] += delta
            progress = particle_data[self._RENP_TWEEN]["progress"]

            current_value = _renp_lerp(self.start_value, self.end_value, warpers[self.warper](progress / self.time))
            value = _renp_clamp(current_value, self.start_value, self.end_value)
            particle.set_child(Transform(particle_data[self._RENP_TWEEN]["base_image"], **{self.property: value}))

            particle_data[self._RENP_TWEEN]["finished"] = progress >= self.time

            return UpdateState.Pass    