label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles as rparticles_test onlayer master zorder 1:
        sprite expr Solid("#960000", xysize=(12, 12)); test_particle
        lifetime range random (1.5, 3.0)
        redraw 0.0
        on update:
            emitter spray oneshot:
                amount 250
                area (0, 0, config.screen_width, config.screen_height)
            renpy_repulsor_update
            auto_expire
        on event:
            renpy_repulsor_event
        on particle dead:
            emitter spray:
                amount 1
                area (0, 0, config.screen_width, config.screen_height)
    
    "Executed"

    $ renpy.pause(hard=True)