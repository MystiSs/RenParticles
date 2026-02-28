# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1337 python in renparticles:
    class Emitter(_Behavior):
        def __call__(self, context):
            raise NotImplementedError("Emitter base class must be implemented")