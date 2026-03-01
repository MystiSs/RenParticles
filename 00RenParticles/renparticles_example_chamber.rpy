# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init 100:
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
    
    # -------------------------------------------------------------------------------------------------------------

    rparticles define preset orbit_mouse_rain_behavior type general:
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

    rparticles define multiple "rparticles_mouse_orbit_multiple":
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
            preset orbit_mouse_rain_behavior

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_squares_from_center":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(24, 24))
        lifetime constant 2.5

        preset interval_spray:
            amount "infinite"
            per_amount 2
            interval 0.25
            area (960, 540, 0, 0)

        on update:
            simple_move:
                velocity [0, 0]
                velocity_range [540, 540]

            oscillate:
                amplitudes [0, 0]
                amplitudes_range [100, 100]

            rotate:
                speed 0
                speed_range 120
                phase_range 360
            
            tween:
                block "alpha":
                    time 0.2
                    mode "lifetime"
                    from_end True
                    start_value 1.0
                    end_value 0.0
            
            auto_expire
            bounds_killer

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_wiggle_wiggle_little_squares":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(24, 24))

        preset spray:
            amount 75

        on update:
            oscillate:
                amplitudes [0, 0]
                frequencies [4.0, 1.5]
                amplitudes_range [100, 100]

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_snowfall_demo":
        redraw asap
        sprite expr Solid("#ffffff", xysize=(8, 8))

        preset interval_spray:
            amount "infinite"
            per_amount 1
            interval 0.1
            area (0, -50, config.screen_width - 32, 0)

        on update:
            simple_move:
                velocity [20.0, 200.0]
                velocity_range [50.0, 40.0]
            
            rotate:
                speed 45.0
                speed_range 90.0
            
            oscillate:
                amplitudes [30.0, 0.0]
                frequencies [0.5, 0.0]
            
            bounds_killer:
                margin 60

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_fireflies_demo":
        redraw asap
        sprite expr Solid("#ffff99", xysize=(5, 5))
        lifetime range random (3.0, 6.0)

        preset interval_spray:
            amount 25
            interval 0.5
            per_amount 2
            area (200, 200, config.screen_width-200, config.screen_height-200)

        on update:
            oscillate:
                amplitudes [20.0, 20.0]
                amplitudes_range [15.0, 15.0]
                frequencies [0.3, 0.5]
                phases_range [6.28, 6.28]
            
            tween:
                block "alpha":
                    mode "lifetime"
                    time 0.8
                    start_value 0.0
                    end_value 1.0
            
            tween:
                block "alpha":
                    mode "lifetime"
                    time 0.3
                    from_end True
                    start_value 1.0
                    end_value 0.0

            flicker:
                property "alpha"
                mode "sub"
                range [0.15, 0.3]
                interval 0.1
            
            auto_expire
        
        on particle dead:
            emitter spray:
                amount 1
                area (200, 200, config.screen_width-200, config.screen_height-200)
    
    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_mouse_trail_demo":
        redraw asap
        sprite expr Solid("#fdfdfdc2", xysize=(8, 8))
        lifetime constant 0.5

        on update:
            simple_move:
                velocity [0.0, 0.0]
                velocity_range [30.0, 30.0]
            
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
                interval 0.05

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "renparticles_sparkles_v2_demo":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(4, 12)); expr Solid("#e7a900", xysize=(2, 8)); expr Solid("#e7a900", xysize=(1, 7))
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

    # -------------------------------------------------------------------------------------------------------------


label renparticles_choice:
    $ renpy.block_rollback()
    scene black
    with dspr
    hide window

    rparticles clear cache deep

    menu:
        "Orbit Mouse And Rotate":
            jump renparticles_orbit_mouse_and_rotate
        "Orbit Mouse And Rotate v2.0":
            jump renparticles_orbit_mouse_and_rotate_multiple
        "Mouse Trail":
            jump renparticles_mouse_trail_demo
        "Squares From Center":
            jump renparticles_squares_from_center
        "Wiggle-Wiggle Little Squares":
            jump renparticles_wiggle_wiggle_little_squares
        "Look! {i}Snowfall!{/i}":
            jump renparticles_snowfall_demo
        "Fireflies! {alpha=0.5}(Just Squares -_-)":
            jump renparticles_fireflies_demo
        "Sparkles v2.0":
            jump renparticles_sparkles_v2_demo

label renparticles_orbit_mouse_and_rotate:
    rparticles model "rparticles_mouse_orbit_simple" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_mouse_trail_demo:
    rparticles model "rparticles_mouse_trail_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_orbit_mouse_and_rotate_multiple:
    rparticles model "rparticles_mouse_orbit_multiple" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_squares_from_center:
    rparticles model "rparticles_squares_from_center" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_wiggle_wiggle_little_squares:
    rparticles model "rparticles_wiggle_wiggle_little_squares" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_snowfall_demo:
    rparticles model "rparticles_snowfall_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_fireflies_demo:
    rparticles model "rparticles_fireflies_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_sparkles_v2_demo:
    rparticles model "renparticles_sparkles_v2_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice
