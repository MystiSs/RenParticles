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

    class _RequiredField(object):
        pass

    class _CheckInitialisedMixin:
        def check_initialised(self):
            uninitialised = []
            for attr_name in dir(self):
                if attr_name.startswith('_'):
                    continue
                    
                cls_val = getattr(self.__class__, attr_name, None)
                if isinstance(cls_val, _RequiredField):
                    if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
                        uninitialised.append(attr_name)
            
            if uninitialised:
                raise ValueError(
                    "The following required fields are not initialized: {}".format(
                        ", ".join(uninitialised)
                    )
                )
            return True

    class _Behavior(_InjectPropertiesMixin, _CheckInitialisedMixin):
        def __call__(self, context):
            raise NotImplementedError("_Behavior base class must be implemented")

    class _UpdateBehavior(_InjectPropertiesMixin, _CheckInitialisedMixin):
        def __call__(self, context):
            raise NotImplementedError("_UpdateBehavior base class must be implemented")

    class _EventBehavior(_InjectPropertiesMixin, _CheckInitialisedMixin):
        def __call__(self, context):
            raise NotImplementedError("_EventBehavior base class must be implemented")

    class _OnDeadBehavior(_InjectPropertiesMixin, _CheckInitialisedMixin):
        def __call__(self, context):
            raise NotImplementedError("_EventBehavior base class must be implemented")
