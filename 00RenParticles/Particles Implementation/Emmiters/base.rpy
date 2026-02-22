init -1337 python in renparticles:
    class Emitter(_UpdateBehavior):
        def __call__(self, st, manager):
            raise NotImplementedError("Emitter base class must be implemented")

    class EventEmitter(_EventBehavior):
        def __call__(self, ev, x, y, st, manager):
            raise NotImplementedError("EventEmitter base class must be implemented")

    class DeadEmitter(_OnDeadBehavior):
        def __call__(self, particle, st, manager):
            raise NotImplementedError("OnDeadEmitter base class must be implemented")