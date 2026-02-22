init -1337 python in renparticles:
    class Emitter(_Behavior):
        def __call__(self, context):
            raise NotImplementedError("Emitter base class must be implemented")