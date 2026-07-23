# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.


python early:
    import re


    class _RenParserType:
        Func = 333
        Shortcut = 666
        Emitter = 999

        GeneralPreset = 1332
        InnerPreset = 1665

        System = 8888
        SubSystem = 9999

        PresetsTypes = (GeneralPreset, InnerPreset)

    class _RenPLexerKeywords:
        # Ключевые слова показа
        ONLAYER = "onlayer"
        ZORDER = "zorder"
        MULTIPLE = "multiple"
        WITH = "with"
        AS = "as"
        MODEL = "model"
        
        # Ключевые слова системы
        SYSTEM = "system"
        SUBSYSTEM_ID = "id"
        TARGET_SYSTEM = "system"
        REDRAW = "redraw"
        NOREDRAW = "noredraw"
        CACHE = "cache"
        DEEP = "deep"
        
        # Ключевые слова пресетов
        PRESET = "preset"
        PRESET_TYPE = "type"
        
        # Ключевые слова событий
        ON_UPDATE = "on update"
        ON_EVENT = "on event"
        ON_PARTICLE_DEAD = "on particle dead"
        ON_PARTICLE_APPEAR = "on particle appear"
        
        # Ключевые слова поведения
        ONESHOT = "oneshot"
        BEHAVIOR_ID = "id"
        EMITTER = "emitter"
        CUSTOM = "custom"
        IF_CONDITION = "if"
        
        # Ключевые слова для значений
        RANDOM = "random"
        RANGE = "range"
        CONSTANT = "constant"
        
        # Ключевые слова ускорения
        TRANSFORM_ACCELERATION = "accelerate transforming"
        UPDATE_ACCELERATION = "accelerate update"
        ACCELERATION_TARGET_FPS = "acceleration target fps"
        UPDATE_FIDELITY = "update fidelity"
        PARTICLE_EVENT_LISTENING = "particles listening events"
        
        # Ключевые слова симуляции
        SIMULATE_TIME = "simulate_time"
        SIMULATE_WAIT = "wait"
        SIMULATE_WAIT_STEP = "simulate_wait_step"
        
        # Ключевые слова свойств
        PROP_BLOCK = "block"
        
        # Типы времени жизни
        LIFETIME_CONSTANT = "constant"
        LIFETIME_RANGE_RANDOM = "range-random"

    class _RenPKeys:
        # Базовые ключи системы
        TAG = "tag"
        LAYER = "layer"
        ZORDER = "zorder"
        MULTIPLE = "multiple"
        REDRAW = "redraw"
        WITH = "with"
        
        # Ключи системы
        SUBSYSTEMS = "subsystems"
        SYSTEM_ID = "system_id"
        TYPE = "type"
        PRESETS = "presets"
        LIFETIME = "lifetime"

        SPRITE = "sprite"
        IMAGES = "images"
        CACHE = "cache"

        # Время жизни
        TIMINGS = "timings"
        
        # Ключи событий
        ON_UPDATE = "on_update"
        ON_EVENT = "on_event"
        ON_PARTICLE_DEAD = "on_particle_dead"
        ON_PARTICLE_APPEAR = "on_particle_appear"
        
        # Ключи поведения
        FUNC = "func"
        BEHAVIORS = "behaviors"
        ONESHOT = "oneshot"
        BEHAVIOR_ID = "renp_behavior_id"
        TARGET_SYSTEM = "renp_target_system"
        PROPERTIES = "properties"
        CONDITION = "m_renp_condition"
        
        # Ключи шорткатов
        SHORTCUT = "shortcut"
        SHORTCUTS_BLOCK = "shortcuts_block"
        GENERAL_SHORTCUTS = "general"
        INNER_SHORTCUTS = "inner"
        
        # Ключи моделей
        MODEL_NAME = "model_name"
        REDEFINITION = "redefinition"
        PRESET_NAME = "preset_name"
        PRESET_TYPE = "preset_type"
        PRESET_DEFINE_DATA = "preset_define_data"
        
        # Ключи ускорения
        TRANSFORM_ACCELERATION = "transform_acceleration"
        UPDATE_ACCELERATION = "update_acceleration"
        ACCELERATION_TARGET_FPS = "acceleration_target_fps"
        UPDATE_FIDELITY = "update_fidelity"
        PARTICLE_EVENT_LISTENING = "particles_listening_events"
        
        # Ключи симуляции
        SIMULATE_TIME = "simulate_time"
        SIMULATE_WAIT = "wait"
        SIMULATE_WAIT_STEP = "simulate_wait_step"
        
        # Специальные ключи
        BASE_NAME = "rparticles_displayable"
        POSSIBLE = "possible"
        PROPERTIES_DYNAMIC = "dynamic"

    class _RenPLifetime:
        Constant = "constant"
        RangeRandom = "range-random"

    class _RenPConditionCache:
        _cache = {}

        @classmethod
        def get(cls, source):
            if source not in cls._cache:
                cls._cache[source] = renpy.python.py_compile(source, "eval")
            return cls._cache[source]
        
        @classmethod
        def eval_fast(cls, source):
            if source not in cls._cache:
                cls._cache[source] = renpy.python.py_compile(source, "eval")
            return renpy.python.py_eval_bytecode(cls._cache[source])

    REDRAW_ASAP_ALIASES = {"asap", "fastest", "fast"}
    RENPY_RESERVED_WORDS = {"move", "dissolve", "dspr"}
    BASE_LAYER = "master"
    BASE_ZORDER = "0"
    BASE_REDRAW = "None"
    BASE_TRANSITION = "None"

    RENP_PRESET_DEFAULT_TYPE = "general"

    #-------------------FACTORIES---------------------

    def _renp_create_base_data_dict():
        return {
            _RenPKeys.TAG: None,
            _RenPKeys.LAYER: BASE_LAYER,
            _RenPKeys.ZORDER: BASE_ZORDER,
            _RenPKeys.MULTIPLE: False,
            _RenPKeys.SUBSYSTEMS: [],
            _RenPKeys.REDRAW: BASE_REDRAW,
            _RenPKeys.WITH: BASE_TRANSITION,
            _RenPKeys.MODEL_NAME: None,
            _RenPKeys.REDEFINITION: None,
        }

    def _renp_create_system_data(system_type=_RenParserType.System):
        return {
            _RenPKeys.PRESETS: [],
            _RenPKeys.ON_UPDATE: [],
            _RenPKeys.ON_EVENT: [],
            _RenPKeys.ON_PARTICLE_DEAD: [],
            _RenPKeys.ON_PARTICLE_APPEAR: [],
            _RenPKeys.IMAGES: [],
            _RenPKeys.LIFETIME: None,
            _RenPKeys.TYPE: system_type,
        }

    def _renp_create_lifetime_data():
        return {
            _RenPKeys.TYPE: None,
            _RenPKeys.TIMINGS: None,
        }

    def _renp_create_show_data():
        return {
            _RenPKeys.TAG: None,
            _RenPKeys.LAYER: BASE_LAYER,
            _RenPKeys.ZORDER: BASE_ZORDER,
        }

    def _renp_create_preset_define_data():
        return {
            _RenPKeys.PRESET_NAME: None,
            _RenPKeys.PRESET_TYPE: RENP_PRESET_DEFAULT_TYPE,
            _RenPKeys.PRESET_DEFINE_DATA: {},
        }

    def _renp_create_shortcut_properties():
        return {
            _RenPKeys.ONESHOT: "False",
            _RenPKeys.BEHAVIOR_ID: None,
            _RenPKeys.TARGET_SYSTEM: None,
            _RenPKeys.CONDITION: "True",
        }

    def _renp_create_show_component_keys():
        return {
            _RenPKeys.TAG,
            _RenPKeys.LAYER,
            _RenPKeys.ZORDER,
        }

    def _renp_create_system_content_flags():
        return {
            _RenPKeys.SPRITE: False,
            _RenPKeys.LIFETIME: False,
            _RenPKeys.ON_UPDATE: False,
            _RenPKeys.ON_EVENT: False,
            _RenPKeys.ON_PARTICLE_DEAD: False,
            _RenPKeys.ON_PARTICLE_APPEAR: False,
            _RenPKeys.REDRAW: False,
            _RenPKeys.CACHE: False,
            _RenPKeys.TRANSFORM_ACCELERATION: False,
            _RenPKeys.UPDATE_ACCELERATION: False,
            _RenPKeys.UPDATE_FIDELITY: False,
            _RenPKeys.ACCELERATION_TARGET_FPS: False,
            _RenPKeys.PARTICLE_EVENT_LISTENING: False,
        }

    def _renp_create_preset_block_flags():
        return {
            _RenPKeys.ON_UPDATE: False,
            _RenPKeys.ON_EVENT: False,
            _RenPKeys.ON_PARTICLE_DEAD: False,
            _RenPKeys.ON_PARTICLE_APPEAR: False,
        }

    def _renp_create_simulate_data():
        return {
            _RenPKeys.TAG: None,
            _RenPKeys.SIMULATE_TIME: "None",
            _RenPKeys.SIMULATE_WAIT: False,
            _RenPKeys.SIMULATE_WAIT_STEP: "None",
        }

    def _renp_create_continue_data():
        return {
            _RenPKeys.TAG: None,
            _RenPKeys.LAYER: None,
            _RenPKeys.ZORDER: "0",
            _RenPKeys.WITH: "None",
        }

    def _renp_create_freeze_data():
        return {
            _RenPKeys.TAG: None,
            _RenPKeys.SYSTEM_ID: None,
        }

    def _renp_create_unfreeze_data():
        return {
            _RenPKeys.TAG: None,
            _RenPKeys.SYSTEM_ID: None,
            _RenPKeys.REDRAW: True,
        }

    def _renp_create_reset_data():
        return {
            _RenPKeys.TAG: None,
        }

    def _renp_create_clear_cache_data():
        return {
            _RenPLexerKeywords.DEEP: False,
        }
    
    def _renp_create_define_particles_data():
        return {
            _RenPKeys.MODEL_NAME: None,
            _RenPKeys.MULTIPLE: False,
            _RenPKeys.SUBSYSTEMS: [],
            _RenPKeys.REDRAW: BASE_REDRAW
        }

    #-------------------FACTORIES---------------------

    #-------------------PARSERS---------------------

    def _renp_is_show_component_keyword(lexer):
        """Проверяет, является ли текущее ключевое слово компонентом показа."""
        return (lexer.keyword(_RenPLexerKeywords.AS) or
                lexer.keyword(_RenPLexerKeywords.ONLAYER) or
                lexer.keyword(_RenPLexerKeywords.ZORDER))

    def _renp_parse_show_component(lexer):
        """Парсит один компонент показа."""
        data = {}
        
        if lexer.keyword(_RenPLexerKeywords.AS):
            data[_RenPKeys.TAG] = lexer.image_name_component()
        elif lexer.keyword(_RenPLexerKeywords.ONLAYER):
            data[_RenPKeys.LAYER] = lexer.simple_expression()
        elif lexer.keyword(_RenPLexerKeywords.ZORDER):
            data[_RenPKeys.ZORDER] = lexer.simple_expression()
        
        return data

    def _renp_parse_show_components(lexer, data):
        seen_with = False
        while not lexer.match(':') and not lexer.eol():
            if _renp_is_show_component_keyword(lexer):
                data.update(_renp_parse_show_component(lexer))
            elif lexer.keyword(_RenPLexerKeywords.MULTIPLE):
                data[_RenPKeys.MULTIPLE] = True
            elif lexer.keyword(_RenPLexerKeywords.WITH):
                if seen_with:
                    lexer.error("there can only be one 'with' statement")
                seen_with = True
                data[_RenPKeys.WITH] = lexer.simple_expression()
            else:
                break
        return data

    def _renp_parse_redraw(lexer, was_redraw=False):
        if was_redraw:
            renpy.error("there can be only one 'redraw' instruction")
        
        for alias in REDRAW_ASAP_ALIASES:
            if lexer.keyword(alias):
                return "0.0"
        return lexer.float()

    def _renp_parse_sprites(lexer):
        data = []
        images = [img.strip() for img in lexer.rest().split(';')]
        expr_pattern = re.compile(r'^(expression|expr)\s+(.*)$')
        
        for image in images:
            match = expr_pattern.match(image)
            if match:
                data.append((match.group(2), True))
            else:
                data.append((image, False))
        
        return data

    def _renp_parse_lifetime(lexer):
        data = _renp_create_lifetime_data()

        if lexer.keyword(_RenPLexerKeywords.RANGE):
            if lexer.keyword(_RenPLexerKeywords.RANDOM):
                data[_RenPKeys.TYPE] = _RenPLifetime.RangeRandom
                data[_RenPKeys.TIMINGS] = lexer.simple_expression()
        elif lexer.keyword(_RenPLexerKeywords.CONSTANT):
            data[_RenPKeys.TYPE] = _RenPLifetime.Constant
            data[_RenPKeys.TIMINGS] = lexer.simple_expression()
        else:
            lexer.error("expected '{}' or '{}'".format(_RenPLexerKeywords.LIFETIME_RANGE_RANDOM, _RenPLexerKeywords.LIFETIME_CONSTANT))

        return data

    def _renp_parse_properties(lexer, allow_dynamic=True):
        properties = {}
        prop_blocks = {}
        properties_block = lexer.subblock_lexer()

        while properties_block.advance():
            if allow_dynamic and properties_block.keyword(_RenPLexerKeywords.PROP_BLOCK):
                prop_name = properties_block.string()
                properties_block.require(':')
                properties_block.expect_eol()
                prop_blocks[prop_name] = _renp_parse_properties(properties_block, False)
            else:
                key = properties_block.word()
                value = properties_block.simple_expression()
                properties[key] = value
        
        if prop_blocks:
            properties[_RenPKeys.PROPERTIES_DYNAMIC] = prop_blocks

        return properties

    def _renp_parse_common_behavior(lexer, expect_eol=True, **kwargs):
        """Парсит общую часть поведения (custom или shortcut)"""
        allow_oneshot = kwargs.get("allow_oneshot", True)
        allow_target_system = kwargs.get("allow_target_system", True)
        allow_properties = kwargs.get("allow_properties", True)
        is_custom = kwargs.get("is_custom", False)
        
        if is_custom:
            func = lexer.simple_expression()
            result = {_RenPKeys.FUNC: func, _RenPKeys.TYPE: _RenParserType.Func}
        else:
            shortcut = lexer.word()
            shortcut_block = kwargs.get('shortcut_block', _RenPKeys.BEHAVIORS)
            result = {
                _RenPKeys.SHORTCUT: shortcut,
                _RenPKeys.SHORTCUTS_BLOCK: shortcut_block,
                _RenPKeys.TYPE: _RenParserType.Shortcut,
            }
        
        properties = _renp_create_shortcut_properties()
        seen = {key: False for key in properties.keys()}
        
        was_delim = False
        while not lexer.eol():
            if allow_oneshot and lexer.keyword(_RenPLexerKeywords.ONESHOT):
                if seen[_RenPKeys.ONESHOT]:
                    lexer.error("only one 'oneshot' instruction allowed")
                properties[_RenPKeys.ONESHOT] = "True"
                seen[_RenPKeys.ONESHOT] = True
                
            elif allow_target_system and lexer.keyword(_RenPLexerKeywords.TARGET_SYSTEM):
                if seen[_RenPKeys.TARGET_SYSTEM]:
                    lexer.error("only one 'system' instruction allowed")
                properties[_RenPKeys.TARGET_SYSTEM] = lexer.string()
                seen[_RenPKeys.TARGET_SYSTEM] = True
                
            elif lexer.keyword(_RenPLexerKeywords.BEHAVIOR_ID):
                if seen[_RenPKeys.BEHAVIOR_ID]:
                    lexer.error("only one behavior 'id' instruction allowed")
                properties[_RenPKeys.BEHAVIOR_ID] = lexer.string()
                seen[_RenPKeys.BEHAVIOR_ID] = True

            elif lexer.keyword(_RenPLexerKeywords.IF_CONDITION):
                if seen[_RenPKeys.CONDITION]:
                    lexer.error("only one behavior 'if' instruction allowed")
                properties[_RenPKeys.CONDITION] = lexer.string()
                seen[_RenPKeys.CONDITION] = True
                
            elif lexer.match(':'):
                lexer.expect_eol()
                was_delim = True
                break
            else:
                break
        
        if allow_properties and was_delim:
            properties.update(_renp_parse_properties(lexer))
        
        if expect_eol:
            lexer.expect_eol()
        
        result[_RenPKeys.PROPERTIES] = properties
        return result

    def _renp_parse_custom(lexer, **kwargs):
        return _renp_parse_common_behavior(lexer, is_custom=True, **kwargs)

    def _renp_parse_shortcut(lexer, shortcut_block=_RenPKeys.BEHAVIORS, **kwargs):
        return _renp_parse_common_behavior(lexer, is_custom=False, shortcut_block=shortcut_block, **kwargs)

    def _renp_parse_preset(lexer, preset_type=_RenParserType.GeneralPreset):
        result = _renp_parse_shortcut(lexer, _RenPKeys.PRESETS, allow_oneshot=False)
        result[_RenPKeys.TYPE] = preset_type
        return result

    def _renp_parse_emitter(lexer):
        if lexer.keyword(_RenPLexerKeywords.CUSTOM):
            return _renp_parse_custom(lexer)
        return _renp_parse_shortcut(lexer, "emitters")

    #----------------------------------------

    def _renp_parse_on_block(lexer):
        block_data = []
        
        lexer.require(':')
        on_block = lexer.subblock_lexer()

        while on_block.advance():
            if on_block.keyword(_RenPLexerKeywords.EMITTER):
                block_data.append(_renp_parse_emitter(on_block))
            elif on_block.keyword(_RenPLexerKeywords.PRESET):
                block_data.append(_renp_parse_preset(on_block, _RenParserType.InnerPreset))
            elif on_block.keyword(_RenPLexerKeywords.CUSTOM):
                block_data.append(_renp_parse_custom(on_block))
            else:
                block_data.append(_renp_parse_shortcut(on_block))
            
            on_block.expect_eol()
        
        return block_data

    def _renp_parse_system_content(lexer, data):
        seen = _renp_create_system_content_flags()
        system_type = data.get(_RenPKeys.TYPE, _RenParserType.System)

        while lexer.advance():
            if lexer.keyword(_RenPKeys.REDRAW):
                if seen[_RenPKeys.REDRAW]:
                    lexer.error("only one 'redraw' instruction allowed")
                data[_RenPKeys.REDRAW] = _renp_parse_redraw(lexer)
                seen[_RenPKeys.REDRAW] = True

            elif lexer.keyword(_RenPKeys.CACHE):
                if seen[_RenPKeys.CACHE]:
                    lexer.error("only one 'cache' instruction allowed")
                data[_RenPKeys.CACHE] = "True"
                seen[_RenPKeys.CACHE] = True
                lexer.expect_eol()

            elif lexer.keyword(_RenPKeys.SPRITE):
                if seen[_RenPKeys.SPRITE]:
                    lexer.error("only one 'sprite' instruction allowed")
                data[_RenPKeys.IMAGES] = _renp_parse_sprites(lexer)
                seen[_RenPKeys.SPRITE] = True
            
            elif lexer.keyword(_RenPKeys.LIFETIME):
                if seen[_RenPKeys.LIFETIME]:
                    lexer.error("only one 'lifetime' instruction allowed")
                data[_RenPKeys.LIFETIME] = _renp_parse_lifetime(lexer)
                seen[_RenPKeys.LIFETIME] = True

            elif lexer.keyword(_RenPLexerKeywords.PRESET):
                data[_RenPKeys.PRESETS].append(_renp_parse_preset(lexer))

            elif lexer.match(_RenPLexerKeywords.ON_UPDATE):
                if seen[_RenPKeys.ON_UPDATE]:
                    lexer.error("only one 'on update' block allowed")
                data[_RenPKeys.ON_UPDATE] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_UPDATE] = True

            elif lexer.match(_RenPLexerKeywords.ON_EVENT):
                if seen[_RenPKeys.ON_EVENT]:
                    lexer.error("only one 'on event' block allowed")
                data[_RenPKeys.ON_EVENT] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_EVENT] = True

            elif lexer.match(_RenPLexerKeywords.ON_PARTICLE_DEAD):
                if seen[_RenPKeys.ON_PARTICLE_DEAD]:
                    lexer.error("only one 'on particle dead' block allowed")
                data[_RenPKeys.ON_PARTICLE_DEAD] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_PARTICLE_DEAD] = True

            elif lexer.match(_RenPLexerKeywords.ON_PARTICLE_APPEAR):
                if seen[_RenPKeys.ON_PARTICLE_APPEAR]:
                    lexer.error("only one 'on particle appear' block allowed")
                data[_RenPKeys.ON_PARTICLE_APPEAR] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_PARTICLE_APPEAR] = True

            elif lexer.match(_RenPLexerKeywords.TRANSFORM_ACCELERATION):
                if seen[_RenPKeys.TRANSFORM_ACCELERATION]:
                    lexer.error("only one 'accelerate transforming' instruction allowed")
                data[_RenPKeys.TRANSFORM_ACCELERATION] = "True"
                seen[_RenPKeys.TRANSFORM_ACCELERATION] = True

            elif lexer.match(_RenPLexerKeywords.UPDATE_ACCELERATION):
                if seen[_RenPKeys.UPDATE_ACCELERATION]:
                    lexer.error("only one 'accelerate update' instruction allowed")
                data[_RenPKeys.UPDATE_ACCELERATION] = "True"
                seen[_RenPKeys.UPDATE_ACCELERATION] = True

            elif lexer.match(_RenPLexerKeywords.UPDATE_FIDELITY):
                if seen[_RenPKeys.UPDATE_FIDELITY]:
                    lexer.error("only one 'update fidelity' instruction allowed")
                data[_RenPKeys.UPDATE_FIDELITY] = lexer.integer()
                seen[_RenPKeys.UPDATE_FIDELITY] = True

            elif lexer.match(_RenPLexerKeywords.ACCELERATION_TARGET_FPS):
                if seen[_RenPKeys.ACCELERATION_TARGET_FPS]:
                    lexer.error("only one 'acceleration target fps' instruction allowed")
                data[_RenPKeys.ACCELERATION_TARGET_FPS] = lexer.integer()
                seen[_RenPKeys.ACCELERATION_TARGET_FPS] = True

            elif lexer.match(_RenPLexerKeywords.PARTICLE_EVENT_LISTENING):
                if seen[_RenPKeys.PARTICLE_EVENT_LISTENING]:
                    lexer.error("only one 'particles listening events' instruction allowed")
                data[_RenPKeys.PARTICLE_EVENT_LISTENING] = "True"
                seen[_RenPKeys.PARTICLE_EVENT_LISTENING] = True
            
            else:
                return False
            
            lexer.expect_eol()
        return True

    def _renp_parse_preset_block(lexer, data):
        seen = _renp_create_preset_block_flags()

        while lexer.advance():
            if lexer.match(_RenPLexerKeywords.ON_UPDATE):
                if seen[_RenPKeys.ON_UPDATE]:
                    lexer.error("only one 'on update' block allowed")
                data[_RenPKeys.ON_UPDATE] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_UPDATE] = True

            elif lexer.match(_RenPLexerKeywords.ON_EVENT):
                if seen[_RenPKeys.ON_EVENT]:
                    lexer.error("only one 'on event' block allowed")
                data[_RenPKeys.ON_EVENT] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_EVENT] = True

            elif lexer.match(_RenPLexerKeywords.ON_PARTICLE_DEAD):
                if seen[_RenPKeys.ON_PARTICLE_DEAD]:
                    lexer.error("only one 'on particle dead' block allowed")
                data[_RenPKeys.ON_PARTICLE_DEAD] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_PARTICLE_DEAD] = True

            elif lexer.match(_RenPLexerKeywords.ON_PARTICLE_APPEAR):
                if seen[_RenPKeys.ON_PARTICLE_APPEAR]:
                    lexer.error("only one 'on particle appear' block allowed")
                data[_RenPKeys.ON_PARTICLE_APPEAR] = _renp_parse_on_block(lexer)
                seen[_RenPKeys.ON_PARTICLE_APPEAR] = True
            
            elif lexer.keyword(_RenPLexerKeywords.PRESET):
                lexer.error("recursive presets are not allowed")
            
            else:
                return False
            
            lexer.expect_eol()
        return True

    #----------------------------------------

    def renp_parse_fast_particles_show(lexer):
        data = _renp_create_base_data_dict()

        if lexer.keyword(_RenPLexerKeywords.MODEL):
            data[_RenPKeys.MODEL_NAME] = lexer.string()

            while not lexer.eol():
                if lexer.match(':'):
                    data[_RenPKeys.REDEFINITION] = _renp_parse_redefinition_in_model(lexer.subblock_lexer())
                    lexer.expect_eol()
                    break
                elif lexer.keyword(_RenPLexerKeywords.WITH):
                    if data[_RenPKeys.WITH] != BASE_TRANSITION:
                        lexer.error("there can only be one 'with' statement")
                    data[_RenPKeys.WITH] = lexer.simple_expression()
                data.update(_renp_parse_show_component(lexer))

            return data
        
        _renp_parse_show_components(lexer, data)
        
        if lexer.eol():
            lexer.error("subblock required")

        lexer.expect_eol()
        subblock = lexer.subblock_lexer()
        _renp_parse_system_subblock(subblock, data)

        return data

    def _renp_parse_system_subblock(subblock, data):
        if data[_RenPKeys.MULTIPLE]:
            while subblock.advance():
                if subblock.keyword(_RenPLexerKeywords.REDRAW):
                    data[_RenPKeys.REDRAW] = _renp_parse_redraw(subblock)
                elif subblock.keyword(_RenPLexerKeywords.SYSTEM):
                    system_id = None
                    if subblock.keyword(_RenPLexerKeywords.SUBSYSTEM_ID):
                        system_id = subblock.string()

                    subblock.require(':')
                    subblock.expect_eol()
                    sub_data = _renp_create_system_data(_RenParserType.SubSystem)
                    sub_data[_RenPKeys.SYSTEM_ID] = system_id
                    _renp_parse_system_content(subblock.subblock_lexer(), sub_data)
                    data[_RenPKeys.SUBSYSTEMS].append(sub_data)
                else:
                    subblock.error("Multiple rparticles can only contain 'system:' blocks or 'redraw' instruction. Got: " + subblock.rest())
                subblock.expect_eol()
        else:
            system_data = _renp_create_system_data(_RenParserType.System)
            if not _renp_parse_system_content(subblock, system_data):
                subblock.error("Unknown instruction in rparticles: " + subblock.rest())
            
            data.update(system_data)

        return data

    def _renp_parse_redefinition_in_model(lexer):
        data = {}
        seen = set()
        was_at_least_one_block = False

        while lexer.advance():
            behavior_id = lexer.require(lexer.string, "behavior ID is required as a string")
            if behavior_id in seen:
                lexer.error("duplicate behavior ID found: {}".format(behavior_id))

            lexer.require(':')
            data[behavior_id] = _renp_parse_properties(lexer)

            seen.add(behavior_id)
            was_at_least_one_block = True

        if not was_at_least_one_block:
            lexer.error("at least one behavior handler must be redefined or don't open redefinition block")

        return data

    def renp_parse_fast_particles_define(lexer):
        data = _renp_create_define_particles_data()

        if lexer.keyword(_RenPLexerKeywords.MULTIPLE):
            data[_RenPKeys.MULTIPLE] = True

        data[_RenPKeys.MODEL_NAME] = lexer.string()

        if not lexer.match(':'):
            lexer.error("subblock required")

        lexer.expect_eol()
        subblock = lexer.subblock_lexer()
        _renp_parse_system_subblock(subblock, data)

        return data

    def renp_parse_fast_particles_define_preset(lexer):
        data = _renp_create_preset_define_data()

        data[_RenPKeys.PRESET_NAME] = lexer.word()

        if lexer.keyword(_RenPLexerKeywords.PRESET_TYPE):
            data[_RenPKeys.PRESET_TYPE] = lexer.word()
        
        lexer.require(':')
        lexer.expect_eol()
        _renp_parse_preset_block(lexer.subblock_lexer(), data[_RenPKeys.PRESET_DEFINE_DATA])

        return data

    def renp_parse_fast_particles_reset(lexer):
        data = _renp_create_reset_data()

        if not lexer.eol():
            data[_RenPKeys.TAG] = lexer.string()

        lexer.expect_eol()
        return data

    def renp_parse_fast_particles_freeze(lexer):
        data = _renp_create_freeze_data()

        if not lexer.eol():
            data[_RenPKeys.TAG] = lexer.string()
            if lexer.match('.'):
                data[_RenPKeys.SYSTEM_ID] = lexer.string()

        lexer.expect_eol()
        return data

    def renp_parse_fast_particles_unfreeze(lexer):
        data = _renp_create_unfreeze_data()

        if lexer.eol():
            return data

        checkpoint = lexer.checkpoint()
        if lexer.keyword(_RenPLexerKeywords.NOREDRAW):
            data[_RenPKeys.REDRAW] = False
            lexer.expect_eol()
            return data
        lexer.revert(checkpoint)

        data[_RenPKeys.TAG] = lexer.string()
        if lexer.match('.'):
            data[_RenPKeys.SYSTEM_ID] = lexer.string()
        
        if lexer.keyword(_RenPLexerKeywords.NOREDRAW):
            data[_RenPKeys.REDRAW] = False

        lexer.expect_eol()
        return data

    def renp_parse_fast_particles_clear_cache(lexer):
        data = _renp_create_clear_cache_data()
        data[_RenPLexerKeywords.DEEP] = lexer.keyword(_RenPLexerKeywords.DEEP) is not None
        lexer.expect_eol()
        return data
    
    def renp_parse_fast_particles_continue(lexer):
        data = _renp_create_continue_data()

        if lexer.eol():
            return data

        checkpoint = lexer.checkpoint()
        
        # Проверяем, начинается ли с ключевого слова компонента показа
        if _renp_is_show_component_keyword(lexer):
            data.update(_renp_parse_show_component(lexer))
            while not lexer.eol():
                if _renp_is_show_component_keyword(lexer):
                    data.update(_renp_parse_show_component(lexer))
                else:
                    lexer.error("unknown show component: {}".format(lexer.rest()))
            return data
            
        lexer.revert(checkpoint)

        data[_RenPKeys.TAG] = lexer.string()

        while not lexer.eol():
            if lexer.keyword(_RenPLexerKeywords.ONLAYER):
                data[_RenPKeys.LAYER] = lexer.simple_expression()
            elif lexer.keyword(_RenPLexerKeywords.ZORDER):
                data[_RenPKeys.ZORDER] = lexer.require(lexer.integer, "integer expected")
            elif lexer.keyword(_RenPLexerKeywords.WITH):
                if data[_RenPKeys.WITH] != BASE_TRANSITION:
                    lexer.error("there can only be one 'with' statement")
                data[_RenPKeys.WITH] = lexer.simple_expression()
            else:
                lexer.error("unknown show component: {}".format(lexer.rest()))

        lexer.expect_eol()
        return data

    def renp_parse_fast_particles_simulate(lexer):
        data = _renp_create_simulate_data()

        data[_RenPKeys.TAG] = lexer.string()
        data[_RenPKeys.SIMULATE_TIME] = lexer.simple_expression()
        
        if lexer.match(_RenPKeys.SIMULATE_WAIT):
            data[_RenPKeys.SIMULATE_WAIT] = True

        if not lexer.eol():
            data[_RenPKeys.SIMULATE_WAIT_STEP] = lexer.simple_expression()

        lexer.expect_eol()
        return data

    #-------------------PARSERS---------------------

    #---------------EXECUTE------------------

    def renp_execute_fast_particles_show(data):
        is_model = _RenPKeys.MODEL_NAME in data and data[_RenPKeys.MODEL_NAME] is not None
        
        if is_model:
            model_name = data[_RenPKeys.MODEL_NAME]
            model_data = renparticles._fast_particles_models.get(model_name, None)
            
            if model_data is None:
                renpy.error("the rparticles model named '{}' does not exist\n"
                            "Available models: {}".format(model_name, list(renparticles._fast_particles_models.keys())))
                return
            
            data = data.copy()
            data.update(model_data)

        tag = data.get(_RenPKeys.TAG, None)
        layer = data[_RenPKeys.LAYER]
        zorder = eval(data[_RenPKeys.ZORDER])
        redraw = eval(data[_RenPKeys.REDRAW])

        if data[_RenPKeys.MULTIPLE]:
            subsystems = [_renp_eval_system(system) for system in data[_RenPKeys.SUBSYSTEMS]]
            displayable = renparticles.RenParticleFastGroup(subsystems, redraw, layer)
        else:
            displayable = _renp_eval_system(data)

        if is_model and _RenPKeys.REDEFINITION in data and data[_RenPKeys.REDEFINITION]:
            _renp_try_redefine_properties_in_handlers(displayable, data[_RenPKeys.REDEFINITION])
        
        true_tag = tag or _RenPKeys.BASE_NAME
        renparticles._fast_particles_entries[true_tag] = displayable

        renpy.show(name=_RenPKeys.BASE_NAME, tag=tag, what=displayable, layer=layer, zorder=zorder)

        with_statement = eval(data[_RenPKeys.WITH])
        if with_statement:
            renpy.with_statement(with_statement)

    def renp_parse_fast_particles_define_execute_init(data):
        model_name = data[_RenPKeys.MODEL_NAME]

        if model_name in renparticles._fast_particles_models:
            renpy.error("rparticles model named '{}' already declared. Name your system differently".format(model_name))

        renparticles._fast_particles_models[model_name] = data.copy()

    def renp_execute_fast_particles_define_preset(data):
        preset_prefab = renparticles._RFDynamicBehaviorPreset()
        preset_data = data[_RenPKeys.PRESET_DEFINE_DATA]
        
        preset_prefab.behaviors[_RenPKeys.ON_UPDATE] = preset_data.get(_RenPKeys.ON_UPDATE, {})
        preset_prefab.behaviors[_RenPKeys.ON_EVENT] = preset_data.get(_RenPKeys.ON_EVENT, {})
        preset_prefab.behaviors[_RenPKeys.ON_PARTICLE_DEAD] = preset_data.get(_RenPKeys.ON_PARTICLE_DEAD, {})
        preset_prefab.behaviors[_RenPKeys.ON_PARTICLE_APPEAR] = preset_data.get(_RenPKeys.ON_PARTICLE_APPEAR, {})

        renparticles.add_preset(data[_RenPKeys.PRESET_NAME], preset_prefab, data[_RenPKeys.PRESET_TYPE])

    def renp_execute_fast_particles_reset(data):
        tag = data[_RenPKeys.TAG] or _RenPKeys.BASE_NAME
        system = renparticles._fast_particles_entries.get(tag, None)
        if system is not None:
            system.reset()

    def renp_execute_fast_particles_freeze(data):
        tag = data[_RenPKeys.TAG] or _RenPKeys.BASE_NAME
        system_id = data.get(_RenPKeys.SYSTEM_ID)
        
        system = renparticles._fast_particles_entries.get(tag, None)
        if not system:
            return
        
        if system_id:
            if isinstance(system, renparticles.RenParticleFastGroup):
                system.freeze_one(system_id)
            return
        
        system.freeze()

    def renp_execute_fast_particles_unfreeze(data):
        tag = data[_RenPKeys.TAG] or _RenPKeys.BASE_NAME
        system_id = data.get(_RenPKeys.SYSTEM_ID)
        redraw = data[_RenPKeys.REDRAW]
        
        system = renparticles._fast_particles_entries.get(tag, None)
        if not system:
            return
        
        if system_id:
            if isinstance(system, renparticles.RenParticleFastGroup):
                system.unfreeze_one(system_id, redraw)
            return
            
        system.unfreeze(redraw)

    def renp_execute_fast_particles_clear_cache(data):
        deep = data.get(_RenPLexerKeywords.DEEP, False)
        
        if deep:
            for tag, system in list(renparticles._fast_particles_entries.items()):
                renpy.hide(tag, layer=system.layer)
            renparticles._fast_particles_entries.clear()
        else:
            for tag, system in list(renparticles._fast_particles_entries.items()):
                if not renpy.showing(tag, layer=system.layer):
                    renpy.hide(tag, layer=system.layer)
                    renparticles._fast_particles_entries.pop(tag, None)

    def renp_execute_fast_particles_continue(data):
        tag = data[_RenPKeys.TAG] or _RenPKeys.BASE_NAME
        system = renparticles._fast_particles_entries.get(tag, None)
        
        if system is not None:
            layer = data[_RenPKeys.LAYER] or system.layer
            system.layer = layer
            zorder = eval(data[_RenPKeys.ZORDER])
            renpy.show(_RenPKeys.BASE_NAME, what=system, layer=layer, tag=tag, zorder=zorder)
            
            with_statement = eval(data[_RenPKeys.WITH])
            if with_statement:
                renpy.with_statement(with_statement)

    def renp_execute_fast_particles_simulate(data):
        tag = data[_RenPKeys.TAG] or _RenPKeys.BASE_NAME
        simulate_time = eval(data[_RenPKeys.SIMULATE_TIME])
        simulate_wait_step = eval(data[_RenPKeys.SIMULATE_WAIT_STEP]) if data[_RenPKeys.SIMULATE_WAIT_STEP] != "None" else None

        if not isinstance(simulate_time, (int, float)):
            renpy.error("[[RENPARTICLES]: rparticles simulate error: 'simulate time' statement is not int or float\nGot: Type <{}> Value <{}>".format(type(simulate_time), simulate_time))
        if simulate_time < 0:
            renpy.error("[[RENPARTICLES]: rparticles simulate error: 'simulate time' cannot be negative")

        if simulate_wait_step is not None:
            if not isinstance(simulate_wait_step, (int, float)):
                renpy.error("[[RENPARTICLES]: rparticles simulate error: 'simulate wait step' statement is not int or float\nGot: Type <{}> Value <{}>".format(type(simulate_wait_step), simulate_wait_step))
            elif simulate_wait_step < 0:
                renpy.error("[[RENPARTICLES]: rparticles simulate error: 'simulate wait step' cannot be negative")

        system = renparticles._fast_particles_entries.get(tag, None)
        if system is not None:
            if data[_RenPKeys.SIMULATE_WAIT]:
                system.simulate_time = simulate_time
                renpy.call("_renp_simulate_loop_label", system, simulate_wait_step)
            else:
                system.simulate(simulate_time)

    #---------------EXECUTE------------------

    #--------------EVALUATORS----------------

    def _renp_try_redefine_properties_in_handlers(system, redef_properties):
        evaluated_props = _renp_eval_props(redef_properties)
        
        for behavior_id, properties in evaluated_props.items():
            behavior = system.get_behavior_by_id(behavior_id)
            
            if behavior is None:
                renpy.error("<rparticles>: cannot redefine properties for unknown behavior ID '{}'".format(behavior_id))
            
            behavior.inject_properties(**properties)

    def _renp_eval_system(system):
        on_update = []
        on_event = []
        on_particle_dead = []
        on_particle_appear = []
        images = _renp_eval_images(system[_RenPKeys.IMAGES])

        # Обработка пресетов высокого уровня
        _renp_eval_high_level_presets(
            system[_RenPKeys.PRESETS],
            on_update,
            on_event,
            on_particle_dead,
            on_particle_appear
        )

        # Обработка блоков
        on_update.extend(_renp_eval_on_block(system[_RenPKeys.ON_UPDATE]))
        on_event.extend(_renp_eval_on_block(system[_RenPKeys.ON_EVENT]))
        on_particle_dead.extend(_renp_eval_on_block(system[_RenPKeys.ON_PARTICLE_DEAD]))
        on_particle_appear.extend(_renp_eval_on_block(system[_RenPKeys.ON_PARTICLE_APPEAR]))

        # Время жизни
        lifetime_type = None
        lifetime_timings = None
        if system[_RenPKeys.LIFETIME]:
            lifetime_type = system[_RenPKeys.LIFETIME][_RenPKeys.TYPE]
            lifetime_timings = eval(system[_RenPKeys.LIFETIME][_RenPKeys.TIMINGS])

        particles_data = renparticles.ParticlesData(
            images=images,
            tag=system.get(_RenPKeys.TAG, None),
            lifetime_type=lifetime_type,
            lifetime_timings=lifetime_timings
        )
        
        system_instance = renparticles.RenParticlesFast(
            on_update,
            on_event,
            on_particle_dead,
            on_particle_appear,
            particles_data,
            eval(system.get(_RenPKeys.CACHE, "False")),
            eval(system.get(_RenPKeys.REDRAW, "None")),
            system.get(_RenPKeys.LAYER, None),
            eval(system.get(_RenPKeys.TRANSFORM_ACCELERATION, "None")),
            eval(system.get(_RenPKeys.PARTICLE_EVENT_LISTENING, "None")),
            _renp_eval_positive_integer(system.get(_RenPKeys.UPDATE_FIDELITY, "None"), _RenPLexerKeywords.UPDATE_FIDELITY),
            eval(system.get(_RenPKeys.UPDATE_ACCELERATION, "None")),
            _renp_eval_positive_integer(system.get(_RenPKeys.ACCELERATION_TARGET_FPS, "None"), _RenPLexerKeywords.ACCELERATION_TARGET_FPS)
        )
        
        system_instance.system_id = system.get(_RenPKeys.SYSTEM_ID, None)
        return system_instance

    def _renp_eval_images(images_data):
        images = []
        for content, is_expr in images_data:
            if is_expr:
                images.append(eval(content))
            else:
                images.append(content)
        return images

    def _renp_eval_on_block(on_block_data):
        on_block = []
        for content in on_block_data:
            behavior = None
            
            if content[_RenPKeys.TYPE] in (_RenParserType.Func, _RenParserType.Emitter):
                behavior = eval(content[_RenPKeys.FUNC])

            elif content[_RenPKeys.TYPE] == _RenParserType.Shortcut:
                shortcuts_block = content[_RenPKeys.SHORTCUTS_BLOCK]
                shortcut = content[_RenPKeys.SHORTCUT]
                behavior = _renp_try_get_shortcut_behavior(shortcuts_block, shortcut)

            elif content[_RenPKeys.TYPE] == _RenParserType.InnerPreset:
                behavior = _renp_try_get_preset_behavior(_RenPKeys.INNER_SHORTCUTS, content[_RenPKeys.SHORTCUT])
                if isinstance(behavior, renparticles._RFDynamicBehaviorPreset):
                    if not behavior.is_one_block():
                        _renp_inner_preset_multiple_blocks_error(behavior)
                    on_block.extend(_renp_eval_on_block(behavior.get_one()))
                    continue

            behavior = behavior()
            props = _renp_eval_props(content[_RenPKeys.PROPERTIES])

            if content[_RenPKeys.TYPE] not in _RenParserType.PresetsTypes:
                behavior.inject_properties(**props)
                behavior.check_initialised()
                on_block.append((behavior, behavior.m_properties))
            else:
                if not behavior.is_one_block():
                    _renp_inner_preset_multiple_blocks_error(behavior)
                behavior.build()
                on_block.extend(behavior.get_one())

        return on_block

    def _renp_eval_high_level_presets(presets, on_update, on_event, on_particle_dead, on_particle_appear):
        for preset in presets:
            preset_behavior = _renp_try_get_preset_behavior(
                _RenPKeys.GENERAL_SHORTCUTS,
                preset[_RenPKeys.SHORTCUT]
            )

            if isinstance(preset_behavior, renparticles._RFDynamicBehaviorPreset):
                on_update.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeys.ON_UPDATE]))
                on_event.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeys.ON_EVENT]))
                on_particle_dead.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeys.ON_PARTICLE_DEAD]))
                on_particle_appear.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeys.ON_PARTICLE_APPEAR]))
            else:
                preset_behavior = preset_behavior()
                props = _renp_eval_props(preset[_RenPKeys.PROPERTIES])
                preset_behavior.inject_properties(**props)
                behaviors = preset_behavior.build()
                on_update.extend([(behavior, _renp_safe_merge_preset_props(preset, behavior)) for behavior in behaviors[_RenPKeys.ON_UPDATE]])
                on_event.extend([(behavior, _renp_safe_merge_preset_props(preset, behavior)) for behavior in behaviors[_RenPKeys.ON_EVENT]])
                on_particle_dead.extend([(behavior, _renp_safe_merge_preset_props(preset, behavior)) for behavior in behaviors[_RenPKeys.ON_PARTICLE_DEAD]])
                on_particle_appear.extend([(behavior, _renp_safe_merge_preset_props(preset, behavior)) for behavior in behaviors[_RenPKeys.ON_PARTICLE_APPEAR]])

    def _renp_eval_props(props_raw):
        if isinstance(props_raw, dict):
            evaluated_collection = { }
            for key, value in props_raw.items():
                if key == _RenPKeys.CONDITION:
                    evaluated_collection[key] = value
                else:
                    evaluated_collection[key] = _renp_eval_props(value)
            return evaluated_collection
        elif isinstance(props_raw, (list, tuple)):
            return type(props_raw)(_renp_eval_props(item) for item in props_raw)
        elif isinstance(props_raw, basestring) and props_raw not in RENPY_RESERVED_WORDS:
            try:
                return eval(props_raw)
            except:
                return props_raw
        else:
            return props_raw

    def _renp_eval_positive_integer(raw_data, instruction_name="NULL"):
        if raw_data == "None":
            return None

        try:
            eval_data = eval(raw_data)
        except Exception as e:
            renpy.error("incorrect value for '{}': '{}'. Parsing error: {}".format(instruction_name, raw_data, str(e)))
            return None

        if not isinstance(eval_data, (int, float)):
            renpy.error("{} must be a number, received: {}".format(instruction_name, type(eval_data).__name__))
            return None

        if eval_data <= 0:
            renpy.error("{} must be a positive number greater than 0. Received: {}".format(instruction_name, eval_data))
            return None

        return eval_data

    def _renp_try_get_shortcut_behavior(shortcut_block, shortcut):
        shortcut_behavior = renparticles.static_shortcuts[shortcut_block].get(shortcut, None)
        
        if shortcut_behavior is None:
            shortcut_behavior = renparticles.dynamic_shortcuts[shortcut_block].get(shortcut, None)
        
        if shortcut_behavior is None:
            _renp_shortcut_error(shortcut_block, shortcut)
        
        return shortcut_behavior

    def _renp_try_get_preset_behavior(preset_block, shortcut):
        preset_behavior = renparticles.static_shortcuts[_RenPKeys.PRESETS][preset_block].get(shortcut, None)
        
        if preset_behavior is None:
            preset_behavior = renparticles.dynamic_shortcuts[_RenPKeys.PRESETS][preset_block].get(shortcut, None)
            
        if preset_behavior is None:
            _renp_preset_error(preset_block, shortcut)
        
        return preset_behavior

    #--------------EVALUATORS----------------

    #-----------------MISC-------------------

    def _renp_safe_merge_preset_props(preset, behavior):
        misc = {}

        preset_condition = preset.get(_RenPKeys.PROPERTIES, {}).get(_RenPKeys.CONDITION, None)
        if preset_condition is not None:
            misc[_RenPKeys.CONDITION] = preset_condition
        
        behavior_props = behavior.m_properties or {}
        if not isinstance(behavior_props, dict):
            behavior_props = {}
        
        final_dict = misc
        final_dict.update(behavior_props)
        return final_dict

    #-----------------MISC-------------------

    #------------ERROR NOTIFIERS-------------

    def _renp_shortcut_error(shortcuts_block, shortcut):
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available static shortcuts: {}\n"
            "Available dynamic shortcuts: {}".format(
                shortcut,
                shortcuts_block,
                ", ".join(renparticles.static_shortcuts[shortcuts_block].keys()),
                ", ".join(renparticles.dynamic_shortcuts[shortcuts_block].keys())
            )
        )

    def _renp_preset_error(preset_block, shortcut):
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available static preset shortcuts: {}\n"
            "Available dynamic preset shortcuts: {}".format(
                shortcut,
                preset_block,
                ", ".join(renparticles.static_shortcuts[_RenPKeys.PRESETS][preset_block].keys()),
                ", ".join(renparticles.dynamic_shortcuts[_RenPKeys.PRESETS][preset_block].keys())
            )
        )

    def _renp_inner_preset_multiple_blocks_error(preset_behavior):
        renpy.error(
            "Preset '{}' must have exactly one active block. "
            "Current blocks: on_update={}\non_event={}\non_particle_dead={}. "
            "Expected: exactly one block to be active (not None).".format(
                preset_behavior.__class__.__name__,
                preset_behavior.behaviors.get(_RenPKeys.ON_UPDATE),
                preset_behavior.behaviors.get(_RenPKeys.ON_EVENT),
                preset_behavior.behaviors.get(_RenPKeys.ON_PARTICLE_DEAD)
            )
        )

    #------------ERROR NOTIFIERS-------------

    #----------------SCREENS-----------------

    def _renp_instantiate_system_displayable(data, redraw=0.0, layer=None):
        if data[_RenPKeys.MULTIPLE]:
            subsystems = [_renp_eval_system(system) for system in data[_RenPKeys.SUBSYSTEMS]]
            return renparticles.RenParticleFastGroup(subsystems, redraw, layer)
        return _renp_eval_system(data)

    def _renp_sl_displayable_early_wrapper(tag, **properties):
        return renparticles.instantiate_model(tag)

    renpy.register_sl_displayable("rparticles", _renp_sl_displayable_early_wrapper, "default", 0) \
        .add_positional("child")

    #----------------SCREENS-----------------

    #------------------CDS-------------------

    renpy.register_statement(
        "rparticles",
        renp_parse_fast_particles_show,
        None,
        renp_execute_fast_particles_show,
        block=_RenPKeys.POSSIBLE
    )

    renpy.register_statement(
        "rparticles define",
        renp_parse_fast_particles_define,
        None,
        execute_init=renp_parse_fast_particles_define_execute_init,
        block=_RenPKeys.POSSIBLE
    )

    renpy.register_statement(
        "rparticles define preset",
        renp_parse_fast_particles_define_preset,
        None,
        execute_init=renp_execute_fast_particles_define_preset,
        block=_RenPKeys.POSSIBLE
    )

    renpy.register_statement(
        "rparticles reset",
        renp_parse_fast_particles_reset,
        None,
        renp_execute_fast_particles_reset
    )

    renpy.register_statement(
        "rparticles freeze",
        renp_parse_fast_particles_freeze,
        None,
        renp_execute_fast_particles_freeze
    )

    renpy.register_statement(
        "rparticles unfreeze",
        renp_parse_fast_particles_unfreeze,
        None,
        renp_execute_fast_particles_unfreeze
    )

    renpy.register_statement(
        "rparticles clear cache",
        renp_parse_fast_particles_clear_cache,
        None,
        renp_execute_fast_particles_clear_cache
    )

    renpy.register_statement(
        "rparticles continue",
        renp_parse_fast_particles_continue,
        None,
        renp_execute_fast_particles_continue
    )

    renpy.register_statement(
        "rparticles simulate",
        renp_parse_fast_particles_simulate,
        None,
        renp_execute_fast_particles_simulate
    )

    #------------------CDS-------------------
