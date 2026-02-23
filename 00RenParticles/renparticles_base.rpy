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

        def inject_properties(self, **properties):
            self.m_properties = { }
            for key, value in properties.items():
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
