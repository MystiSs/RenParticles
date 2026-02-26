label renp_test_chamber:
    $ st_chmbr_test = False

    #show screen shcs_overlay_hided
    scene black
    with dspr

    "RenParticles"

    rparticles multiple as rparticles_test onlayer master zorder 1:
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
                    interval 0.1
        
        system id "rain":
            sprite expr Solid("#0064e7ab", xysize=(24, 24)); expr Solid("#001694ad", xysize=(24, 24))
            lifetime constant 1.0
            
            preset auto_expire

            on update:
                tween:
                    block "alpha":
                        time 0.5
                    block "zoom":
                        time 1.0
                        start_value 1.0
                        end_value 0.0
                        warper "ease"
                
                move:
                    velocity [0.0, 0.0]
                    velocity_range [100.0, 5.0]
                    acceleration [0.0, 0.0]
                    acceleration_range [50.0, 50.0]
    
    "Executed"

    rparticles reset rparticles_test

    "Reseted"

    hide rparticles_test with dissolve

    "Hided"

    $ renpy.pause(hard=True)