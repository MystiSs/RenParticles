label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles as rparticles_test onlayer master zorder 1:
        redraw asap
        sprite expr Solid("#e78300", xysize=(24, 24)); expr Solid("#160094", xysize=(24, 24))
        lifetime range random (1.5, 3.0)

        preset interval_spray:
            interval 0.005
            amount 50

        preset repulsor:
            strength 32.0

        preset auto_expire

        on update:
            tween:
                block "alpha":
                    time 0.5
                block "zoom":
                    time 0.5
                    start_value 2.0
                    end_value 1.0

        on particle dead:
            emitter spray:
                amount 1
    
    "Executed"

    hide rparticles_test with dissolve

    "Hided"

    $ renpy.pause(hard=True)