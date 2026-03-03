# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1337 python in renparticles:
    from builtins import min, max


    _fast_particles_entries = { }
    _fast_particles_models = { }

    _particles_pool = RenParticlesPool()
    _particles_pool.reserve()
    _pool_stats = False

    def add_shortcut(tag, behavior, is_emitter=False):
        if not issubclass(behavior, _Behavior):
            error_msg = (
                "TypeError in add_shortcut(): Expected subclass of _Behavior, "
                "got {} instead. Tag: '{}', is_emitter: {}"
            ).format(type(behavior), tag, is_emitter)
            renpy.error(error_msg)

        emitter_or_behavior = "behaviors" if not is_emitter else "emitters"
        
        if tag in dynamic_shortcuts[emitter_or_behavior]:
            warn_msg = (
                "Warning: Shortcut tag '{}' already exists in {}. "
                "Old: {}, New: {}"
            ).format(
                tag,
                emitter_or_behavior,
                dynamic_shortcuts[emitter_or_behavior][tag].__name__,
                behavior.__name__
            )
            renpy.error(warn_msg)
        
        dynamic_shortcuts[emitter_or_behavior][tag] = behavior

    def add_preset(tag, preset_behavior, preset_type="general"):
        if not isinstance(preset_behavior, (_RFDynamicBehaviorPreset, _RFBehaviorPreset)):
            error_msg = (
                "TypeError in add_preset(): Expected subclass of _RFDynamicBehaviorPreset or _RFBehaviorPreset, "
                "got {} instead. Tag: '{}', preset_type: '{}'"
            ).format(type(preset_behavior), tag, preset_type)
            renpy.error(error_msg)
        
        if preset_type not in dynamic_shortcuts["presets"]:
            error_msg = (
                "KeyError in add_preset(): Invalid preset_type '{}'. "
                "Valid types: {}"
            ).format(preset_type, ", ".join(dynamic_shortcuts["presets"].keys()))
            renpy.error(error_msg)
        
        if tag in dynamic_shortcuts["presets"][preset_type]:
            warn_msg = (
                "Warning: Preset tag '{}' already exists in '{}' presets. "
                "Old: {}, New: {}"
            ).format(
                tag,
                preset_type,
                dynamic_shortcuts["presets"][preset_type][tag].__name__,
                preset_behavior.__name__
            )
            renpy.error(warn_msg)
        
        dynamic_shortcuts["presets"][preset_type][tag] = preset_behavior

    def instantiate_model(tag):
        model = _fast_particles_models.get(tag, None)
        if model is None:
            renpy.error("there is no model named '{}'\navailable models: {}".format(tag, ",".join(_fast_particles_models.keys())))
        return renpy.store._renp_instantiate_system_displayable(model)

    def _renp_lerp(start, end, t):
        return start + (end - start) * t

    def _renp_clamp(value, min_value, max_value):
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        
        return max(min_value, min(max_value, value))
