# RenParticles

RenParticles is a high-performance, ATL-like DSL (Domain Specific Language) for creating complex particle systems in Ren'Py. It allows developers to define particle behavior using a declarative syntax while maintaining the efficiency of low-level Python execution.

## Installation

1. Download the `00RenParticles` folder.
2. Place it inside your project's `game/` directory.

---

Detailed manuals are in the **docs** folder.

---

## Quick Start (DSL Example)

```renpy
rparticles show magic_circles:
    on update:
        # Using built-in move behavior
        move:
            velocity (0, -100)
            friction 0.05
        
        # Using tween for animation
        tween:
            time 2.0
            block:
                property "alpha"
                range (0.0, 1.0)
                warper "linear"

    # Define how particles are spawned
    emitter spray:
        rate 10
        circle_radius 50

```

---

## Developer Guide

### Architecture Overview

The system is built on three layers:

1. **DSL Parser** (`01renparticles_cds.rpy`) — Handles the declarative syntax.
2. **Core Engine** (`renparticles_fast.rpy`) — Manages particle lifecycle and rendering.
3. **Behaviors & Emitters** — Extensible logic components.

### 1. Creating Custom Behaviors

All behaviors must inherit from `_Behavior`. The logic is implemented in the `__call__` method.

```python
class SimpleBounce(_UpdateBehavior):
    bounce_factor = 0.8
    
    def __call__(self, context):
        particle = context.particle
        system = context.system
        
        # Simple boundary check
        if particle.x < 0 or particle.x > system.width:
            particle.x = renparticles._renp_clamp(particle.x, 0, system.width)
            # Custom logic here...
            
        return UpdateState.Pass

```

### 2. Component Registration

To use your Python classes in the DSL, you need to register them.

#### Static Registration (Not recommended for modifications)

Defined in `fast_particles.rpy`.

#### Dynamic Registration (Recommended)

Add your components without modifying core files:

```python
init python:
    # Registering a behavior
    renparticles.add_shortcut("my_behavior", MyCustomBehavior, is_emitter=False)
    
    # Registering an emitter
    renparticles.add_shortcut("my_emitter", MyEmitter, is_emitter=True)

```

### 3. The Smol Tweening Engine `-_-`

The `tween` handler is a powerful tool for animating particle properties (alpha, zoom, rotate, etc.).

**Technical Features:**

* **Parallel processing of properties**: Multiple `block` definitions can run concurrently for different properties within one `tween` block.
* **State Isolation**: Each particle stores its own animation progress, preventing conflicts between multiple systems.
* **Optimization**: Once an animation finishes, the handler sets a `_completed` flag and skips calculations to save CPU cycles.
* **Lazy Rendering**: All `tween` blocks queue transformations, which are applied all at once at the end of the frame.

### 4. RenSprite Properties

The `RenSprite` class extends the standard Ren'Py Sprite with additional fields:

* `x, y`: Position.
* `zorder`: Rendering order.
* `live`: Boolean flag (if False, the particle is destroyed).
* `lifetime`: Current remaining time.
* `queue_transform(**kwargs)`: Queues a visual change for the next frame.

### 5. Multi-System Management

Use `RenParticleFastGroup` to sync multiple systems.

```python
# Create a group of systems
rparticles show fire_effect multiple:
    system "smoke":
        # ... smoke config
    system "flames":
        # ... flames config

```

---

## Performance Tips

* **Use Lazy Rendering in your own transorm behaviors**: Avoid direct manipulation of `Transform` objects. Use `particle.queue_transform()` or `particle.queue_transform_additive()` instead.

## License

