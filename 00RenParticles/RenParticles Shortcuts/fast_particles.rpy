init -555 python in renparticles:
    static_shortcuts = {
        "behaviors": {
            "renpy_repulsor_update": RepulsorUpdate,
            "renpy_repulsor_event": RepulsorEvent,

            "auto_expire": LifetimeDeltaDecreaser,

            "simple_move": SimpleMove,
            "move": Move,

            "orbit_mouse": OrbitCursorUpdate
        },

        "emitters": {
            "spray": EmitterRandom,
            "interval_spray": IntervalSprayEmitter
        },

        "presets": {
            "general": {
                "spray": SprayPreset,
                "interval_spray": IntervalSprayPreset,

                "renpy_repulsor": RepulsorPreset,
                "auto_expire": AutoExpirePreset
            },

            "inner": {
                
            }
        }
    }