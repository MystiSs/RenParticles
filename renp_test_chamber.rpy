init 100:
    rparticles define "renparticles_test_model":
        redraw asap
        sprite expr Solid("#fdfdfdc2", xysize=(8, 8))
        lifetime constant 2.0

        on update:
            simple_move:
                velocity [0.0, 0.0]
                velocity_range [30.0, 30.0]

            attractor:
                target (960, 540)
                falloff 0.25
                strength 10000
            
            tween:
                block "alpha":
                    mode "lifetime"
                    from_end True
                    time 0.5
                    start_value 1.0
                    end_value 0.0
                block "zoom":
                    mode "lifetime"
                    time 0.5
                    start_value 1.5
                    end_value 0.5
                    warper "ease"
            
            rotate:
                speed 180.0
                phase_range 360.0
            
            auto_expire

        on event:
            emitter mouse_interval_spray:
                amount "infinite"
                interval 0.075

label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    #jump renparticles_choice

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