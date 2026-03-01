init 100:
    rparticles define "renparticles_test_model":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(6, 12)); expr Solid("#e7a900", xysize=(2, 8))
        lifetime range random (1.0, 2.0)

        preset interval_spray:
            amount "infinite"
            per_amount 2
            interval 0.125
            area (960, 540, 0, 0)

        on update:
            move id "move":
                velocity [0, -200]
                velocity_range [250, 75]
                acceleration [0, 600]

            color_curve:
                colors ["#ffffff", "#ffcc00", "#ff4400", "#33333300"]
                warper "easein_quad"

            face_velocity:
                target_behavior_id "move"
                base_angle 90

            auto_expire

label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    jump renparticles_choice

    "RenParticles"

    rparticles model "renparticles_test_model" as rparticles_test
    
    "Executed"

    rparticles reset "rparticles_test"

    "Reseted"

    hide rparticles_test with dissolve

    "Hided"

    rparticles continue "rparticles_test" zorder 1 onlayer master

    "Continued"

    rparticles clear cache deep

    "Cache cleared deep mode"

    $ renpy.pause(hard=True)