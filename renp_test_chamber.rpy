label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles multiple as rparticles_test onlayer master zorder 1:
        redraw asap
        system:
            sprite expr Solid("#960000", xysize=(12, 12)); test_particle
            lifetime range random (0.5, 0.75)

            preset interval_spray:
                interval 0.01
                amount 25

            on update:
                orbit_mouse:
                    screen_bounds True
                    pull_strength 0.1

                auto_expire

            on particle dead:
                emitter spray:
                    amount 1
        
        system:
            sprite expr Solid("#e78300", xysize=(12, 12)); expr Solid("#160094", xysize=(12, 12))
            lifetime range random (1.5, 3.0)
            preset interval_spray:
                interval 0.02
                amount 100
            preset renpy_repulsor
            preset auto_expire

            on update:
                move:
                    velocity [0.0, 0.0]
                    velocity_range [200.0, 100.0]

                    acceleration [150.0, 400.0]

            on particle dead:
                emitter spray:
                    amount 1
    
    "Executed"

    hide rparticles_test with dissolve

    "Hided"

    $ renpy.pause(hard=True)