init -555 python in renparticles:
    static_shortcuts = {
        "behaviors": {
            "renpy_repulsor_update": RepulsorUpdate,
            "renpy_repulsor_event": RepulsorEvent,

            "auto_expire": LifetimeDeltaDecreaser
        },

        "emitters": {
            "spray": EmitterRandom
        },

        "presets": {
            "general": {
                "spray": SprayPreset,

                "renpy_repulsor": RepulsorPreset,
                "auto_expire": AutoExpirePreset
            }
        }
    }