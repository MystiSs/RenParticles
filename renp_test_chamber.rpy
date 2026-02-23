label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles as rparticles_test onlayer master zorder 1:
        sprite expr Solid("#960000", xysize=(12, 12)); test_particle
        lifetime range random (1.5, 3.0)
        redraw asap

        preset spray:
            amount 250
        preset renpy_repulsor
        preset auto_expire

        on particle dead:
            emitter spray:
                amount 1
    
    "Executed"

    $ renpy.pause(hard=True)