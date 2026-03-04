# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -2448 python in renparticles:
    class BehaviorType:
        Function = 1500
        Emitter = 2500

    class UpdateState:
        Pass = 1000
        Repeat = 2000
        Kill = 3000
    
    class _Properties:
        pass

    class _InjectPropertiesMixin:
        m_properties = None
        _renp_always = { "oneshot", "renp_behavior_id", "renp_target_system" }
        _valid = set()
        _check_is_valid = False

        def inject_properties(self, **properties):
            self.m_properties = {}
            valid = self._valid.union(self._renp_always)
            
            for key, value in properties.items():
                if self._check_is_valid and key not in valid:
                    renpy.error("invalid property '{}' for {}\nlist of acceptable properties: {}".format(key, type(self), ", ".join(valid)))

                if key == "dynamic" and hasattr(self, "dynamic") and self.dynamic is not None:
                    self.dynamic.update(value)
                else:
                    setattr(self, key, value)
                    self.m_properties[key] = value

    class _RequiredField(object):
        pass

    class _CheckInitialisedMixin:
        def check_initialised(self):
            uninitialised = set()
            for attr_name in dir(self):
                if attr_name.startswith('_'):
                    continue
                    
                for attr_name, cls_val in self.__class__.__dict__.items():
                    if isinstance(cls_val, _RequiredField):
                        if isinstance(getattr(self, attr_name, None), _RequiredField):
                            uninitialised.add(attr_name)
            
            if uninitialised:
                raise ValueError(
                    "The following required fields are not initialized: {}".format(
                        ", ".join(uninitialised)
                    )
                )
            return True

    class _TryGetOtherSystemMixin:
        renp_target_system = None

        def get_system(self, context, id=None):
            if id is None:
                return context.system
            return context.systems.get(id, None)

    class _Behavior(_InjectPropertiesMixin, _CheckInitialisedMixin, _TryGetOtherSystemMixin):
        def __call__(self, context):
            raise NotImplementedError("_Behavior base class must be implemented")

    class _UpdateBehavior(_Behavior):
        def __call__(self, context):
            raise NotImplementedError("_UpdateBehavior base class must be implemented")

    class _EventBehavior(_Behavior):
        def __call__(self, context):
            raise NotImplementedError("_EventBehavior base class must be implemented")

    class _OnDeadBehavior(_Behavior):
        def __call__(self, context):
            raise NotImplementedError("_EventBehavior base class must be implemented")

