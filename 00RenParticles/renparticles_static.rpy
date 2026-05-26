# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1337 python in renparticles:
    from builtins import min, max
    from renpy.store import persistent


    _fast_particles_entries = { }
    _fast_particles_models = { }

    _particles_pool = RenParticlesPool()
    _particles_pool.reserve()
    _debug_stats = False

    persistent._RENP_DEFAULT_PREFERENCES = {
        "transform_acceleration": False,
        "update_acceleration": False,
        "update_fidelity": 1,

        "particles_listening_events": False,
        "acceleration_target_fps": 60,
        "acceleration_root_fps": 60.0
    }

    def get_default_system_parameter(key):
        if key not in persistent._RENP_DEFAULT_PREFERENCES:
            available_keys = ", ".join(persistent._RENP_DEFAULT_PREFERENCES.keys())
            
            error_msg = "parameter '{}' not found in _RENP_DEFAULT_PREFERENCES.\navailable parameters: {}.\nplease ensure that you have added '{}' to the default configuration.".format(
                key, 
                available_keys, 
                key
            )
            
            renpy.error(error_msg)

        return persistent._RENP_DEFAULT_PREFERENCES[key]

    def set_default_system_parameter(key, value):
        if key not in persistent._RENP_DEFAULT_PREFERENCES:
            available_keys = ", ".join(persistent._RENP_DEFAULT_PREFERENCES.keys())
            renpy.error("attempted to set an unknown parameter '{}'.\navailable parameters: {}.".format(
                key, 
                available_keys
            ))

        #<Ебанутая хуйня. Только попробуйте напрямую поменять значение. За вами придёт ебака и трахнет вас>#
        #<Впадлу переделывать прост>#
        expected_type = type(persistent._RENP_DEFAULT_PREFERENCES[key])

        if expected_type == float and isinstance(value, int):
            value = float(value)
        elif not isinstance(value, expected_type):
            renpy.error("invalid type for parameter '{}'.\nexpected: {}, got: {}.".format(
                key, 
                expected_type.__name__, 
                type(value).__name__
            ))

        persistent._RENP_DEFAULT_PREFERENCES[key] = value

    def enable_debug_stats(state=True):
        global _debug_stats
        
        _debug_stats = state

    def add_shortcut(tag, behavior, is_emitter=False):
        if not issubclass(behavior, _Behavior):
            error_msg = (
                "TypeError in add_shortcut(): expected subclass of _Behavior, "
                "got {} instead. Tag: '{}', is_emitter: {}"
            ).format(type(behavior), tag, is_emitter)
            renpy.error(error_msg)

        emitter_or_behavior = "behaviors" if not is_emitter else "emitters"
        
        if tag in dynamic_shortcuts[emitter_or_behavior]:
            warn_msg = (
                "shortcut tag '{}' already exists in {}. "
                "old: {}, new: {}"
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
                "TypeError in add_preset(): expected subclass of _RFDynamicBehaviorPreset or _RFBehaviorPreset, "
                "got {} instead. Tag: '{}', preset_type: '{}'"
            ).format(type(preset_behavior), tag, preset_type)
            renpy.error(error_msg)
        
        if preset_type not in dynamic_shortcuts["presets"]:
            error_msg = (
                "KeyError in add_preset(): invalid preset_type '{}'. "
                "valid types: {}"
            ).format(preset_type, ", ".join(dynamic_shortcuts["presets"].keys()))
            renpy.error(error_msg)
        
        if tag in dynamic_shortcuts["presets"][preset_type]:
            warn_msg = (
                "preset tag '{}' already exists in '{}' presets. "
                "old: {}, new: {}"
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
