# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init 200:
    screen _renp_rparticles_test_sc(tag):
        rparticles tag

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
                    per_amount 1
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
        accelerate transforming
        #accelerate update
        #acceleration target fps 30
        #update fidelity 2
        #particles listening events

        preset interval_spray:
            amount "infinite"
            per_amount 1
            interval 0.125
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

        preset repulsor

        on update:
            emitter radial_interval_spray:
                amount 25
                interval 0.5
                per_amount 2
                center "mouse"
                radius 100

            oscillate:
                amplitudes [20.0, 20.0]
                amplitudes_range [15.0, 15.0]
                frequencies [0.3, 0.5]
                phases_range [6.28, 6.28]
            
            wander

            attractor:
                target (960.0, 540.0)
                strength 250.0
                radius 0.0
                falloff 0.25
                max_speed 1000.0
                screen_bounds False
            
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
                area (0, -50, config.screen_width - 32, config.screen_height)
    
    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_mouse_trail_demo":
        redraw asap
        sprite expr Solid("#fdfdfdc2", xysize=(8, 8))
        lifetime constant 0.5

        # on particle appear:
        #     sound:
        #         file "RenParticles/00RenParticles/assets/Bubble_Crack.mp3"
        #         channel "audio"

        on update:
            simple_move id "move_handler":
                velocity [0.0, 0.0]
                velocity_range [30.0, 30.0]
            
            tween id "tweener":
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
        sprite expr Solid("#e7a900", xysize=(1, 12)); expr Solid("#e7a900", xysize=(2, 8)); expr Solid("#e7a900", xysize=(1, 7)); expr Solid("#e7a900", xysize=(2, 9))
        lifetime range random (1.0, 2.0)
        accelerate transforming
        # accelerate update
        # update fidelity 4

        preset interval_spray:
            amount "infinite"
            per_amount 2
            interval 0.145
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

    rparticles define "rparticles_mouse_trail_to_center_attractor":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(6, 6)); expr Solid("#ffffff", xysize=(4, 4))
        lifetime range random (1.5, 3.0)

        on event:
            emitter mouse_interval_spray:
                amount "infinite"
                interval 0.075

        on update:
            simple_move id "base_move":
                velocity [0.0, 0.0]
                velocity_range [40.0, 40.0]

            friction:
                target_behavior_id "base_move"
                friction 0.25

            turbulence:
                amount (160, 90)
                frequency 1.5
                smoothness 0.33

            attractor:
                target (960.0, 540.0)
                strength 17500.0
                radius 0.0
                falloff 0.25
                max_speed 1500.0
                screen_bounds False

            zone_enter:
                x 960.0
                y 540.0
                width 15.0
                shape "circle"
                function renparticles.on_enter_zone_debug
                once True

            tween:
                block "alpha":
                    mode "lifetime"
                    from_end True
                    time 0.5
                    start_value 1.0
                    end_value 0.0
                block "zoom":
                    mode "lifetime"
                    time 1.0
                    start_value 1.2
                    end_value 0.2
                    warper "ease"

            auto_expire

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_spring_demo":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(24, 24))

        preset spray:
            amount 10
        
        on update:
            spring:
                target "mouse"
                stiffness 100.0
                max_force 50000.0
                max_speed 5000.0

                stiffness_range 50.0
                rest_length_range 100
                damping_range 0.05

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_wander_demo":
        redraw asap
        sprite expr Solid("#e7a900", xysize=(24, 24))

        preset spray:
            amount 5
        
        on update:
            # face_velocity:
            #     target_behavior_id "wandering"
            #     target_key "velocity"

            wander id "wandering":
                speed_range 15

    # -------------------------------------------------------------------------------------------------------------

    rparticles define "rparticles_wander_and_flock_demo":
        sprite expr Solid("#333333", xysize=(6, 4))
        lifetime range random (8.0, 15.0)
        redraw 0.016
        
        preset interval_spray:
            amount 30
            interval 0.1
            per_amount 2
            area (100, 100, 1720, 580)
        
        on update:
            flock:
                separation_radius 40.0
                alignment_radius 100.0
                cohesion_radius 200.0
                separation_weight 1.5
                alignment_weight 2.0
                cohesion_weight 0.5
                max_speed 300.0
                min_speed 50.0
                margin 100.0
            
            turbulence:
                amount [30, 15]
                frequency 0.5
                smoothness 0.3
            
            face_velocity:
                target_behavior_id "flock_motion"
                target_key "velocity"
                base_angle -90.0
            
            auto_expire

    # -------------------------------------------------------------------------------------------------------------

label renparticles_choice:
    $ renpy.block_rollback()
    scene black
    with dspr
    hide window

    rparticles clear cache deep
    jump renparticles_choice_p1 # На всякий случай

label renparticles_choice_p1:
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
        "[[Page 2]":
            jump renparticles_choice_p2

label renparticles_choice_p2:
    menu:
        "Black Hole on the center!":
            jump renparticles_attractor_zone_demo
        "Springy":
            jump renparticles_spring_demo
        "Oow? it's wandering!":
            jump renparticles_wander_demo
        # "Oow? it's flocking!!":
        #     jump renparticles_wander_and_flock_demo
        "_Screen Test":
            jump renparticles_screen_test_demo
        "[[Page 1]":
            jump renparticles_choice_p1

label renparticles_orbit_mouse_and_rotate:
    rparticles model "rparticles_mouse_orbit_simple" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_mouse_trail_demo:
    rparticles model "rparticles_mouse_trail_demo" as _renp_demo_displ:
        "move_handler":
            velocity_range [30.0, 90.0]
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

    rparticles simulate "_renp_demo_displ" 1.0 # wait 0.0001
    "Simulated +1 seconds"

    rparticles simulate "_renp_demo_displ" 0.34
    "Another +0.34 seconds"

    rparticles simulate "_renp_demo_displ" 0.56
    "Another +0.56 seconds"

    rparticles simulate "_renp_demo_displ" 5.0 wait
    "Another +5 seconds. Wait mode. Wait Mode Step 0.0005s"

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
    rparticles model "renparticles_sparkles_v2_demo" as _renp_demo_displ with Dissolve(0.1)
    "Executed"

    rparticles simulate "_renp_demo_displ" 5.0
    "Simulated +5 seconds"

    hide _renp_demo_displ with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_screen_test_demo:
    show screen _renp_rparticles_test_sc("rparticles_mouse_trail_demo")
    with Dissolve(0.1)
    "Executed"

    hide screen _renp_rparticles_test_sc
    with Dissolve(0.1)
    "Hided"

    jump renparticles_choice

label renparticles_attractor_zone_demo:
    rparticles model "rparticles_mouse_trail_to_center_attractor" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ with Dissolve(0.1)
    "Hided"
    jump renparticles_choice

label renparticles_spring_demo:
    rparticles model "rparticles_spring_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ with Dissolve(0.1)
    "Hided"
    jump renparticles_choice

label renparticles_wander_demo:
    rparticles model "rparticles_wander_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ with Dissolve(0.1)
    "Hided"
    jump renparticles_choice

label renparticles_wander_and_flock_demo:
    rparticles model "rparticles_wander_and_flock_demo" as _renp_demo_displ
    with Dissolve(0.1)
    "Executed"

    hide _renp_demo_displ with Dissolve(0.1)
    "Hided"
    jump renparticles_choice
