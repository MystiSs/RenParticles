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
        def inject_properties(self, **properties):
            for key, value in properties.items():
                setattr(self, key, value)

    class _UpdateBehavior(_InjectPropertiesMixin):
        def __call__(self, st, manager):
            raise NotImplementedError("_UpdateBehavior base class must be implemented")

    class _EventBehavior(_InjectPropertiesMixin):
        def __call__(self, ev, x, y, st, manager):
            raise NotImplementedError("_EventBehavior base class must be implemented")

    class _OnDeadBehavior(_InjectPropertiesMixin):
        def __call__(self, particle, st, manager):
            raise NotImplementedError("_EventBehavior base class must be implemented")
