# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -555 python in renparticles:
    static_shortcuts = {
        "behaviors": {
            "repulsor_update": RepulsorUpdate,
            "repulsor_event": RepulsorEvent,

            "auto_expire": LifetimeDeltaDecreaser,
            "bounds_killer": BoundsKiller,

            "simple_move": SimpleMove,
            "move": Move,
            "oscillate": OscillateMove,
            "friction": Friction,
            "bounce": Bounce,
            "attractor": Attractor,
            "turbulence": Turbulence,

            "orbit_mouse": OrbitCursorUpdate,
            "orbit_point": OrbitPoint,

            "tween": PropertyTween,
            "color_curve": ColorCurve,

            "rotate": RotateBehavior,
            "face_velocity": FaceVelocity,
            "flicker": FlickerBehavior,

            "interval_fragmentation_per_particle": EmitterIntervalRemoteSpawn
        },

        "emitters": {
            "spray": EmitterRandom,
            "interval_spray": IntervalSprayEmitter,
            "mouse_interval_spray": MouseIntervalSpawner,
            "fragmentation": EmitterRemoteSpawn,
            "interval_fragmentation": EmitterIntervalRemoteSpawn
        },

        "presets": {
            "general": {
                "spray": SprayPreset,
                "interval_spray": IntervalSprayPreset,

                "repulsor": RepulsorPreset,

                "auto_expire": AutoExpirePreset,
                "bounds_killer": BoundsKillerPreset,

                "orbit_mouse": OrbitMousePreset
            },

            "inner": {

            }
        }
    }

    dynamic_shortcuts = {
        "behaviors": {

        },

        "emitters": {

        },

        "presets": {
            "general": {

            },

            "inner": {
                
            }
        }
    }