label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles as rparticles_test onlayer master zorder 1:
        sprite expr Solid("#960000", xysize=(12, 12)); test_particle
        lifetime range random (0.5, 0.75)
        redraw asap

        preset interval_spray:
            interval 0.01
            amount 100

        on update:
            orbit_mouse:
                screen_bounds True
                pull_strength 0.25

            auto_expire

        on particle dead:
            emitter spray:
                amount 1
    
    "Executed"

    $ renpy.pause(hard=True)