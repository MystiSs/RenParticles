# RenParticles - Developer Guide

Here is the `Table of Contents` for your `Developer_En.md` file.

# Table of Contents

* [System Architecture](#system-architecture)
* [Module Structure](#module-structure)
* [Base Classes](#base-classes)
    * [_Behavior](#_behavior)
    * [Behavior Types](#behavior-types)
* [Execution Contexts](#execution-contexts)
    * [RenpFContext](#renpfcontext)
    * [EventContext](#eventcontext)
* [Creating Custom Behaviors](#creating-custom-behaviors)
    * [Simple Behavior](#simple-behavior)
    * [Per-Particle Stateful Behavior](#per-particle-stateful-behavior)
* [Creating Emitters](#creating-emitters)
    * [1. Standard Emitter (`Emitter` Class)](#1-standard-emitter-emitter-class)
    * [2. Streaming Emitter (`_Behavior` Class)](#2-streaming-emitter-_behavior-class)
    * [Comparison of Emitter Types](#comparison-of-emitter-types)
* [Creating Presets](#creating-presets)
    * [1. Basic Preset Architecture](#1-basic-preset-architecture)
    * [2. Preset Creation Example (`RepulsorPreset`)](#2-preset-creation-example-repulsorpreset)
    * [3. Special Preset Types](#3-special-preset-types)
    * [4. Useful Methods of `_RFBehaviorPreset`](#4-useful-methods-of-_rfbehaviorpreset)
    * [5. Implementation Recommendations](#5-implementation-recommendations)
* [Component Registration](#component-registration)
    * [1. Static Shortcuts](#1-static-shortcuts)
    * [2. Dynamic Registration (Recommended)](#2-dynamic-registration-recommended)
    * [3. Technical Registration Nuances](#3-technical-registration-nuances)
    * [4. Initialization Order (Priorities)](#4-initialization-order-priorities)
* [Working with Particles](#working-with-particles)
    * [RenSprite](#rensprite)
    * [Visualization Management](#visualization-management)
    * [Practical Example: Creation and Configuration](#practical-example-creation-and-configuration)
    * [Nuance with `set_child`](#nuance-with-set_child)
* [Particle System: Core](#particle-system-core)
    * [1. RenParticlesFast](#1-renparticlesfast)
    * [2. ParticlesData](#2-particlesdata)
* [Multiple Systems](#multiple-systems)
    * [1. RenParticleFastGroup](#1-renparticlefastgroup)
    * [2. Interaction Between Systems](#2-interaction-between-systems)
* [Technical Reference: Execution Contexts](#technical-reference-execution-contexts)
* [Particle Transformations](#particle-transformations)
    * [PropertyTween](#propertytween)
* [Performance](#performance)
    * [Rendering Optimization](#rendering-optimization-standard-renpy-code-from-spritemanagerrender)
    * [Optimization Tips](#optimization-tips)
* [Debugging](#debugging)
    * [Output System Information](#output-system-information)
    * [Checking Particle State](#checking-particle-state)
* [Advanced Patterns](#advanced-patterns)
    * [Particle Pool](#particle-pool)
    * [Behavior Chains](#behavior-chains)
    * [Conditional Behaviors](#conditional-behaviors)
* [API Reference](#api-reference)
    * [Main Constants](#main-constants)
    * [Utilities](#utilities)
    * [Access to Systems](#access-to-systems)
* [Code Conventions](#code-conventions)
* [Implementation Examples](#implementation-examples)
    * [Gravity](#gravity)
    * [Boundary Collision](#boundary-collision)
    * [Target Following](#target-following)

## System Architecture

RenParticles is built on three levels:

1.  **DSL Parser** (`01renparticles_cds.rpy`) — parses the declarative syntax
2.  **Core Engine** (`renparticles_fast.rpy`) — manages particles and rendering
3.  **Behaviors & Emitters** — extensible behavior components

---

## Module Structure

```
00RenParticles/
├── renparticles_base.rpy          # Base classes and mixins
├── renparticles_fast.rpy          # Main particle engine
├── renparticles_static.rpy        # Utilities and shortcut registration
├── 01renparticles_cds.rpy         # DSL parser
└── Particles Implementation/
    └── Fast Particles/
        ├── Emitters/              # Particle emitters
        ├── Presets/               # Ready-made presets
        ├── move_behaviors.rpy     # Movement behaviors
        ├── tween.rpy              # Property animation
        ├── mouse_orbiting.rpy     # Mouse interaction
        └── ...
```

---

## Base Classes

### _Behavior

The base class for all particle behaviors:

```python
class _Behavior(_InjectPropertiesMixin, _CheckInitialisedMixin, _TryGetOtherSystemMixin):
    def __call__(self, context):
        raise NotImplementedError()
```

**Mixins:**
- `_InjectPropertiesMixin` — property injection via `inject_properties(**props)`
- `_CheckInitialisedMixin` — validation of required fields using `_RequiredField()`
- `_TryGetOtherSystemMixin` — access to other systems via `get_system(context, id)`

### Behavior Types

```python
class _UpdateBehavior(_Behavior):
    """Executed every frame for each particle"""
    pass

class _EventBehavior(_Behavior):
    """Handles mouse events"""
    pass

class _OnDeadBehavior(_Behavior):
    """Executed when a particle dies"""
    pass

class Emitter(_Behavior):
    """Creates new particles"""
    pass
```

---

## Execution Contexts

### RenpFContext

The base context passed to behaviors:

```python
class RenpFContext:
    system = None      # Current particle system
    st = None          # Show time
    delta = None       # Time since last frame
    particle = None    # Current particle (if any)
    systems = None     # Dictionary of all systems by ID
```

### EventContext

Extended context for events:

```python
class EventContext(RenpFContext):
    x = None           # Event X coordinate
    y = None           # Event Y coordinate
    event = None       # Ren'Py event object
```

---

## Creating Custom Behaviors

### Simple Behavior

```python
init -1000 python in renparticles:
    class MyCustomBehavior(_UpdateBehavior):
        # Required fields
        speed = _RequiredField()
        
        # Optional fields with default values
        direction = [1.0, 0.0]
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            
            # Your logic
            particle.x += self.direction[0] * self.speed * delta
            particle.y += self.direction[1] * self.speed * delta
            
            return UpdateState.Pass
```

**Return Values:**
- `UpdateState.Pass` — continue execution
- `UpdateState.Repeat` — repeat (not used)
- `UpdateState.Kill` — remove this behavior from the system

### Per-Particle Stateful Behavior

To store data for each particle, use `particles_properties`:

```python
class MyStatefulBehavior(_UpdateBehavior):
    _MY_DATA_KEY = "_my_behavior_data"
    _COUNTER = 0
    
    def __init__(self):
        # Unique key for each instance
        self._MY_DATA_KEY = f"{self._MY_DATA_KEY}_{self._COUNTER}"
        self._COUNTER += 1
    
    def __call__(self, context):
        particle = context.particle
        particles_props = context.system.particles_data.particles_properties
        
        # Get or create particle data
        particle_data = particles_props.setdefault(particle, {})
        
        if self._MY_DATA_KEY not in particle_data:
            # Initialization on first call
            particle_data[self._MY_DATA_KEY] = {
                "counter": 0,
                "velocity": [random.uniform(-100, 100), random.uniform(-100, 100)]
            }
        
        data = particle_data[self._MY_DATA_KEY]
        data["counter"] += 1
        
        # Use data
        particle.x += data["velocity"][0] * context.delta
        particle.y += data["velocity"][1] * context.delta
        
        return UpdateState.Pass
```

>You can store particle data however you like. For example, within the particle class itself. However, the standard is `particles_properties`. This way, if you need to modify the properties of a group of particles during an update for a single particle, you can access `particles_properties` and iterate over the available particles.

---

## Creating Emitters

Emitters are responsible for generating new particles within the system. In RenParticles, there are two architectural approaches to creating emitters, depending on the required logic.

### 1. Standard Emitter (`Emitter` Class)

Designed for mass particle generation independent of the state of other objects.

```python
class MyEmitter(Emitter):
    # Required fields (will cause an error if missing in DSL)
    amount = _RequiredField() 
    
    # Default values
    spawn_area = (0, 0, 1920, 1080)
    
    def __call__(self, context):
        system = context.system
        images = system.particles_data.images
        
        for i in range(self.amount):
            # Create a sprite based on a random system image
            sprite = system.create(random.choice(images))
            
            # Set initial coordinates
            sprite.x = random.randint(self.spawn_area[0], self.spawn_area[2])
            sprite.y = random.randint(self.spawn_area[1], self.spawn_area[3])
            
            # Set technical sprite properties (RenSprite)
            sprite.zorder = i
        
        return UpdateState.Pass

```

**Architectural Features:**

* **Isolation**: During system initialization, emitters are separated from the general `on update` block and placed into a special priority list.
* **Optimization**: They are called **outside** the iteration loop over live particles.
* **Context**: The `context.particle` attribute is always `None`. This is done to eliminate redundant checks and increase FPS when generating large groups of objects.

### 2. Streaming Emitter (`_Behavior` Class)

Used when the creation of new particles must depend on the state of a "parent" particle (e.g., creating trails or fragmentation during an explosion).

**Mechanism:**

* Inherits directly from `_Behavior` (or `_UpdateBehavior`).
* In the DSL, it is declared **without** the `emitter` keyword.
* Called inside the particle update loop, thus having access to `context.particle`.

> **Implementation Example:** The `EmitterIntervalRemoteSpawn` class uses this approach to read the current particle's coordinates and pass them as the spawn point for particles in another system.

**Another example:**

```python
class MyEmitterPerParticle(_Behavior): # Streaming emitter
    # Required fields (will cause an error if missing in DSL)
    amount = _RequiredField() 
    
    # Default values
    spawn_area = (0, 0, 1920, 1080)
    
    def __call__(self, context):
        system = context.system
        images = system.particles_data.images
        particle = context.particle # Context is guaranteed to have a reference to the current particle
        ...
```

### Comparison of Emitter Types

| Feature | Standard (`Emitter`) | Streaming (`_Behavior`) |
| --- | --- | --- |
| **DSL Keyword** | `emitter <name>` | `<name>` |
| **Loop Location** | Outside particle loop (separate list) | Inside particle loop |
| **Access to `context.particle`** | **No** (`None`) | **Yes** (current particle) |
| **Primary Use** | Global spawn, rain, explosions | Trails, sparks from particles, splitting |
| **CPU Impact** | Minimal (called once per frame) | Depends on particle count (N calls) |

---

## Creating Presets

**Presets** in RenParticles are high-level wrappers that group multiple behaviors and emitters, providing a convenient interface for configuration via DSL.

### 1. Basic Preset Architecture

A preset class inherits from `_RFBehaviorPreset`. Its main task is to initialize a list of behavior classes and distribute parameters from the DSL among these instances.

**Preset Lifecycle:**

1.  **Initialization**: The DSL parser creates a preset instance and writes parameters into it.
2.  **`.build()`**: Called automatically by the engine.
3.  **`.instanciate_behaviors()`**: Turns lists of classes into working instances.
4.  **`.distribute_properties()`**: (You override this) Passes values from the preset to specific behaviors via `inject_properties`.

### 2. Preset Creation Example (`RepulsorPreset`)

Consider a preset that combines particle update logic and mouse event handling.

```python
class RepulsorPreset(_RFBehaviorPreset):
    # 1. Define the set of behaviors
    behaviors = {
        "on_update": [RepulsorUpdate], # Class for repulsion logic
        "on_event": [RepulsorEvent],   # Class for recording mouse coordinates
        "on_particle_dead": None
    }

    # 2. Declare parameters that will be available in the DSL
    repulsor_pos = None
    strength = 3.0
    radius = 150.0
    clamp_margin = 2.0

    # 3. Distribute data
    def distribute_properties(self):
        # Always call super to check for _RequiredField()
        super(RepulsorPreset, self).distribute_properties()

        # Get the instance of the first behavior from the on_update list
        update_logic = self.behaviors["on_update"][0]
        
        # Pass properties into the behavior
        update_logic.inject_properties(
            repulsor_pos=self.repulsor_pos, 
            strength=self.strength, 
            radius=self.radius, 
            clamp_margin=self.clamp_margin
        )

```

### 3. Special Preset Types

| Type | Parent Class | Description |
| --- | --- | --- |
| **Simple Preset** | `_RFBehaviorPreset` | A rigidly defined structure of behaviors in Python. |
| **Dynamic** | `_RFDynamicBehaviorPreset` | Used by the parser to create presets "on the fly" via the DSL command `rparticles define preset`. |

### 4. Useful Methods of `_RFBehaviorPreset`

When writing complex property distribution logic, you may find these built-in methods helpful:

* **`self.is_one_block()`**: Returns `True` if the preset contains only one behavior dict across all categories. Useful for simplified property injection.
* **`self.get_one()`**: Returns the first found behavior dict.
* **`self.check_initialised()`**: Automatically checks if all fields marked as `_RequiredField()` have been filled. Called inside `super(_RFBehaviorPreset, self).distribute_properties()`.

### 5. Implementation Recommendations

* **Dictionary Copying**: In the `__init__` constructor, the base class does `self.behaviors.copy()`. This is critically important: if this weren't done, changing the behavior list in one preset instance would change it for all future systems.
* **Order in Lists**: If multiple behaviors are specified in `on_update`, access them by index in `distribute_properties`, or use loops for batch configuration.
* **Oneshot Presets**: If you set the `m_oneshot = True` flag, the preset will be executed once (useful for instantaneous impulses or single bursts of particles).

---

## Component Registration

For your custom behaviors, emitters, or presets to become available for use within the DSL (e.g., `on update: my_behavior`), they must be registered in the shortcut system.

The system divides registration into two types: **static** (core) and **dynamic** (user extensions).

### 1. Static Shortcuts

Static shortcuts are defined in the `fast_particles.rpy` file inside the `static_shortcuts` dictionary.

> **Important:** It is highly discouraged to modify this dictionary directly in the engine's source files.

If you need to manually add a static shortcut, you can do so from your own file by accessing the `renparticles` RenPy store object:

```python
init 1 python:
    # Example of manually adding to the static dictionary
    renparticles.static_shortcuts["behaviors"]["global_wind"] = MyWindBehavior

```

### 2. Dynamic Registration (Recommended)

To add custom components, use the built-in registration functions. They automatically validate types and prevent accidental overwriting of existing tags.

```python
init python in renparticles:
    # Register a behavior (must inherit from _Behavior)
    # Tag: "fire_logic", Class: FireUpdate
    add_shortcut("fire_logic", FireUpdate, is_emitter=False)
    
    # Register an emitter (must inherit from Emitter or _Behavior)
    add_shortcut("spark_emitter", SparkEmitter, is_emitter=True)
    
    # Register a preset (must inherit from _RFDynamicBehaviorPreset or _RFBehaviorPreset)
    # preset_type can be "general" or "inner"
    add_preset("magic_circle", MagicPreset, preset_type="general")

```

### 3. Technical Registration Nuances

* **Type Validation**: The `add_shortcut` and `add_preset` functions raise a `TypeError` if the registered class is not a descendant of the corresponding base classes (`_Behavior`, `_RFDynamicBehaviorPreset`, or `_RFBehaviorPreset`).
* **Conflict Prevention**: If you attempt to register a tag that already exists in `dynamic_shortcuts`, the system will raise a critical `renpy.error` to avoid unpredictable behavior in the particle system.
* **Priorities**: When searching for a component, the DSL parser first checks static shortcuts, then dynamic ones. Thus, system behaviors always have priority.

### 4. Initialization Order (Priorities)

For registration to work correctly, use the following `init` levels:

* **System Core**: `init -1337` (defines registration functions).
* **Static Shortcuts**: `init -555` (the engine's base set).
* **User Components**: It is recommended to use `init` without an index or above `-555` to ensure that the shortcut dictionaries have already been created.

---

## Working with Particles

### RenSprite

`RenSprite` is an extended class of the standard `Sprite` from the Ren'Py engine. It supports deferred application of transformations.

```python
class RenSprite(Sprite):
    lifetime = 0.0          # Current remaining lifetime
    lifetime_max = 0.0      # Initial lifetime (set by the engine)
    _base_image = None      # Original image without transformations
    
    def queue_transform(self, **properties):
        """Replaces properties in the queue with new ones."""
        self.queued_transforms.update(properties)
    
    def queue_transform_additive(self, **properties):
        """Adds new properties to those already in the queue."""
        # Supports numbers (int/float) and vectors (list/tuple)

```

**Available Properties:**

* **`x, y`** (float): Coordinates of the particle's center on the screen.
* **`zorder`** (int): Drawing order (higher is closer to the player).
* **`live`** (bool): Particle status. If `False`, the system will delete it in the next frame.
* **`lifetime`** (float): Remaining lifetime in seconds.
* **`lifetime_max`** (float): Initial lifetime in seconds. Base handlers do not modify this attribute. It is not recommended to change it at all.
* **`events`** (bool): Flag allowing the particle to react to events (`False` by default for optimization).

---

### Visualization Management

The system uses **Lazy Rendering**. Instead of redrawing the `Transform` on every change to `alpha` or `zoom`, `RenSprite` accumulates changes.

#### Transformation Methods:

1.  **`.queue_transform(**props)`**: Used to set absolute values. If two behaviors try to set `alpha`, the last one wins.
2.  **`.queue_transform_additive(**props)`**: Adds values together. Allows multiple independent behaviors to simultaneously affect a single property (e.g., two different transformation handlers affecting `zoom`. However, these handlers must use `.queue_transform_additive(**props)` in their implementation. For example, the `tween` handler uses `.queue_transform(**props)`, meaning two `tween` handlers will compete to change the same property (the last one added to the processing block wins)).

> **Important:** The system automatically calls `apply_transforms()` at the end of the update cycle. It takes `_base_image` (a copy of the original sprite) and applies all accumulated properties to it once via `Transform`. This significantly saves CPU resources.

### Practical Example: Creation and Configuration

Inside the `__call__` method of your behavior or emitter, you interact with particles via the system object:

```python
def __call__(self, context):
    system = context.system
    
    # 1. Create a particle from the pool of available images
    # system.create returns a RenSprite instance
    sprite = system.create(random.choice(system.particles_data.images))
    
    # 2. Direct control over position and state
    sprite.x = 960
    sprite.y = 540
    sprite.zorder = 10
    sprite.lifetime = 2.0  # Manually setting lifetime
    
    # 3. Working with visual effects
    # Set initial scale and transparency
    sprite.queue_transform(alpha=0.0, zoom=0.5)
    
    # 4. Deleting a particle
    # Calling destroy() does not delete the object instantly, but marks it
    # as 'live = False' for safe cleanup by the engine
    if some_condition:
        sprite.destroy()
        
    return UpdateState.Pass

```

### Nuance with `set_child`

If you dynamically change a particle's image via `set_child(d)`, the `_base_image` field is automatically reset to `None`. This forces the system to capture the new image as the base during the next transformation call.

---

## Particle System: Core

### 1. RenParticlesFast

This is the main managing class, inherited from `SpriteManager`. It coordinates the lifecycle of all particles, calls behaviors, and manages rendering.

**Key Mechanisms:**

* **Creation Queue**: The `create()` method does not add the sprite to the main list immediately but places it in `particles_queue`. This ensures the stability of the iteration loop during updates.
* **Automatic Redraw**: If the `redraw` parameter is set, the system itself requests a redraw via `renpy.redraw`.
* **Time Management**: Using `delta` (the difference between the current and previous frame) ensures particle speed is independent of FPS.

**Main Methods:**

* `reset()`: Completely clears the system. Deletes all particles and clears their properties in `particles_properties`, returning the system to its initial state. It also resets all handlers and emitters. Handlers that were in `oneshotted_...` lists will be placed back into the processing block lists.
* `freeze() / unfreeze()`: Allows temporarily stopping logic updates (pause), preserving the current state of particles on the screen.

### 2. ParticlesData

A container object that stores the settings and state of a specific system.

```python
class ParticlesData:
    particles_properties = {}   # Dictionary: {particle_instance: {custom_data}}
    images = []                 # List of Displayables for spawning
    lifetime_type = None        # "constant" or "range-random"
    lifetime_timings = None     # Value or [min, max]

```

**Important for Developers:**
Use the `particles_properties` dictionary to store any particle-specific data (e.g., its current velocity vector or animation phase). When a particle dies, the system automatically clears this dictionary, preventing memory leaks.

---

## Multiple Systems

### 1. RenParticleFastGroup

This class allows combining several independent particle systems into a single `Displayable`. This is necessary for creating complex effects where different layers of particles (e.g., smoke, fire, and sparks) need to interact or be managed as a single unit.

**Architectural Features:**

* **ID Addressing**: Each system in the group can have a unique `system_id` for quick access.
* **Cross-cutting Contexts**: During initialization, the group passes references to all neighboring systems into the context (`RenpFContext`), allowing behaviors to "see" other systems.
* **Blit Rendering**: The group collects the renders of all subsystems and draws them via `subpixel_blit`.

### 2. Interaction Between Systems

Due to application of the `_TryGetOtherSystemMixin`, any behavior can access another system in the group by its ID.

**Scenario Example: Fragmentation**
When a particle in "System A" dies or reaches a certain condition, it can command "System B" to create a new particle at its coordinates.

```python
class RemoteSpawnBehavior(_UpdateBehavior):
    target_id = "sparks" # ID of the system where we will create the particle
    
    def __call__(self, context):
        # 1. Get access to the neighboring system via context
        target_system = self.get_system(context, self.target_id)
        
        if target_system:
            # 2. Create a particle in the target system
            new_spark = target_system.create(random.choice(target_system.particles_data.images))
            
            # 3. Pass coordinates from the current particle
            new_spark.x = context.particle.x
            new_spark.y = context.particle.y
            
        return UpdateState.Pass

```

**Contains methods `.freeze_one(id)` and `.unfreeze_one(id, redraw=True)`**: Freezes one of the subsystems by the passed `id`. If the subsystem with the `id` is not found, it does nothing.
> **Important Note**: You can freeze one of the subsystems. But be careful. If another subsystem creates particles in the frozen subsystem, the `.particles_queue` list accumulates, and upon unfreezing the subsystem, a stutter may occur if many particles have accumulated.

## Technical Reference: Execution Contexts

RenParticles uses a hierarchy of contexts to pass data into `__call__` methods:

1.  **`RenpFContext`**: Basic (system, time, delta, list of all systems).
2.  **`UpdateEmitterContext`**: Used by emitters (no current particle).
3.  **`EventContext`**: Contains event data (`event`, coordinates `x, y`).
4.  **`ParticleDeadContext`**: Passed to the `on_particle_dead` handler.

---

## Particle Transformations

### PropertyTween

Animation of Transform properties:

```python
class PropertyTween(_Behavior):
    property = None         # Property name
    time = 1.0             # Duration
    start_value = 0.0      # Start value
    end_value = 1.0        # End value
    warper = "linear"      # Interpolation function
    dynamic = None         # Dictionary of blocks
    
    mode = "absolute"      # Time calculation mode
    from_end = False       # Animation mode

```

**Available Warpers:**
- `linear`, `ease`, `easein`, `easeout`, `easeinout`
- `pause`, `bounce`, `spring`
- And others from `renpy.atl.warpers`

---

## Performance

### Rendering Optimization (standard RenPy code from `SpriteManager.render(...)`)

```python
# Fast rendering path (without complex effects)
cache.fast = (
    (r.forward is None) and
    (not r.mesh) and
    (not r.uniforms) and
    (not r.shaders) and
    (not r.properties) and
    (not r.xclipping) and
    (not r.yclipping)
)
```

### Optimization Tips

1.  **Use oneshot for emitters:**
```python
emitter spray oneshot:
    amount 100
```

2.  **Limit the update frequency:**
```python
redraw 0.016  # 60 FPS instead of maximum
```

3.  **Remove dead particles (if not using the `auto_expire` preset/handler):**
```python
class MyBehavior(_UpdateBehavior):
    def __call__(self, context):
        if context.particle.lifetime <= 0:
            context.particle.destroy()
        return UpdateState.Pass
```

4.  **Use caching:**
```python
rparticles as particles:
    cache  # Cache renders
```

---

## Debugging

### Output System Information

```python
system = renparticles._fast_particles_entries.get("my_particles")
if system:
    print(system.get_info())
```

Output:
```
========================================
PARTICLES DATA:
----------------------------------------
redraw: 0.0
images: [...]
lifetime_type: range-random
lifetime_timings: (1.0, 3.0)
----------------------------------------
ON UPDATE:
  • <Move object>
    velocity = [0.0, 100.0]
    acceleration = [0.0, 50.0]
----------------------------------------
...
```

### Checking Particle State

```python
class DebugBehavior(_UpdateBehavior):
    def __call__(self, context):
        particle = context.particle
        print(f"Particle at ({particle.x}, {particle.y}), lifetime: {particle.lifetime}")
        
        # Check particle data
        props = context.system.particles_data.particles_properties.get(particle, {})
        print(f"Particle data: {props}")
        
        return UpdateState.Pass
```

---

## Advanced Patterns

### Particle Pool

```python
class ParticlePool:
    def __init__(self, system, size=100):
        self.system = system
        self.pool = []
        self.active = []
        
        # Pre-create particles
        for i in range(size):
            sprite = system.create(system.particles_data.images[0])
            sprite.live = False
            self.pool.append(sprite)
    
    def acquire(self):
        if self.pool:
            sprite = self.pool.pop()
            sprite.live = True
            self.active.append(sprite)
            return sprite
        return None
    
    def release(self, sprite):
        sprite.live = False
        self.active.remove(sprite)
        self.pool.append(sprite)
```

### Behavior Chains

```python
class BehaviorChain(_UpdateBehavior):
    behaviors = _RequiredField()  # List of behaviors
    
    def __call__(self, context):
        for behavior in self.behaviors:
            result = behavior(context)
            if result == UpdateState.Kill:
                return UpdateState.Kill
        return UpdateState.Pass
```

### Conditional Behaviors

```python
class ConditionalBehavior(_UpdateBehavior):
    condition = _RequiredField()  # Condition function
    true_behavior = _RequiredField()
    false_behavior = None
    
    def __call__(self, context):
        if self.condition(context):
            return self.true_behavior(context)
        elif self.false_behavior:
            return self.false_behavior(context)
        return UpdateState.Pass
```

---

## API Reference

### Main Constants

```python
class UpdateState:
    Pass = 1000      # Continue
    Repeat = 2000    # Repeat (not used)
    Kill = 3000      # Remove the behavior

class BehaviorType:
    Function = 1500
    Emitter = 2500
```

### Utilities

```python
def _renp_lerp(start, end, t):
    """Linear interpolation"""
    return start + (end - start) * t

def _renp_clamp(value, min_value, max_value):
    """Clamp a value to a range"""
    return max(min_value, min(max_value, value))
```

### Access to Systems

```python
# Get a system by tag
system = renparticles._fast_particles_entries.get("my_tag")

# Get a model
model = renparticles._fast_particles_models.get("my_model")

# Get a shortcut
behavior_class = renparticles.static_shortcuts["behaviors"]["move"]
```

## Code Conventions

1.  **Naming:**
    - Classes: `PascalCase`
    - Functions/methods: `snake_case`
    - Constants: `UPPER_CASE`
    - Private fields: `_prefix`

2.  **Initialization Priorities:**
    - Base classes: `init -2448`
    - Engine: `init -1337`
    - Behaviors: `init -1115`
    - Shortcuts: `init -555`

3.  **Required Fields:**
```python
required_field = _RequiredField()
```

4.  **Unique Data Keys:**
```python
_MY_KEY = "_my_key"
_COUNTER = 0

def __init__(self):
    self._MY_KEY = f"{self._MY_KEY}_{self._COUNTER}"
    self._COUNTER += 1
```

## Implementation Examples

### Gravity

```python
init -1000 python in renparticles:
    class Gravity(_UpdateBehavior):
        strength = 500.0
        direction = [0.0, 1.0]  # Downwards
        
        _VELOCITY_KEY = "_gravity_vel"
        _COUNTER = 0
        
        def __init__(self):
            self._VELOCITY_KEY = f"{self._VELOCITY_KEY}_{self._COUNTER}"
            self._COUNTER += 1
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            props = context.system.particles_data.particles_properties
            
            particle_data = props.setdefault(particle, {})
            if self._VELOCITY_KEY not in particle_data:
                particle_data[self._VELOCITY_KEY] = [0.0, 0.0]
            
            vel = particle_data[self._VELOCITY_KEY]
            vel[0] += self.direction[0] * self.strength * delta
            vel[1] += self.direction[1] * self.strength * delta
            
            particle.x += vel[0] * delta
            particle.y += vel[1] * delta
            
            return UpdateState.Pass
```

### Boundary Collision

```python
class BoundsCollision(_UpdateBehavior):
    bounce_factor = 0.8
    
    _VELOCITY_KEY = "_bounds_vel"
    
    def __call__(self, context):
        particle = context.particle
        system = context.system
        props = context.system.particles_data.particles_properties
        
        particle_data = props.get(particle, {})
        vel = particle_data.get(self._VELOCITY_KEY, [0.0, 0.0])
        
        # Boundary check
        if particle.x < 0:
            particle.x = 0
            vel[0] = abs(vel[0]) * self.bounce_factor
        elif particle.x > system.width:
            particle.x = system.width
            vel[0] = -abs(vel[0]) * self.bounce_factor
        
        if particle.y < 0:
            particle.y = 0
            vel[1] = abs(vel[1]) * self.bounce_factor
        elif particle.y > system.height:
            particle.y = system.height
            vel[1] = -abs(vel[1]) * self.bounce_factor
        
        return UpdateState.Pass
```

### Target Following

```python
class FollowTarget(_UpdateBehavior):
    target_pos = _RequiredField()  # [x, y] or a function
    speed = 100.0
    
    def __call__(self, context):
        particle = context.particle
        delta = context.delta
        
        # Get target position
        if callable(self.target_pos):
            tx, ty = self.target_pos()
        else:
            tx, ty = self.target_pos
        
        # Direction to target
        dx = tx - particle.x
        dy = ty - particle.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            # Normalize and apply speed
            nx = dx / dist
            ny = dy / dist
            
            particle.x += nx * self.speed * delta
            particle.y += ny * self.speed * delta
        
        return UpdateState.Pass
```

This documentation covers the basics of extending RenParticles. For more complex cases, study the source code of existing behaviors in the `Particles Implementation` directory.