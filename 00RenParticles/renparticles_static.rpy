init -1337 python in renparticles:
    _fast_particles_cache = { }

    def add_to_cache_fast_particles(particles):
        _fast_particles_cache[particles.image_tag] = particles