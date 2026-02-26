init -1337 python in renparticles:
    from builtins import min, max


    _fast_particles_entries = { }

    def add_to_cache_fast_particles(particles):
        _fast_particles_cache[particles.image_tag] = particles

    def _renp_lerp(start, end, t):
        return start + (end - start) * t

    def _renp_clamp(value, min_value, max_value):
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        
        return max(min_value, min(max_value, value))