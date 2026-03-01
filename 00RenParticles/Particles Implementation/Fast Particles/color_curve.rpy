# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    from renpy.store import Color, TintMatrix

    class ColorCurve(_UpdateBehavior):
        colors = ["#ffffff"] 
        warper = "linear"
        
        _RENP_CURVE_DATA = "_color_curve_state"
        _COUNTER = 0

        def __init__(self):
            self._RENP_CURVE_DATA = "{}_{}".format(self._RENP_CURVE_DATA, self._COUNTER)
            ColorCurve._COUNTER += 1

        def __call__(self, context):
            particle = context.particle
            system = context.system
            props = context.system.particles_data.particles_properties

            if particle not in props:
                return UpdateState.Pass
            
            if props.get(self._RENP_CURVE_DATA) == "_completed":
                return UpdateState.Pass

            if not hasattr(particle, "lifetime") or not hasattr(particle, "lifetime_max"):
                return UpdateState.Pass

            t = 1.0 - (particle.lifetime / particle.lifetime_max)
            
            if t >= 1.0:
                target_color = Color(self.colors[-1])
                particle.queue_transform(matrixcolor=TintMatrix(target_color))
                props[self._RENP_CURVE_DATA] = "_completed"
                return UpdateState.Pass

            t = warpers[self.warper](_renp_clamp(t, 0.0, 1.0))
            
            num_colors = len(self.colors)
            if num_colors < 2:
                target_color = Color(self.colors[0])
                props[self._RENP_CURVE_DATA] = "_completed"
            else:
                scaled_t = t * (num_colors - 1)
                idx = int(scaled_t)
                idx = min(idx, num_colors - 2)
                inner_t = scaled_t - idx
                
                c1 = Color(self.colors[idx])
                c2 = Color(self.colors[idx + 1])
                target_color = c1.interpolate(c2, inner_t)

            particle.queue_transform(matrixcolor=TintMatrix(target_color))
            
            return UpdateState.Pass