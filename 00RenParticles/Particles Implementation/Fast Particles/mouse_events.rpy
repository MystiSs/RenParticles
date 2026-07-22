# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.

init -1115 python in renparticles:
    import pygame

    _MouseEventButtonDown = pygame.MOUSEBUTTONDOWN
    _MouseButtonLeft = 1
    _MouseButtonRight = 3
    _MouseEventMotion = pygame.MOUSEMOTION
    _MouseEventAllowedModes = { "lmb", "rmb", "move" }

    class MouseEvent(_EventBehavior):
        mode = "lmb" # "lmb" | "rmb" | "move"
        function = None # Сигнатура: function(context, behavior) , но может быть списком#

        _button_down_map = {
            "lmb": _MouseButtonLeft,
            "rmb": _MouseButtonRight,
        }

        _normalized = False
        
        _check_is_valid = True
        _valid = {"mode", "function"}

        def _normalize_functions(self):
            if self.function is None:
                self.function = []
            
            if isinstance(self.function, (list, tuple)):
                self.function = [func for func in self.function if func is not None]
            else:
                self.function = [self.function]
            
            self._normalized = True

        def _call_callbacks(self, context, behavior):
            if not self._normalized:
                self._normalize_functions()

            for callback in self.function:
                callback(context, self)

        def _log_invalid_context_error(self, context):
            error_msg = (
                "Invalid context type for MouseEvent: {}\n"
                "Expected: EventContext\n"
                "This usually happens when the event handler is attached to the wrong callback type.\n"
                "Context details: {}".format(
                    type(context).__name__,
                    str(context) if context else "None"
                )
            )
            renpy.error(error_msg)

        def _log_invalid_mode_error(self):
            error_msg = (
                "Invalid mode for MouseEvent: '{}'\n"
                "Allowed modes: {}\n"
                "Check that the mode is correctly specified when creating the MouseEvent instance.".format(
                    self.mode,
                    ", ".join(_MouseEventAllowedModes) if _MouseEventAllowedModes else "None"
                )
            )
            renpy.error(error_msg)

        def __call__(self, context):
            if not isinstance(context, EventContext):
                self._log_invalid_context_error(context)
                return UpdateState.Pass
            
            if self.mode not in _MouseEventAllowedModes:
                self._log_invalid_mode_error()
                return UpdateState.Pass

            if self.function is None:
                return UpdateState.Pass

            self._normalize_functions()

            event = context.event
            if event == _MouseEventButtonDown and event.button == MouseEvent._button_down_map.get(self.mode, None):
                self._call_callbacks(context, self)
            elif event == _MouseEventMotion and self.mode == "move":
                self._call_callbacks(context, self)
            
            return UpdateState.Pass
