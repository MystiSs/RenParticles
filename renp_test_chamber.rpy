init 100:
    rparticles define preset dynamic_preset_test type general:
        on update:
            tween:
                block "alpha":
                    time 0.5
                block "zoom":
                    time 1.0
                    start_value 1.0
                    end_value 0.0
                    warper "ease"
            
            tween:
                block "alpha":
                    mode "lifetime"
                    from_end True
                    time 0.5
                    start_value 1.0
                    end_value 0.0
            
            rotate:
                speed 0.0
                speed_range 360.0
                phase_range 360.0
            
            move:
                velocity [0.0, 0.0]
                velocity_range [100.0, 5.0]
                acceleration [0.0, 0.0]
                acceleration_range [50.0, 50.0]

    rparticles define multiple "renparticles_test_model":
        redraw asap

        system id "orbit":
            sprite expr Solid("#e7a900", xysize=(24, 24)); expr Solid("#160094", xysize=(24, 24))

            preset spray:
                amount 3
            preset orbit_mouse:
                speed 10.0

            on update:
                interval_fragmentation_per_particle system "rain":
                    amount 1
                    interval 0.2
        
        system id "rain":
            sprite expr Solid("#0064e7ab", xysize=(24, 24)); expr Solid("#001694ad", xysize=(24, 24))
            lifetime constant 1.0
            
            preset auto_expire

            preset dynamic_preset_test

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_mouse_orbit_simple":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(24, 24))

        preset spray:
            amount 10

        preset orbit_mouse:
            speed 5.0
            speed_variance 0.5
        
        on update:
            rotate:
                speed 60.0
                phase_range 360.0

label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

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