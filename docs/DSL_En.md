# RenParticles DSL - User Guide

# Table of Contents

* [Introduction](#introduction)
* [Quick Start](#quick-start)
* [Basic Syntax](#basic-syntax)
    * [Declaring a Particle System](#declaring-a-particle-system)
    * [Particle Sprites](#particle-sprites)
    * [Particle Lifetime](#particle-lifetime)
    * [Update Frequency](#update-frequency)
* [Behavior Blocks](#behavior-blocks)
    * [on update](#on-update)
    * [on event](#on-event)
    * [on particle dead](#on-particle-dead)
* [Emitters](#emitters)
    * [Emitter: spray](#handler-spray)
    * [Emitter: interval_spray](#handler-interval_spray)
    * [Emitter: interval_spray](#emitter-mouse_interval)
* [Handler-Emitter: fragmentation (interval_fragmentation_per_particle)](#handler-fragmentation-interval_fragmentation_per_particle)
* [Particle Behaviors](#particle-behaviors)
    * [What Are They?](#what-are-they)
    * [Behavior Identifiers (id)](#behavior-identifiers-id)
---
* [Handler: auto_expire](#handler-auto_expire-or-preset-auto_expire)
* [Handler: bounds_killer](#handler-bounds_killer-or-preset-bounds_killer)
* [Handler: move](#handler-move)
* [Handler: simple_move](#handler-simple_move)
* [Handler: friction](#handler-friction)
* [Handler: bounce](#handler-bounce)
* [Handler: rotate](#handler-rotate)
* [Handler: flicker](#handler-flicker)
* [Handler: oscillate](#handler-oscillate)
* [Handler: orbit_mouse](#handler-orbit_mouse-or-preset-orbit_mouse)
* [Handler: orbit_point](#handler-orbit_point)
* [Handler: attractor](#handler-attractor)
* [Handler: repulsor](#handler-repulsor)
* [Handler: tween](#handler-tween)
---
* [Presets](#presets)
    * [Built-in Presets](#built-in-presets)
    * [Creating Custom Presets](#creating-custom-presets)
* [Multiple Systems](#multiple-systems)
* [Models (Templates)](#models-templates)
* [System Management](#system-management)
    * [Control Commands](#control-commands)
* [Advanced Features](#advanced-features)
    * [Custom Functions](#custom-functions)
    * [oneshot Modifier](#oneshot-modifier)
    * [Dynamic Properties](#dynamic-properties)
* [Examples](#examples)
    * [Simple Rain](#simple-rain)
    * [Firework (Example of a Complex Chain)](#firework-example-of-a-complex-chain)
    * [Magical Effect](#magical-effect)
* [Performance Tips](#performance-tips)
* [Debugging](#debugging)
* [Limitations](#limitations)

## Introduction

RenParticles is a particle system for Ren'Py with its own DSL (Domain-Specific Language). Instead of writing Python code, you describe particle behavior declaratively using a simple syntax.

---

## Quick Start

```renpy
rparticles as my_particles onlayer master zorder 1:
    sprite expr Solid("#ff0000", xysize=(12, 12))
    lifetime range random (1.0, 3.0)
    redraw asap

    preset spray:
        amount 100

    preset auto_expire
```

This code will create 100 red square particles with a random lifetime between 1 and 3 seconds.

---

## Basic Syntax

### Declaring a Particle System

```renpy
rparticles [model "model_name"] [as tag] [onlayer layer_name] [zorder z] [multiple]:
    # system contents
```

**Parameters:**
- `model "name"` — use a predefined model
- `as tag` — tag for system control (default `rparticles_displayable`)
- `onlayer layer_name` — display layer (default `master`)
- `zorder z` — drawing order (default `0`)
- `multiple` — create a group of several subsystems

### Particle Sprites

Define the appearance of particles:

```renpy
sprite image_tag
sprite expr Solid("#ff0000", xysize=(12, 12))
sprite image1; image2; expr Solid("#00ff00", xysize=(8, 8))
```

- Regular image tag: `sprite my_particle_image`
- Python expression: `sprite expr <expression>`
- Multiple variants separated by `;` — the system will choose randomly

### Particle Lifetime

```renpy
lifetime constant 2.0
lifetime range random (1.0, 3.0)
```

- `constant <number>` — fixed lifetime
- `range random (<min>, <max>)` — random time within a range

### Update Frequency

```renpy
redraw 0.0          # maximum frequency
redraw asap         # same as above (as soon as possible)
redraw 0.016        # ~60 FPS
redraw None         # default update
```

A smaller value means smoother animation but higher load.

---

## Behavior Blocks

### on update

Executed every clock cycle for each particle (the "clock cycle" refers to the renpy.redraw call, the speed of which you specify yourself):

```renpy
on update:
    move:
        velocity [0.0, 100.0]
        acceleration [0.0, 50.0]

    auto_expire
```

### on event

Reacts to mouse events:

```renpy
on event:
    repulsor_event
```

### on particle dead

Executed when a particle dies:

```renpy
on particle dead:
    emitter spray:
        amount 3
```

## Emitters

Emitters create new particles.

### Emitter: `spray`

Creates particles all at once:

```renpy
emitter spray oneshot:
    amount 100
    area (0, 0, 1920, 1080)
```

**Parameters:**
- `amount` — number of particles (required)
- `area` — generation area `(x1, y1, width, height)` (defaults to the entire screen)

### Emitter: `interval_spray`

Creates particles at intervals:

```renpy
emitter interval_spray:
    amount 500
    interval 0.05
    per_amount 10
```

**Parameters:**
- `amount` — total number of particles
* * The parameter can be set as `"infinite"'. Then the particles will be emitted indefinitely.
- `interval` — interval between generations (seconds)
- `per_amount` — particles per batch (default 1)
- `kill_on_finish` — delete the emitter after completion (default True)

---

### Emitter: `mouse_interval`

Spawns particles at the current mouse cursor position at regular time intervals.

**Usage Example:**

```renpy
rparticles as cursor_trail:
    emitter mouse_interval:
        interval 0.05    # Spawns every 50ms
        per_amount 2     # 2 particles at once
        offset (5, 5)    # Slight offset from the cursor tip

```

**Parameters:**

* **`amount`** (int or "infinite") — Total number of particles this emitter can spawn. Default is `"infinite"`.
* **`interval`** (float) — Time in seconds between spawns. Default is `0.1`.
* **`per_amount`** (int) — Number of particles spawned per interval tick. Default is `1`.
* **`offset`** (tuple) — Spawn point offset relative to the cursor `(x, y)`. Default is `(0, 0)`.
* **`kill_on_finish`** (bool) — If `True`, the emitter will be removed from the system after reaching the `amount` limit. Default is `False`.

---

## Handler-Emitter: `fragmentation (interval_fragmentation_per_particle)`

This handler allows one system (the donor) to create particles in another system (the receiver). It is used for creating trails, cascading explosions, or complex weather effects.

### Syntax:

```renpy
# Inside a behavior block (on update)
interval_fragmentation_per_particle system "target_system_id":
    amount 1      # Number of particles created per tick
    interval 0.1  # Generation frequency (in seconds)

```

### Parameters:

* **`system "id"`** (string): The unique identifier of the target system where new particles will be born. Optional parameter.
>If you set an invalid `id`, the system will create particles in the current system.
* **`amount`** (integer): How many particles are created at once when the interval triggers.
* **`interval`** (float): The delay between generation cycles.
* **`fallback_position`** (2 numbers): The particle creation position, if the emitter is specified using the keyword `emitter`.

### Operational Nuances and Architecture

#### 1. Context Dependency (`_has_particle`)

The handler automatically determines its role on the first run:

* **If called inside a particle's `on update` without the `emitter` keyword**: It becomes "local". Each parent particle gets its own timer. This allows for creating unique trails that follow each particle individually.
* **If called with the `emitter` keyword**: It works as a regular interval emitter, creating particles at the coordinates $(0, 0)$ of the target system.

#### 2. Trail Mechanics

When a parent particle moves, it passes its current `x` and `y` coordinates to the newly created particles in the target system.

> **Important:** The created particles "detach" from the parent. They appear at its position but then live according to the rules of their own system (they can have their own speed, gravity, and lifetime).

#### 3. Timer Isolation

Due to application of `particles_properties` and unique counters (`_RENP_INT_REM_EM`), timers of different fragmenters do not conflict. If a particle has two different trails (e.g., smoke and sparks), they will generate independently.

#### 4. Working within the Same System

If you do not specify a `system "id"` or specify an invalid `id`, the emitter will work in the current system (where it was defined).

### Usage Examples

#### Creating a "Rocket" with a Smoke Trail:

In this example, the `rocket` system flies upward and leaves a particle in the `smoke_trail` system every 0.05 seconds.

```renpy
rparticles define multiple "projectile":
    system id "smoke_trail":
        # ... smoke settings (fade out, upward drift) ...
        preset auto_expire

    system id "rocket":
        # ... rocket settings ...
        on update:
            move:
                velocity [0, -500]

            # Generate trail
            interval_fragmentation_per_particle system "smoke_trail":
                amount 1
                interval 0.05

```

### Technical Notes:

* **UpdateState.Pass**: The handler always returns `Pass`, as it does not change the state of the current particle but merely initiates a side effect in another system.
* **Performance**: Using very small intervals (less than 0.02) with a large number of parent particles can lead to an exponential increase in the number of objects in memory. It is recommended to combine fragmentation with `preset auto_expire` in the target system.
* **Coordinate Copying**: New particles receive the `sprite.x` and `sprite.y` values at the moment of creation. If the target system has an offset, it will be applied on top of these coordinates.

---

## Particle Behaviors

### What Are They?

**Behaviors** are the building blocks of logic that create particle effects.

They work as **commands for each particle**:
- `move` — controls physics-based movement
- `rotate` — rotates the sprite
- `attractor` — attracts to a point
- `friction` — slows down movement
- `tween` — smoothly animates properties
- etc.

```renpy
on update:
    move:                 # movement behavior
        velocity [100, 0]
    
    rotate:               # rotation behavior
        speed 360
    
    attractor:            # attraction behavior
        target mouse
        strength 500
```

### Behavior Identifiers (id)

Each behavior can be assigned a unique identifier using the `id` keyword on the same line:

```renpy
on update:
    move id "player_movement":
        velocity [100, 0]
        acceleration [0, 200]
    
    friction:
        target_behavior_id "player_movement"
        friction 0.3
    
    rotate id "spin":
        speed 360
        phase_range 360
```

**Why Use IDs:**

1. **Inter-Behavior Communication**: One behavior can reference another via `target_behavior_id`. For example, `friction` slows down a specific movement, not all at once.

2. **Debugging and Control**: Easily identify specific behaviors within the system.

4. **Extensibility**: Enables complex interaction chains between independent behaviors.

**How It Works:**
- ID must be unique within a single particle system
- Set immediately after the behavior name, before the parameter block
- Case-sensitive
- Can contain letters, numbers, and underscores

**Example with Multiple IDs:**

```renpy
on update:
    simple_move id "bullet_motion":
        velocity [500, 0]
    
    attractor id "gravity_well":
        target (960, 540)
        strength 3000
    
    friction id "air_resistance":
        target_behavior_id "bullet_motion"  # References the simple_move behavior
        friction 0.1
    
    rotate id "tumble":
        speed 720
        phase_range 360
```

> **Note:** The ID system is especially useful when combining behaviors that modify each other (e.g., `friction`, `bounce` bound to a specific movement).
```

---

### Handler: auto_expire or preset: auto_expire

Automatically decreases lifetime and removes particles:

```renpy
on update:
    auto_expire
```
or
```renpy
preset auto_expire
```

---

### Handler: `bounds_killer` or preset: `bounds_killer`

A handler for forcibly destroying particles that move beyond the visible screen area or specified boundaries. Unlike `auto_expire`, which is time-based, this handler operates based on spatial coordinates.

**Usage Example:**

```renpy
on update:
    bounds_killer:
        margin 50
        only_if_completely True

```
or
```renpy
preset bounds_killer:
    margin 50
    only_if_completely True

```

**Parameters:**

* **`margin`** (number, list, or tuple) — The "buffer" zone outside the screen in pixels. Default is `32`.
    * `margin 100` — The particle will be destroyed if it moves more than 100 pixels beyond the screen edges on any side.
    * `margin (100, 200)` — 100px horizontal margin, 200px vertical margin.
    * `margin (50, 100, 50, 150)` — Individual margins (Left, Top, Right, Bottom).


* **`only_if_completely`** (bool) — The boundary check mode.
* `False` (default) — The particle is destroyed as soon as its **center** (pivot point) crosses the boundary.
* `True` — The particle is destroyed only when it is **completely** hidden behind the boundary (takes sprite size into account). Recommended for large objects to prevent sudden snapping out of existence.


* **`safe_zone`** (float) — An internal "safe zone" from the screen edges. If a particle is inside this zone, the boundary checks are ignored. This is useful for optimizing logic in highly complex systems.

> **Performance Tip**: Always use `bounds_killer` in systems with infinite lifetimes or fast-moving particles (`move`) to prevent "ghost" particles from accumulating off-screen and slowing down the game over time.

---

## Handler: move

The `move` handler is responsible for the physical movement of particles within the system space. It implements the classic motion model where, at each step, the particle's velocity changes its position, and acceleration changes the velocity itself.

### Parameters for the `move` block:

* **`velocity`** `[x, y]` (list of floats): The initial velocity of the particle in pixels per second.
* **`velocity_range`** `[x, y]` (list of floats): The radius of random variation for the initial velocity. The final value is calculated as `velocity ± random(velocity_range)`.
* **`acceleration`** `[x, y]` (list of floats): Constant acceleration (e.g., gravity).
* **`acceleration_range`** `[x, y]` (list of floats): The radius of random variation for acceleration. This allows particles in the same stream to fall or rise with varying intensity.

### Usage Examples

#### 1. Fountain Effect (Gravity)

Particles shoot upwards with some spread and eventually start falling down due to acceleration.

```renpy
on update:
    move:
        velocity [0.0, -400.0]        # Fast upward
        velocity_range [100.0, 50.0]  # Slight spread sideways
        acceleration [0.0, 800.0]     # Strong downward gravity

```

#### 2. Wind or Drift

Particles drift slowly sideways, gradually accelerating.

```renpy
on update:
    move:
        velocity [50.0, 0.0]
        acceleration [20.0, 5.0]     # Light impulse right and down
        acceleration_range [5.0, 2.0] # Flow non-uniformity

```

### Technical Implementation Details

1.  **Two-Pass Update**: The handler updates the state in two stages:
    * First, the `x` and `y` coordinates are changed based on the current velocity.
    * Then, the velocity itself is updated based on the acceleration.
    This ensures correct parabolic motion.

2.  **State Permanence**: Unlike purely visual transformations, the `velocity` and `acceleration` values are calculated once when the particle is initialized and stored in `particles_properties`. This guarantees that the particle's "physical profile" remains unchanged for its entire life.
3.  **Axis Independence**: Calculations for the X and Y axes are completely separate, allowing for the simulation of complex forces, such as strong lateral resistance combined with weak vertical fall.
4.  **Delta-time Scaling**: All calculations are multiplied by `delta` (the time elapsed since the last frame), making motion smooth and independent of the frame rate.

### Important Note on Coordinates:

The `move` handler directly modifies the `particle.x` and `particle.y` properties. These coordinates determine the **center** position of the particle (due to application of the the automatic `size/2` offset in the rendering system).

---

## Handler: simple_move

The `simple_move` handler implements uniform linear motion. The particle's velocity is set once when it is born and remains unchanged throughout its life.

### Parameters for the `simple_move` block:

* **`velocity`** `[x, y]` (list of floats): The velocity vector (pixels per second).
* **`velocity_range`** `[x, y]` (list of floats): The range of random velocity deviation per axis. The final particle velocity is calculated as `velocity ± random(velocity_range)`.

---

### Usage Examples

#### 1. Straight Stream (Laser or Bullets)

All particles fly at the same speed in one direction.

```renpy
on update:
    simple_move:
        velocity [1000.0, 0.0]  # Fast flight to the right

```

#### 2. Scattered Explosion (without gravity)

Particles fly out from the center in all directions and continue moving inertially.

```renpy
on update:
    simple_move:
        velocity [0.0, 0.0]
        velocity_range [300.0, 300.0] # Scatter in random directions

```

### Technical Implementation Details

1.  **Linear Inertia**: Unlike the main `move` handler, there is no acceleration vector (`acceleration`). The velocity (`velocity`) is calculated using the `_get_velocity()` method only once.
2.  **Performance Optimization**: Because the velocity is constant, the engine doesn't need to perform addition operations to change the velocity vector every frame. This makes `simple_move` an ideal choice for systems with a very large number of particles (e.g., dense snow or rain without wind).
3.  **State Preservation**: The velocity vector is stored in `particles_properties` under the unique key `_renp_simple_vel_<id>`. This ensures that even if the system is `freeze`d or paused, the particle will continue moving along the same trajectory when resumed.
4.  **Delta-time**: The position is updated using the frame time (`delta`), ensuring consistent movement speed at both 30 FPS and 144 FPS.

### Comparison with `move`:

| Feature | move | simple_move |
| --- | --- | --- |
| **Acceleration** | Supported | No |
| **Trajectory** | Parabolic (curved) | Straight line |
| **Load** | Medium | Low |
| **Application** | Gravity, physics, smoke | Precipitation, bullets, simple backgrounds |

---

## Handler: `friction`

Simulates friction or air resistance by gradually slowing down a particle. Instead of moving the particle itself, it directly modifies the velocity vector of another behavior (like `move` or `simple_move`).

**Parameters:**

* **`target_behavior_id`** (string, **required**) — The `id` of the behavior whose velocity should be dampened.
> The handler by `id` must have the `.get_key()` method. The system handlers `move` and `simple_move` have this method by default. If there is no such method, then `friction` will not do anything.
* **`friction`** (float) — Friction strength. Higher values lead to faster deceleration. Default is `0.1`.
* **`per_axis`** (boolean) — If `True`, friction is applied to each axis independently. If `False`, it dampens the overall speed vector. Default is `True`.
* **`min_speed`** (float) — The speed threshold below which the particle is considered stopped. Default is `0.01`.

**Usage Example:**

```renpy
on update:
    # Define movement with a specific ID
    simple_move id "bullet_speed":
        velocity [1000, 200]
    
    # Apply friction to that movement
    friction:
        target_behavior_id "bullet_speed"
        friction 5.0
        min_speed 0.1
```
---

## Handler: `bounce`

Enables particles to bounce off screen boundaries or custom margins. It requires a movement behavior (e.g., `move`) to function properly.

**Parameters:**

* **`target_behavior_id`** (string, **required**) — The ID of the movement behavior whose velocity will be inverted upon impact.
* **`restitution`** (float) — Energy recovery coefficient (`0.0` to `1.0`).
* * `1.0`: Perfectly elastic bounce (no speed loss).
* * `0.0`: Particle "sticks" to the boundary.
* **`margin`** (float/tuple) — Screen boundary offsets.
* * Single number: uniform margin for all sides.
* * List `[left, top, right, bottom]`: unique offsets for each side.
* **`bounce_axes`** (string) — Axis to bounce on: `"both"`, `"x"`, or `"y"`.

**Usage Example:**

```renpy
on update:
    simple_move id "projectile":
        velocity [500, 500]
    
    bounce:
        target_behavior_id "projectile"
        restitution 0.9
        bounce_axes "both"
```

---

## Handler: rotate

The `rotate` handler controls the rotation of particle sprites. It allows setting both the initial rotation angle (phase) and a constant rotation speed, with the possibility of randomization for each individual particle.

### Parameters for the `rotate` block:

* **`speed`** (float): Base rotation speed in degrees per second. Default `360.0`.
* **`speed_range`** (float): Range of random speed deviation. The final speed will be within `[speed - speed_range, speed + speed_range]`.
* **`phase`** (float): Base initial rotation angle in degrees.
* **`phase_range`** (float): Range of random initial angle deviation. The final phase will be within `[phase - phase_range, phase + phase_range]`.

### Usage Examples

#### 1. Chaotic Rotation (Sparks/Shards)

Each particle gets a random initial orientation and a unique rotation speed.

```renpy
on update:
    rotate:
        speed 180.0       # Base speed
        speed_range 360.0 # Speed from -180 to +540 deg/sec
        phase_range 360.0 # Random initial rotation (0-360)

```

#### 2. Uniform Slow Rotation (Snowflakes/Leaves)

Particles rotate slowly in one direction with slight speed variation.

```renpy
on update:
    rotate:
        speed 45.0
        speed_range 15.0  # Speed from 30 to 60 deg/sec
        phase_range 90.0

```

### Technical Implementation Details

1.  **Centering**: Rotation occurs around the geometric center of the sprite (due to application of the automatic `size/2` offset in the engine), preventing rotation around a corner.
2.  **Cumulative Effect**: Unlike `tween`, which sets absolute values, `rotate` accumulates the rotation angle (`total_rotation`) each frame based on `delta`. This allows particles to rotate indefinitely without jumps.
3.  **Data Isolation**: The `speed` and `phase` parameters are calculated once during particle initialization in `_get_initial_data` and stored in `particles_properties`. This ensures that a particle's rotation speed does not change throughout its life.
4.  **Queue Transform**: It uses `particle.queue_transform(rotate=...)`, allowing rotation to be combined with other transformations (e.g., `zoom` or `alpha` from `tween` blocks) without overwriting each other.
> **Important Note:** The `.queue_transform(...)` method is **not** additive or multiplicative. It simply writes the value to a queue for application. If two different handlers (e.g., two different `rotate` blocks or a `tween`) attempt to change the same property in one `update` cycle, the **last** one called will overwrite the previous value.

---

### Developer Tip:

Using `phase_range 360.0` is the simplest and most effective way to eliminate visual repetition (patterns) in a particle system, as even identical sprites will look different under random angles.

---

## Handler: flicker
Adds a random "flicker" effect to a property value every frame. It works additively, meaning it adds to existing transformations (like transparency animations) without overriding them.

### Parameters for the `flicker` block:

* **`property`** (string) — Property name (`"alpha"`, `"zoom"`, `"rotate"`).
* **`base_value`** (number) – If the property is not changed in any way by other blocks, then this value is taken as the initial value and a "shake" is applied to it.
* **`range`** (tuple) — Range for random values `(min, max)`.
* **`interval`** (float) — Delay between jitter value changes (in seconds). 0.0 for every frame.
* **`mode`** (string) — Blend mode:
* * `"add"` — Value is always added (increases brightness/size).
* * `"sub"` — Value is always subtracted (decreases brightness/size).

**Usage Example:**

```renpy
on update:
    flicker:
        property "zoom"
        range (-0.05, 0.05) # Subtle size jittering
```

---

## Handler: oscillate

The `oscillate` handler adds an oscillatory component based on a sine function to the particle's current coordinates. This motion is layered on top of any other movement (e.g., `move` or `simple_move`).

### Parameters for the `oscillate` block:

* **`amplitudes`** `[x, y]` (list of floats): The maximum deviation from the center point along the X and Y axes.
* **`frequencies`** `[x, y]` (list of floats): The number of complete oscillations per second.
* **`phases`** `[x, y]` (list of floats): The initial phase shift (in radians). Allows particles in the same system to oscillate asynchronously.
* **`amplitudes_range` / `frequencies_range` / `phases_range`**: Random deviations for the respective parameters, calculated individually for each particle upon its creation.

### Usage Examples

#### 1. "Floating" Firefly Effect

Slow, chaotic oscillations along both axes.

```renpy
on update:
    oscillate:
        amplitudes [30.0, 30.0]
        amplitudes_range [10.0, 10.0]
        frequencies [0.5, 0.5]
        phases_range [6.28, 6.28] # Random initial phase (0 - 2pi)

```

#### 2. Falling Leaf (Zigzag)

A combination with `simple_move`. The leaf falls down, swaying side-to-side horizontally.

```renpy
on update:
    simple_move:
        velocity [0.0, 100.0]
    oscillate:
        amplitudes [50.0, 0.0]  # Oscillations only on X
        frequencies [1.5, 0.0]

```

### Technical Details and Nuances

1.  **Additivity**: The handler is **additive**. This means it does not set the particle's coordinate but adds the calculated displacement to the current `particle.x` and `particle.y` values. This allows using multiple `oscillate` blocks simultaneously or in combination with `move` or `simple_move` blocks to create complex Lissajous figures.
2.  **Drift**: Since the displacement is calculated based on `delta` and added every frame, a mathematical error (floating-point error) can accumulate over time.
    * *What this means:* For very long particle lifetimes, the "oscillation center" may shift slightly relative to the original trajectory. This is imperceptible for short-lived effects.

3.  **Parameter Independence**: Each axis (X and Y) has its own timer and set of settings, allowing for circular or elliptical motion by setting the same frequencies but different phases.
4.  **Performance**: It uses the `math.sin` function, which is somewhat heavier than `move`, but due to application to storing precomputed parameters in `particle_data`, the calculation remains efficient even for hundreds of particles.

### Mathematical Note:

The displacement per frame is calculated by the formula:

$$\Delta = A \cdot \sin(2\pi \cdot f \cdot t + \phi) \cdot dt$$

Where $A$ is the amplitude, $f$ is the frequency, $t$ is the accumulated lifetime, $\phi$ is the phase, and $dt$ is the frame time (`delta`).

---

## Handler: orbit_mouse or preset orbit_mouse

The `orbit_mouse` behavior makes particles strive for a circular orbit around the current mouse position and rotate along it. Due to application the `pull_strength` parameter, particles can gently fly towards the cursor from any point on the screen, creating an effect of organic attraction.

![ehehehe](../gif_examples/orbit_mouse.gif)

### Parameters for the `orbit_mouse` block:

* **`radius`** (float): The desired orbit radius in pixels. Default `100.0`.
* **`speed`** (float): Base angular rotation speed. Default `10.0`.
* **`speed_variance`** (float): Speed variation for each particle (coefficient 0.0–1.0). Allows particles in a swarm to move at different paces. Default `0.5`.
* **`pull_strength`** (float): The strength of attraction to the ideal point on the orbit (0.0–1.0). The higher the value, the more tightly the particle is "chained" to the radius. Default `0.5`.
* **`clockwise`** (bool): Rotation direction. `True` — clockwise, `False` — counter-clockwise.
* **`screen_bounds`** (bool): If `True`, particles cannot fly outside the game window boundaries (held within 2 pixels of the edge). Default `True`.

### Usage Examples

#### 1. Dense Magic Ring Around the Cursor

Particles follow the mouse quickly and rigidly.

```renpy
on update:
    orbit_mouse:
        radius 80.0
        speed 15.0
        pull_strength 0.8
        speed_variance 0.2

```

#### 2. Lazy "Firefly" Swarm

Gentle attraction and wide speed variation create the effect of a living cloud.

```renpy
on update:
    orbit_mouse:
        radius 200.0
        speed 3.0
        pull_strength 0.1
        speed_variance 0.8
        clockwise False

```

### Technical Implementation Details

1.  **Dynamic Capture**: If the distance to the mouse becomes critically small (< 1 pixel), the handler automatically "ejects" the particle onto the specified radius at a random angle to avoid division by zero in calculations and visual "clumping".
2.  **Vector Mathematics**:
    * The algorithm calculates the normalized vector from the mouse to the particle (`nx`, `ny`).
    * Based on the direction (`clockwise`), a perpendicular vector for rotation is created.
    * The particle's final position is an interpolation between its current location and the target point on the orbit, multiplied by `pull_strength`.

3.  **Individuality**: Each particle's speed is calculated once during initialization, considering `speed_variance`, and stored in `_orbit_speed`. This prevents "marching in formation" and makes the swarm chaotic and lively.
4.  **Safety (Screen Bounds)**: The built-in boundary check ensures that even with a sharp mouse movement, particles don't "fly off into infinity", which is critical for interactive menus.

### Developer Note:

This handler works best as the **sole** position controller. If you add `move` or `oscillate` in the same `on update` block, particles may behave unpredictably (shake or spiral away), as `orbit_mouse` constantly overwrites the `particle.x/y` coordinates, trying to return them to the orbit. However, experimentation is not forbidden :).

---

## Handler: `orbit_point`

Functionally similar to `orbit_mouse`, but uses a static screen coordinate as its anchor. Particles gravitate toward a defined radius and rotate around the center point.

**Parameters:**

* **`center`** (2D tuple, **required**) — The orbit center coordinates `(x, y)`.
* **`radius`** (float) — Target orbit radius in pixels. Default is `100.0`.
* **`speed`** (float) — Base rotation speed. Default is `10.0`.
* **`speed_variance`** (float) — Speed variation per particle (from 0.0 to 1.0). Default is `0.5`.
* **`pull_strength`** (float) — "Gravity" strength toward the radius (from 0.0 to 1.0). Controls how fast particles snap to the circle. Default is `0.5`.
* **`clockwise`** (boolean) — Rotation direction. `True` for clockwise. Default is `True`.
* **`screen_bounds`** (boolean) — Keep particles within screen limits. Default is `True`.

**Usage Example:**

```renpy
on update:
    orbit_point:
        center (1280, 720)
        radius 150
        speed 20.0
        clockwise False
```

---

## Handler: `attractor`

Creates a point of attraction (or repulsion) that influences particles using force-based physics. Unlike `orbit`, it applies acceleration, resulting in natural inertial movement.

| Example |
| :---: |
| ![attractor-center](../gif_examples/attractor.gif) |

**Parameters:**

* **`target`** ("mouse"/tuple, **required**) — Attraction point. Either `"mouse"` or a coordinate tuple `(x, y)`.
* **`strength`** (float) — Attraction force. Positive attracts, negative repels. Default is `500.0`.
* **`radius`** (float) — Effective radius. `0.0` means it affects the entire screen. Default is `0.0`.
* **`falloff`** (float) — How the force diminishes over distance:
* * `0.0`: Constant force regardless of distance.
* * `1.0`: Linear falloff (like gravity).
* * `2.0+`: Exponential falloff (like magnetic force).

* **`max_speed`** (float) — Velocity cap to prevent particles from accelerating to infinity. Default is `1000.0`.
* **`screen_bounds`** (boolean) — Keep particles within screen limits. Default is `True`.

**Usage Example:**

```renpy
on update:
    # Magnetic cursor effect
    attractor:
        target "mouse"
        strength 1500.0
        radius 400.0
        falloff 1.5
```

---

## Handler: repulsor

*This functionality is based on the classic example from Ren'Py documentation but adapted to the RenParticles architecture with a split into update (update) and event handling.*

The pair `repulsor_update` and `repulsor_event` creates a repulsion zone. When the mouse cursor comes near a particle, it is pushed outside the specified radius.

### Syntax:

```renpy
on update:
    repulsor_update:
        strength 5.0     # Impulse strength
        radius 200.0     # Influence distance
        clamp_margin 2.0 # Keep inside screen bounds

on event:
    repulsor_event       # Passes mouse coordinates to the system

```

### Parameters:

* **`strength`** (float): The force with which the particle is pushed away from the center. Default `3.0`.
* **`radius`** (float): The "repulsor's" range of action. If the particle is further than this distance, the effect is not applied. Default `150.0`.
* **`clamp_margin`** (float): The margin from the system's edges, so particles pushed off-screen don't disappear entirely but "stick" to the edge. Default `2.0`.

### How It Works (Architecture)

1.  **Event Layer (`repulsor_event`)**: This handler triggers when the mouse moves over the particle area. It writes the current `x, y` coordinates to the system's shared data storage (`system.particles_data.repulsor_pos`). This saves each particle from needing to query the Ren'Py engine directly.
2.  **Update Layer (`repulsor_update`)** :
    * Every frame, the particle checks for the presence of `repulsor_pos`.
    * The vector between the particle and the "repulsor" is calculated.
    * **Falloff**: The repulsion force is not constant. It is maximal at the center and linearly decreases to zero at the radius boundary. This creates a soft pushing effect, not a sharp teleport.
    * **Clamp**: If the force pushes the particle beyond the `width/height` boundaries, the handler forcibly returns it to the edge, considering the `clamp_margin`.

### Usage Examples

#### 1. Interactive Cloud (Fog "Dispersing" Effect)

Particles drift slowly but scatter when the mouse is hovered over them.

```renpy
rparticles define preset interactive_fog:
    on update:
        simple_move:
            velocity [10, 0]
        repulsor_update:
            strength 4.0
            radius 180.0
    on event:
        repulsor_event

```

#### 2. Protective Barrier

With a very high strength, the mouse acts as an impenetrable shield for particles.

```renpy
on update:
    repulsor_update:
        strength 50.0 # Instant push
        radius 100.0

```

### Implementation Nuances

* **Pair is Mandatory**: `repulsor_update` by itself does not know where the mouse is. It needs the data provided by `repulsor_event`.
* **Context Type**: The code includes strict checks: `repulsor_event` can only work within `on event`, as it requires an `EventContext` (containing event coordinates). Attempting to call it in `on update` will cause a clear error.
* **Additivity**: Like the oscillator, this handler modifies `p.x/y` directly, adding the force to the current position. This means it combines well with any movement methods (`move`, `simple_move`), acting as an "external force".

### Using the Ready-Made Preset:

There is a global-level preset `repulsor` that allows you to connect everything at once with a single line.
The preset is static, meaning it knows how to distribute overridable parameters:

```renpy
rparticles define system "my_system":
    preset repulsor:
        strength 10.0
        radius 250.0

```

---

## Handler: tween

The `tween` handler is designed for smoothly changing a sprite's transformation properties (alpha, zoom, rotate, etc.) over time. It supports both fixed time intervals and dynamic binding to the particle's lifecycle.

### Parameters for the `block`:

* **`time`** (float): Animation duration. In `absolute` mode — seconds; in `lifetime` mode — coefficient (0.0–1.0).
* **`start_value`** (float): The initial value of the property.
* **`end_value`** (float): The final value of the property.
* **`warper`** (string): The interpolation function (names of standard [Ren'Py warpers](https://www.renpy.org/doc/html/transforms.html#warpers): `"linear"`, `"ease"`, `"easein_expo"`, `"easein_circ"`, etc.). Default `"linear"`.
* **`mode`** (string): Time calculation mode:
  * `"absolute"` (default): `time` is treated as a fixed time in seconds.
  * `"lifetime"`: `time` is treated as a fraction of the particle's total lifetime.

* **`from_end`** (bool): If `True`, the animation will start at the end of the particle's life, finishing exactly at the moment of its disappearance.

### Usage Examples

#### 1. Basic Animation (Absolute Time)

Simple fade-in and scale-down upon creation.

```renpy
on update:
    tween:
        block "alpha":
            time 0.5
            start_value 0.0
            end_value 1.0
        block "zoom":
            time 1.0
            start_value 2.0
            end_value 1.0
            warper "ease"

```

#### 2. Adaptive Animation (Lifetime mode)

Animation that adjusts to the particle's lifetime. If a particle lives for 2 seconds, alpha fades in over 0.4s. If it lives for 10 seconds — over 2s.

```renpy
on update:
    tween:
        block "alpha":
            mode "lifetime"
            time 0.2  # 20% of lifetime for fade-in
            start_value 0.0
            end_value 1.0

```

#### 3. Fade-Out Animation (from_end)

For example, for smoothly fading out particles before removal. The animation will start automatically based on the remaining lifetime.

```renpy
on update:
    # Animate alpha to 0.0 in the last 0.5 seconds of life
    tween:
        block "alpha":
            from_end True
            time 0.5
            start_value 1.0
            end_value 0.0

```

### Technical Implementation Details

1.  **Parallel Property Execution**: You can describe multiple `block`s for different properties inside a single `tween` block. They will run in parallel and independently.
2.  **State Uniqueness**: Each particle stores its animation progress in `particles_properties` under a unique key, preventing conflicts when using multiple `tween` blocks in one system.
3.  **Optimization**: After all animations in a block are complete, the handler sets a `_completed` flag and stops performing calculations in `__call__`, simply skipping iterations (`UpdateState.Pass`).
4.  **Safety**: All output values are passed through `_renp_clamp`, preventing them from going outside the `[start, end]` range, which is critical when using complex warpers with "bounces".

**Available Properties:** alpha, zoom, xzoom, yzoom, rotate, xpos, ypos, and other `Transform` properties.

> **Important Note**: Keep in mind that property transformation is a relatively expensive operation for RenPy, so using a `tween` handler significantly burdens the CPU. However, increasing the number of `tween` blocks has a relatively minor impact on performance because **RenParticles** uses **Lazy Rendering** and `tween` leverages this mechanism. All `tween` blocks merely send a new transformation to a queue, and the engine applies them all at once at the end of the frame. More details in Developer_En.md (section *Visualization Management*)

---

## Presets

Presets are ready-made combinations of behaviors.

### Built-in Presets

```renpy
preset spray:
    amount 100

preset interval_spray:
    amount 500
    interval 0.05

preset auto_expire

preset repulsor:
    strength 5.0
    radius 200.0

preset orbit_mouse:
    speed 10.0
    pull_strength 0.5
```

### Creating Custom Presets

```renpy
init 100:
    rparticles define preset my_preset type general:
        on update:
            move:
                velocity [0.0, 100.0]
                acceleration [0.0, 50.0]

            tween:
                block "alpha":
                    time 1.0
```

**Preset Types:**
- `type general` — used at the top level of the system.
- `type inner` — used inside on update/event/particle dead blocks.

### Technical Implementation Notes
1.  **Single-Level**: Recursive presets are not available.
2.  **Parameter Dispatching**: Dynamic presets do not know how to pass overridable parameters (when you open a parameter block while using a preset in a system). Such parameters will not go anywhere, although it is possible to specify them. Keep this in mind.

---

## Multiple Systems

Creating several independent particle systems:

```renpy
rparticles multiple as particles onlayer master:
    redraw asap

    system id "fire":
        sprite expr Solid("#ff4400", xysize=(8, 8))
        lifetime constant 1.0

        preset interval_spray:
            amount 100
            interval 0.01

        on update:
            move:
                velocity [0.0, -100.0]
            auto_expire

    system id "sparks":
        sprite expr Solid("#ffff00", xysize=(4, 4))
        lifetime range random (0.5, 1.5)

        preset spray:
            amount 50

        on update:
            move:
                velocity [0.0, 0.0]
                velocity_range [200.0, 200.0]
            auto_expire
```

Interaction between systems:

```renpy
on update:
    interval_fragmentation_per_particle system "sparks":
        amount 3
        interval 0.2
```

---

## Models (Templates)

Saving a configuration for reuse:

```renpy
init:
    rparticles define "explosion_effect":
        sprite expr Solid("#ff0000", xysize=(16, 16))
        lifetime range random (0.5, 1.5)
        redraw asap

        preset spray:
            amount 200

        on update:
            move:
                velocity [0.0, 0.0]
                velocity_range [300.0, 300.0]
                acceleration [0.0, 500.0]

            tween:
                block "alpha":
                    time 1.0
                block "zoom":
                    time 1.0
                    start_value 1.5
                    end_value 0.0

            auto_expire

label game:
    # Using the model
    rparticles model "explosion_effect" as explosion1
```

---

## System Management

### Control Commands

```renpy
# Show a system
rparticles model "my_model" as particles

# Reset the system (delete all particles, restart emitters and handlers)
rparticles reset "particles"

# Freeze the system (stop updates)
rparticles freeze "particles"

# Unfreeze the system
rparticles unfreeze "particles"
rparticles unfreeze "particles" noredraw

# Manage subsystems
rparticles freeze "particles"."fire"
rparticles unfreeze "particles"."sparks" noredraw

# Hide the system
hide particles

# Show again
rparticles continue "particles" onlayer master zorder 1

# Clear cache
rparticles clear cache        # delete hidden systems
rparticles clear cache deep   # delete all systems
```

---

## Advanced Features

### Custom Functions

Instead of shortcuts, you can use Python classes inherited from `_Behavior`, `Emitter`:

```renpy
on update:
    custom my_custom_Behavior oneshot
    custom my_custom_Behavior system "target_system"
```

### oneshot Modifier

Execute a behavior once:

```renpy
on update:
    emitter spray oneshot:
        amount 100
```

### Dynamic Properties

For complex configurations:

```renpy
tween:
    block "alpha":
        time 0.5
    block "zoom":
        time 1.0
        start_value 2.0
        end_value 0.5
        warper "easein"
```

---

## Examples

### Simple Rain

```renpy
rparticles as rain onlayer master:
    sprite expr Solid("#4488ff", xysize=(2, 8))
    lifetime constant 3.0
    redraw 0.016

    preset interval_spray:
        amount 1000
        interval 0.01
        per_amount 5

    on update:
        move:
            velocity [0.0, 500.0]
        auto_expire
```

### Firework (Example of a Complex Chain)

```renpy
rparticles multiple as firework:
    system id "trail":
        sprite expr Solid("#ffffff", xysize=(2, 2))
        lifetime constant 0.5
        on update:
            tween:
                block "alpha":
                    from_end True
                    time 0.5
                    start_value 1.0
                    end_value 0.0
            auto_expire

    system id "shell":
        sprite expr Solid("#ffff00", xysize=(4, 4))
        lifetime constant 1.5
        on update:
            move:
                velocity [0, -400]
                acceleration [0, 200]
            # Create a trail from the 'trail' system
            interval_fragmentation_per_particle system "trail":
                amount 1
                interval 0.02
            auto_expire
        # Explosion upon "shell" death
        on particle dead:
             emitter spray oneshot:
                amount 50
                # Add logic for shrapnel scatter here if needed
```

### Magical Effect

```renpy
rparticles as magic onlayer master:
    sprite expr Solid("#aa00ff", xysize=(12, 12))
    lifetime range random (2.0, 4.0)
    redraw asap

    preset interval_spray:
        amount 200
        interval 0.02

    on update:
        orbit_mouse:
            radius 100.0
            speed 8.0
            pull_strength 0.2

        tween:
            block "alpha":
                time 2.0

        auto_expire
```

---

## Performance Tips

1.  Use `redraw 0.016` instead of `asap` if maximum frequency is not needed.
2.  Limit the number of simultaneous particles.
3.  Use `lifetime` for automatic particle removal.
4.  For static effects, use `cache`.
5.  Group similar particles into one system.

---

## Debugging

The system outputs configuration information to the console upon creation. Check the Ren'Py console to diagnose issues.

---

## Limitations

- Sprites are drawn with an offset of `sprite_size / 2` from the specified position.
- Recursive presets are not supported.
- Maximum performance depends on the number of particles and the complexity of behaviors.