label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles as rparticles_test onlayer master zorder 1:
        sprite expr Solid("#960000", xysize=(12, 12)); test_particle
        lifetime range random (1.5, 1.75)
        redraw asap

        preset interval_spray:
            interval 0.01
            amount 100

        preset orbit_mouse:
            screen_bounds True
            pull_strength 0.1
            speed 20.0

        preset auto_expire

        on particle dead:
            emitter spray:
                amount 1
    
    "Executed"

    hide rparticles_test with dissolve

    "Hided"

    $ renpy.pause(hard=True)