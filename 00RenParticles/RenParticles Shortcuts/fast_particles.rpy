init -555 python in renparticles:
    static_shortcuts = {
        "behaviors": {
            "repulsor_update": RepulsorUpdate,
            "repulsor_event": RepulsorEvent,

            "auto_expire": LifetimeDeltaDecreaser,

            "simple_move": SimpleMove,
            "move": Move,
            "oscillate": OscillateMove,

            "orbit_mouse": OrbitCursorUpdate,

            "tween": PropertyTween,

            "interval_fragmentation_per_particle": EmitterIntervalRemoteSpawn
        },

        "emitters": {
            "spray": EmitterRandom,
            "interval_spray": IntervalSprayEmitter,
            "fragmentation": EmitterRemoteSpawn,
            "interval_fragmentation": EmitterIntervalRemoteSpawn
        },

        "presets": {
            "general": {
                "spray": SprayPreset,
                "interval_spray": IntervalSprayPreset,

                "repulsor": RepulsorPreset,
                "auto_expire": AutoExpirePreset,

                "orbit_mouse": OrbitMousePreset
            },

            "inner": {
                
            }
        }
    }