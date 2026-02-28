init -1115 python in renparticles:
    class BoundsKiller(_UpdateBehavior):       
        margin = 32
        only_if_completely = False
        safe_zone = 0.0
        
        def __init__(self):
            super(BoundsKiller, self).__init__()
        
        def _get_margins(self, system):
            if isinstance(self.margin, (int, float)):
                return (self.margin, self.margin, self.margin, self.margin)
            
            elif isinstance(self.margin, (list, tuple)):
                if len(self.margin) == 2:
                    h, v = self.margin
                    return (h, v, h, v)
                elif len(self.margin) == 4:
                    return tuple(self.margin)
            
            return (0, 0, 0, 0)
        
        def _is_out_of_bounds(self, particle, system, margins):
            left = -margins[0]
            top = -margins[1]
            right = system.width + margins[2]
            bottom = system.height + margins[3]
            
            if self.only_if_completely:
                if hasattr(particle, "cache") and particle.cache and particle.cache.render:
                    w, h = particle.cache.render.get_size()
                else:
                    w, h = 0, 0
                
                completely_out = (
                    particle.x + w/2 < left or
                    particle.x - w/2 > right or
                    particle.y + h/2 < top or
                    particle.y - h/2 > bottom
                )
                return completely_out
            else:
                return (
                    particle.x < left or
                    particle.x > right or
                    particle.y < top or
                    particle.y > bottom
                )
        
        def _is_in_safe_zone(self, particle, system):
            if self.safe_zone <= 0:
                return False
            
            return (
                particle.x >= self.safe_zone and
                particle.x <= system.width - self.safe_zone and
                particle.y >= self.safe_zone and
                particle.y <= system.height - self.safe_zone
            )
        
        def __call__(self, context):
            particle = context.particle
            system = context.system
            
            if self._is_in_safe_zone(particle, system):
                return UpdateState.Pass
            
            margins = self._get_margins(system)
            
            if self._is_out_of_bounds(particle, system, margins):
                particle.destroy()
            
            return UpdateState.Pass

    class BoundsKillerPreset(_RFBehaviorPreset):     
        behaviors = {
            "on_update": [BoundsKiller],
            "on_event": None,
            "on_particle_dead": None
        }

        m_oneshot = False
        
        margin = 32
        only_if_completely = False
        safe_zone = 0.0
        
        def distribute_properties(self):
            super(BoundsKillerPreset, self).distribute_properties()
            
            killer = self.behaviors["on_update"][0]
            
            killer.inject_properties(
                margin=self.margin,
                only_if_completely=self.only_if_completely,
                safe_zone=self.safe_zone,
                oneshot=self.m_oneshot
            )