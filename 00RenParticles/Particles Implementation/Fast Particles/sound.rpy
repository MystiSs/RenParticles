# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    class PlaySound(_Behavior):
        file = _RequiredField()
        loop = False
        fadein = 0
        fadeout = None
        volume = 1.0
        channel = "audio"

        _check_is_valid = True
        _valid = { "file", "channel", "loop", "fadein", "fadeout", "volume" }

        def __call__(self, context):
            renpy.music.play(self.file, self.channel, self.loop, self.fadeout, fadein=self.fadein, relative_volume=self.volume)

            return UpdateState.Pass
